from .logger import Logger
from .moduler import Moduler
from .biller import Biller

import logging
import sys


class Realtime:
    def __init__(self, logPath: str = "/var/log"):
        self.amqb_initiated = False
        self.telnet_initiated = False
        self.mongodb_initiated = False
        self.logger_initiated = False
        self.moduler_initiated = False
        self.biller_initiated = False

        self.logPath = logPath
        self.logFormatter = logging.Formatter(
            "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        self.rootLogger = logging.getLogger()
        self.rootLogger.setLevel(logging.DEBUG)

        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(logging.INFO)
        consoleHandler.setFormatter(self.logFormatter)
        self.rootLogger.addHandler(consoleHandler)


    def initiate_amqb(self, host: str = "127.0.0.1", port: int = 5672):
        self.AMQP_BROKER_HOST = host
        self.AMQP_BROKER_PORT = port
        self.amqb_initiated = True

    def initiate_telnet(self, host: str = "127.0.0.1", port: int = 8990, timeout: int = 10, auth: bool = True, username: str = "jcliadmin", password: str = "jclipwd", standard_prompt: str = "jcli : ", interactive_prompt: str = "> "):
        self.TELNET_HOST = host
        self.TELNET_PORT = port
        self.TELNET_TIMEOUT = timeout
        self.TELNET_AUTH = auth
        self.TELNET_USERNAME = username
        self.TELNET_PASSWORD = password
        self.TELNET_STANDARD_PROMPT = standard_prompt
        self.TELNET_INTERACTIVE_PROMPT = interactive_prompt
        self.telnet_initiated = True

    def initiate_mongodb(self, connection_string: str):
        self.MONGODB_CONNECTION_STRING = connection_string
        self.mongodb_initiated = True

    def initiate_logger(self, database: str, collection: str):
        self.MONGODB_LOGS_DATABASE = database
        self.MONGODB_LOGS_COLLECTION = collection
        self.logger_initiated = True

    def initiate_moduler(self, database: str):
        self.MONGODB_MODULES_DATABASE = database
        self.moduler_initiated = True

    def initiate_biller(self, database: str, collection: str, balance_key: str):
        self.MONGODB_BILL_DATABASE = database
        self.MONGODB_BILL_COLLECTION = collection
        self.MONGODB_BILL_BALANCE_KEY = balance_key
        self.biller_initiated = True

    def startModuler(self):
        moduler_ready = self.telnet_initiated and self.mongodb_initiated and self.moduler_initiated

        fileHandler = logging.FileHandler(
            f"{self.logPath}/jasmin_realtime.moduler.log")
        fileHandler.setLevel(logging.DEBUG)
        fileHandler.setFormatter(self.logFormatter)
        self.rootLogger.addHandler(fileHandler)

        logging.info("*********************************************")
        logging.info("::Jasmin Realtime Moduler::")
        logging.info("Starting up")
        logging.info("")
        if not moduler_ready:
            logging.info(
                "Sorry, Could not find correct ENVIRONMENT variables!")

            logging.info("Please export the fallowing:                  \n\
                JASMIN_CLI_HOST                 =       **NoDefault**   \n\
                JASMIN_CLI_PORT                 =           8990        \n\
                JASMIN_CLI_TIMEOUT              =           30          \n\
                JASMIN_CLI_AUTH                 =           True        \n\
                JASMIN_CLI_USERNAME             =         jcliadmin     \n\
                JASMIN_CLI_PASSWORD             =         jclipwd       \n\
                JASMIN_CLI_STANDARD_PROMPT      =         \"jcli : \"   \n\
                JASMIN_CLI_INTERACTIVE_PROMPT   =           \"> \"      \n\
                MONGODB_CONNECTION_STRING       =       **NoDefault**   \n\
                MONGODB_MODULES_DATABASE        =       **NoDefault**   ")

            logging.info("Shutting Down!!")
            logging.info("*********************************************")
            return

        logging.info("initiated!")

        Moduler(
            connection_string=self.MONGODB_CONNECTION_STRING,
            modules_database=self.MONGODB_MODULES_DATABASE,
            host=self.TELNET_HOST,
            port=self.TELNET_PORT,
            timeout=self.TELNET_TIMEOUT,
            auth=self.TELNET_AUTH,
            username=self.TELNET_USERNAME,
            password=self.TELNET_PASSWORD,
            standard_prompt=self.TELNET_STANDARD_PROMPT,
            interactive_prompt=self.TELNET_INTERACTIVE_PROMPT
        )

    def startBiller(self):
        biller_ready = self.amqb_initiated and self.mongodb_initiated and self.biller_initiated

        fileHandler = logging.FileHandler(
            f"{self.logPath}/jasmin_realtime.biller.log")
        fileHandler.setLevel(logging.DEBUG)
        fileHandler.setFormatter(self.logFormatter)
        self.rootLogger.addHandler(fileHandler)

        logging.info("*********************************************")
        logging.info("::Jasmin Realtime Biller::")
        logging.info("Starting up")
        logging.info("")
        if not biller_ready:
            logging.info(
                "Sorry, Could not find correct ENVIRONMENT variables!")

            logging.info("Please export the fallowing:                  \n\
                AMQP_BROKER_HOST                =       **NoDefault**   \n\
                AMQP_BROKER_PORT                =           5672        \n\
                MONGODB_CONNECTION_STRING       =       **NoDefault**   \n\
                MONGODB_BILL_DATABASE           =       **NoDefault**   \n\
                MONGODB_BILL_COLLECTION         =       **NoDefault**   \n\
                MONGODB_BILL_BALANCE_KEY        =       **NoDefault**   ")

            logging.info("Shutting Down!!")
            logging.info("*********************************************")
            return

        logging.info("initiated!")

        Biller(
            amqp_host=self.AMQP_BROKER_HOST,
            amqp_port=self.AMQP_BROKER_PORT,
            connection_string=self.MONGODB_CONNECTION_STRING,
            bill_database=self.MONGODB_BILL_DATABASE,
            bill_collection=self.MONGODB_BILL_COLLECTION,
            bill_balance_key=self.MONGODB_BILL_BALANCE_KEY
        )

    def startLogger(self):
        logger_ready = self.amqb_initiated and self.mongodb_initiated and self.logger_initiated

        fileHandler = logging.FileHandler(
            f"{self.logPath}/jasmin_realtime.logger.log")
        fileHandler.setLevel(logging.DEBUG)
        fileHandler.setFormatter(self.logFormatter)
        self.rootLogger.addHandler(fileHandler)

        logging.info("*********************************************")
        logging.info("::Jasmin Realtime Logger::")
        logging.info("Starting up")
        logging.info("")
        if not logger_ready:
            logging.info(
                "Sorry, Could not find correct ENVIRONMENT variables!")

            logging.info("Please export the fallowing:                  \n\
                AMQP_BROKER_HOST                =       **NoDefault**   \n\
                AMQP_BROKER_PORT                =           5672        \n\
                MONGODB_CONNECTION_STRING       =       **NoDefault**   \n\
                MONGODB_LOGS_DATABASE           =       **NoDefault**   \n\
                MONGODB_LOGS_COLLECTION         =       **NoDefault**   ")

            logging.info("Shutting Down!!")
            logging.info("*********************************************")
            return

        logging.info("initiated!")

        Logger(
            amqp_host=self.AMQP_BROKER_HOST,
            amqp_port=self.AMQP_BROKER_PORT,
            connection_string=self.MONGODB_CONNECTION_STRING,
            log_database=self.MONGODB_LOGS_DATABASE,
            log_collection=self.MONGODB_LOGS_COLLECTION
        )
