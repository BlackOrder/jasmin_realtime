import sys, os
from .realtime import *

def start():

    if not len(sys.argv) == 2:
        print(f"Wrong number of arguments, expected 1, found {len(sys.argv) - 1}")
        exit()

    if sys.argv[1] not in [ "--moduler", "--biller", "--logger" ]:
        print(f"Unknown argument: {sys.argv[1]}. Expected: --moduler, --biller, or --logger")
        exit()


    realtime = Realtime(logPath=os.getenv("JASMIN_REALTIME_LOG_PATH", "/var/log"))

    if os.getenv("AMQP_BROKER_HOST") is not None:
        realtime.initiate_amqb(host=os.getenv(
            'AMQP_BROKER_HOST'), port=int(os.getenv('AMQP_BROKER_PORT', '5672')))

    if os.getenv("JASMIN_CLI_HOST") is not None:
        realtime.initiate_telnet(host=os.getenv("JASMIN_CLI_HOST"), port=int(os.getenv("JASMIN_CLI_PORT", "8990")), timeout=int(os.getenv("JASMIN_CLI_TIMEOUT", "30")), auth=bool(os.getenv("JASMIN_CLI_AUTH", True)), username=os.getenv(
            "JASMIN_CLI_USERNAME", "jcliadmin"), password=os.getenv("JASMIN_CLI_PASSWORD", "jclipwd"), standard_prompt=os.getenv("JASMIN_CLI_STANDARD_PROMPT", "jcli : "), interactive_prompt=os.getenv("JASMIN_CLI_INTERACTIVE_PROMPT", "> "))

    if os.getenv("MONGODB_CONNECTION_STRING") is not None:
        realtime.initiate_mongodb(
            connection_string=os.getenv("MONGODB_CONNECTION_STRING"))

    if os.getenv("MONGODB_MODULES_DATABASE") is not None:
        realtime.initiate_moduler(
            database=os.getenv("MONGODB_MODULES_DATABASE"))

    if os.getenv("MONGODB_BILL_DATABASE") is not None and os.getenv("MONGODB_BILL_COLLECTION") is not None and os.getenv("MONGODB_BILL_BALANCE_KEY") is not None:
        realtime.initiate_biller(
            database=os.getenv("MONGODB_BILL_DATABASE"), collection=os.getenv("MONGODB_BILL_COLLECTION"), balance_key=os.getenv("MONGODB_BILL_BALANCE_KEY"))

    if os.getenv("MONGODB_LOGS_DATABASE") is not None and os.getenv("MONGODB_LOGS_COLLECTION") is not None:
        realtime.initiate_logger(
            database=os.getenv("MONGODB_LOGS_DATABASE"), collection=os.getenv("MONGODB_LOGS_COLLECTION"))


    if sys.argv[1] == "--moduler":
        realtime.startModuler()
    elif sys.argv[1] == "--biller":
        realtime.startBiller()
    elif sys.argv[1] == "--logger":
        realtime.startLogger()

