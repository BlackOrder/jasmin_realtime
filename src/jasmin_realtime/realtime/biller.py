from time import sleep
from twisted.internet.defer import inlineCallbacks
from twisted.internet import reactor
from twisted.internet.protocol import ClientCreator
from twisted.python import log

from txamqp.protocol import AMQClient
from txamqp.client import TwistedDelegate

import txamqp.spec
import pkg_resources

from .sources import MongoDB
import logging


class Biller:
    def __init__(self, amqp_host: str, amqp_port: int, connection_string: str, bill_database: str, bill_collection: str, bill_balance_key: str):
        self.AMQP_BROKER_HOST = amqp_host
        self.AMQP_BROKER_PORT = amqp_port
        self.MONGODB_CONNECTION_STRING = connection_string
        self.MONGODB_BILL_DATABASE = bill_database
        self.MONGODB_BILL_COLLECTION = bill_collection
        self.MONGODB_BILL_BALANCE_KEY = bill_balance_key
        self.queue = {}
        logging.info("Starting ::Biller Socket::")

        self.rabbitMQConnect()

    @inlineCallbacks
    def gotConnection(self, conn, username, password):
        logging.info(f"Connected to broker, authenticating: {username}")

        yield conn.authenticate(username, password)

        logging.info("Authenticated. Ready to receive messages")
        logging.info(" ")

        chan = yield conn.channel(1)
        yield chan.channel_open()

        yield chan.queue_declare(queue="billingQueue")

        # Bind to routes
        yield chan.queue_bind(queue="billingQueue", exchange="billing", routing_key='bill_request.submit_sm_resp.*')
        yield chan.basic_consume(queue='billingQueue', no_ack=True, consumer_tag="billingFollower")
        queue = yield conn.queue("billingFollower")

        mongosource = MongoDB(connection_string=self.MONGODB_CONNECTION_STRING,
                              database_name=self.MONGODB_BILL_DATABASE)

        if mongosource.startConnection() is not True:
            return

        # Wait for messages
        # This can be done through a callback ...
        while True:
            msg = yield queue.get()
            bill = msg.content.properties['headers']
            mongosource.increment_one(
                module=self.MONGODB_BILL_COLLECTION,
                sub_id=bill['user-id'],
                data={
                    self.MONGODB_BILL_BALANCE_KEY: bill['amount']
                }
            )

        # A clean way to tear down and stop
        yield chan.basic_cancel("billingFollower")
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
