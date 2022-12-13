# Jasmin Realtime

## Install
Tested with python 3.11 only.
#### PIP:
```
pip3 install -U jasmin-realtime
```

## The default log path is `/var/log`. To change it, export:
```
JASMIN_REALTIME_LOG_PATH=/var/log
```

## Realtime Moduler:
To start the Realtime Moduler. you have to export the fallowing variables.

#### export:
```
JASMIN_CLI_HOST                 =       **NoDefault**
JASMIN_CLI_PORT                 =           8990
JASMIN_CLI_TIMEOUT              =            30
JASMIN_CLI_AUTH                 =           True
JASMIN_CLI_USERNAME             =        jcliadmin
JASMIN_CLI_PASSWORD             =         jclipwd
JASMIN_CLI_STANDARD_PROMPT      =        "jcli : "
JASMIN_CLI_INTERACTIVE_PROMPT   =           "> "
MONGODB_CONNECTION_STRING       =       **NoDefault**
MONGODB_MODULES_DATABASE        =       **NoDefault**
```
#### Then run:
```
python3 -m jasmin_realtime --moduler
```


## Realtime Biller:
To start the Realtime Biller. you have to export the fallowing variables.

#### export:
```
AMQP_BROKER_HOST                =       **NoDefault**
AMQP_BROKER_PORT                =           5672
MONGODB_CONNECTION_STRING       =       **NoDefault**
MONGODB_BILL_DATABASE           =       **NoDefault**
MONGODB_BILL_COLLECTION         =       **NoDefault**
MONGODB_BILL_BALANCE_KEY        =       **NoDefault**
```
#### Then run:
```
python3 -m jasmin_realtime --biller
```


## Realtime Logger:
To start the Realtime Logger. you have to export the fallowing variables.

#### export:
```
AMQP_BROKER_HOST                =       **NoDefault**
AMQP_BROKER_PORT                =           5672
MONGODB_CONNECTION_STRING       =       **NoDefault**
MONGODB_LOGS_DATABASE           =       **NoDefault**
MONGODB_LOGS_COLLECTION         =       **NoDefault**
```
#### Then run:
```
python3 -m jasmin_realtime --logger
```
