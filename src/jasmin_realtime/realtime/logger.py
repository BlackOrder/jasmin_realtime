from time import sleep
import pickle as pickle
import binascii
from datetime import datetime
from twisted.internet.defer import inlineCallbacks
from twisted.internet import reactor
from twisted.internet.protocol import ClientCreator
from twisted.python import log
from txamqp.protocol import AMQClient
from txamqp.client import TwistedDelegate
import txamqp.spec

from smpp.pdu.pdu_types import DataCoding
import pkg_resources

from .sources import MongoDB
import logging


class Logger:
    def __init__(self, amqp_host: str, amqp_port: int, connection_string: str, log_database: str, log_collection: str):
        self.AMQP_BROKER_HOST = amqp_host
        self.AMQP_BROKER_PORT = amqp_port
        self.MONGODB_CONNECTION_STRING = connection_string
        self.MONGODB_LOGS_DATABASE = log_database
        self.MONGODB_LOGS_COLLECTION = log_collection
        self.queue = {}
        logging.info("Starting ::Logger Socket::")

        self.rabbitMQConnect()

    @inlineCallbacks
    def gotConnection(self, conn, username, password):
        logging.info(f"Connected to broker, authenticating: {username}")

        yield conn.start({"LOGIN": username, "PASSWORD": password})

        logging.info("Authenticated. Ready to receive messages")
        logging.info(" ")

        chan = yield conn.channel(1)
        yield chan.channel_open()

        yield chan.queue_declare(queue="sms_logger_queue")

        # Bind to submit.sm.* and submit.sm.resp.* routes to track sent messages
        yield chan.queue_bind(queue="sms_logger_queue", exchange="messaging", routing_key='submit.sm.*')
        yield chan.queue_bind(queue="sms_logger_queue", exchange="messaging", routing_key='submit.sm.resp.*')
        # Bind to dlr_thrower.* to track DLRs
        yield chan.queue_bind(queue="sms_logger_queue", exchange="messaging", routing_key='dlr_thrower.*')

        yield chan.basic_consume(queue='sms_logger_queue', no_ack=False, consumer_tag="sms_logger")
        queue = yield conn.queue("sms_logger")

        mongosource = MongoDB(connection_string=self.MONGODB_CONNECTION_STRING,
                              database_name=self.MONGODB_LOGS_DATABASE)

        if mongosource.startConnection() is not True:
            return

        # Wait for messages
        # This can be done through a callback ...
        while True:
            msg = yield queue.get()
            props = msg.content.properties

            if msg.routing_key[:10] == 'submit.sm.' and msg.routing_key[:15] != 'submit.sm.resp.':
                pdu = pickle.loads(msg.content.body)
                pdu_count = 1
                short_message = pdu.params['short_message']
                billing = props['headers']
                billing_pickle = billing.get('submit_sm_resp_bill')
                if not billing_pickle:
                    billing_pickle = billing.get('submit_sm_bill')
                submit_sm_bill = pickle.loads(billing_pickle)
                source_connector = props['headers']['source_connector']
                routed_cid = msg.routing_key[10:]

                # Is it a multipart message ?
                while hasattr(pdu, 'nextPdu'):
                    # Remove UDH from first part
                    if pdu_count == 1:
                        short_message = short_message[6:]

                    pdu = pdu.nextPdu

                    # Update values:
                    pdu_count += 1
                    short_message += pdu.params['short_message'][6:]

                # Save short_message bytes
                binary_message = binascii.hexlify(short_message)

                # If it's a binary message, assume it's utf_16_be encoded
                if pdu.params['data_coding'] is not None:
                    dc = pdu.params['data_coding']
                    if (isinstance(dc, int) and dc == 8) or (isinstance(dc, DataCoding) and str(dc.schemeData) == 'UCS2'):
                        short_message = short_message.decode(
                            'utf_16_be', 'ignore').encode('utf_8')

                self.queue[props['message-id']] = {
                    'source_connector': source_connector,
                    'routed_cid': routed_cid,
                    'rate': submit_sm_bill.getTotalAmounts(),
                    'charge': submit_sm_bill.getTotalAmounts() * pdu_count,
                    'uid': submit_sm_bill.user.uid,
                    'destination_addr': pdu.params['destination_addr'],
                    'source_addr': pdu.params['source_addr'],
                    'pdu_count': pdu_count,
                    'short_message': short_message,
                    'binary_message': binary_message,
                }

                mongosource.update_one(
                    module=self.MONGODB_LOGS_COLLECTION,
                    sub_id=props['message-id'],
                    data={
                        "source_connector": source_connector,
                        "routed_cid": routed_cid,
                        "rate": submit_sm_bill.getTotalAmounts(),
                        "charge": submit_sm_bill.getTotalAmounts() * pdu_count,
                        "uid": submit_sm_bill.user.uid,
                        "destination_addr": pdu.params['destination_addr'],
                        "source_addr": pdu.params['source_addr'],
                        "pdu_count": pdu_count,
                        "short_message": short_message,
                        "binary_message": binary_message
                    }
                )
            elif msg.routing_key[:15] == 'submit.sm.resp.':
                # It's a submit_sm_resp

                pdu = pickle.loads(msg.content.body)
                if props['message-id'] not in self.queue:
                    logging.error(
                        f" Got resp of an unknown submit_sm: {props['message-id']}")
                    chan.basic_ack(delivery_tag=msg.delivery_tag)
                    continue

                qmsg = self.queue[props['message-id']]

                if qmsg['source_addr'] is None:
                    qmsg['source_addr'] = ''

                mongosource.update_one(
                    module=self.MONGODB_LOGS_COLLECTION,
                    sub_id=props['message-id'],
                    data={
                        "source_addr": qmsg['source_addr'],
                        "rate": qmsg['rate'],
                        "pdu_count": qmsg['pdu_count'],
                        "charge": qmsg['charge'],
                        "destination_addr": qmsg['destination_addr'],
                        "short_message": qmsg['short_message'],
                        "status": pdu.status,
                        "uid": qmsg['uid'],
                        "created_at": props['headers']['created_at'],
                        "binary_message": qmsg['binary_message'],
                        "routed_cid": qmsg['routed_cid'],
                        "source_connector": qmsg['source_connector'],
                        "status_at": props['headers']['created_at']
                    }
                )

            elif msg.routing_key[:12] == 'dlr_thrower.':
                if props['headers']['message_status'][:5] == 'ESME_':
                    # Ignore dlr from submit_sm_resp
                    chan.basic_ack(delivery_tag=msg.delivery_tag)
                    continue

                # It's a dlr
                if props['message-id'] not in self.queue:
                    logging.error(
                        f" Got dlr of an unknown submit_sm: {props['message-id']}")
                    chan.basic_ack(delivery_tag=msg.delivery_tag)
                    continue

                # Update message status
                qmsg = self.queue[props['message-id']]

                mongosource.update_one(
                    module=self.MONGODB_LOGS_COLLECTION,
                    sub_id=props['message-id'],
                    data={
                        "status": props['headers']['message_status'],
                        "status_at": datetime.now()
                    }
                )

            else:
                logging.error(f" unknown route: {msg.routing_key}")

            chan.basic_ack(delivery_tag=msg.delivery_tag)

        # A clean way to tear down and stop
        yield chan.basic_cancel("sms_logger")
        yield chan.channel_close()
        chan0 = yield conn.channel(0)
        yield chan0.connection_close()

        reactor.stop()

    def rabbitMQConnect(self) -> bool:
        host = self.AMQP_BROKER_HOST
        port = self.AMQP_BROKER_PORT
        vhost = '/'
        username = 'guest'
        password = 'guest'
        spec_file = pkg_resources.resource_filename(
            'jasmin_realtime', 'amqp0-9-1.xml')

        spec = txamqp.spec.load(spec_file)

        def whoops(err):
            logging.critical("Error in RabbitMQ server: ", err)
            logging.critical("Shutting down !!!")
            if reactor.running:
                log.err(err)
                reactor.stop()
            sleep(3)

        try:
            # Connect and authenticate
            d = ClientCreator(reactor,
                              AMQClient,
                              delegate=TwistedDelegate(),
                              vhost=vhost,
                              spec=spec).connectTCP(host, port)
            d.addCallback(self.gotConnection, username, password)

            d.addErrback(whoops)

            reactor.run()

            return True
        except Exception as err:
            logging.critical("Error connecting to RabbitMQ server: ", err)
            logging.critical("Shutting down !!!")
            return False
