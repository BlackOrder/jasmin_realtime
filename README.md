# Jasmin Realtime

Archived!!! 

Moved to 
[Jasmin-Mongo-Configuration](https://github.com/BlackOrder/jasmin_mongo_configuration)

##### Tested with python 3.11 only.

Links [Jasmin SMS Gateway](https://github.com/jookies/jasmin)'s to MongoDB in realtime.
offers three services:
- Sync configurations [`Smppccm`, `Httpccm`, `Group`, `User`, `Filter`, `MoRouter`, `MtRouter`, `MoInterceptor`, and `MtInterceptor`] from a MongoDB.
- Sync User balance with a specified MongoDB collection's key. Can be used to Sync multiple instances of Jasmin if pared with configurations sync.
- Log all sms to a MongoDB collection.

Each instance of the package can performs only one service. You will have to run each service separately. All settings are read from OS ENV when run from console. if you want to import it in you code, you can supply the settings on initialization.

## Install
#### PYPI:
```
pip3 install -U jasmin-realtime
```
#### From Source:
```
git clone https://github.com/BlackOrder/jasmin_realtime.git
cd jasmin_realtime
pip3 install .
```


## The default log path is `/var/log`. To change it, export:
```
JASMIN_REALTIME_LOG_PATH=/var/log
```

## Realtime Moduler:
Sync all configurations [`Smppccm`, `Httpccm`, `Group`, `User`, `Filter`, `MoRouter`, `MtRouter`, `MoInterceptor`, and `MtInterceptor`] from a MongoDB.
The Database supplied should have a collection for each module:
```
smppccm
group
user
filter
httpccm
morouter
mointerceptor
mtrouter
mtinterceptor
```
Each collection should contains your desired Jasmin's settings in a key value format. and should have a valid format for Jasmin. for example the `user` collection should have documents in this format:
```
{
    _id: '$UID',
    gid: '$GID',
    'mt_messaging_cred authorization dlr_level': 'True',
    'mt_messaging_cred authorization hex_content': 'True',
    'mt_messaging_cred authorization http_balance': 'True',
    'mt_messaging_cred authorization http_bulk': 'True',
    'mt_messaging_cred authorization http_dlr_method': 'True',
    'mt_messaging_cred authorization http_long_content': 'True',
    'mt_messaging_cred authorization http_rate': 'True',
    'mt_messaging_cred authorization http_send': 'True',
    'mt_messaging_cred authorization priority': 'True',
    'mt_messaging_cred authorization schedule_delivery_time': 'True',
    'mt_messaging_cred authorization smpps_send': 'True',
    'mt_messaging_cred authorization src_addr': 'True',
    'mt_messaging_cred authorization validity_period': 'True',
    'mt_messaging_cred defaultvalue src_addr': 'None',
    'mt_messaging_cred quota balance': 4000,
    'mt_messaging_cred quota early_percent': 'ND',
    'mt_messaging_cred quota http_throughput': 'ND',
    'mt_messaging_cred quota smpps_throughput': 'ND',
    'mt_messaging_cred quota sms_count': 'ND',
    'mt_messaging_cred valuefilter content': '.*',
    'mt_messaging_cred valuefilter dst_addr': '.*',
    'mt_messaging_cred valuefilter priority': '^[0-3]$',
    'mt_messaging_cred valuefilter src_addr': '^()$',
    'mt_messaging_cred valuefilter validity_period': '^d+$',
    password: '$PASSWORD',
    'smpps_cred authorization bind': 'True',
    'smpps_cred quota max_bindings': '1',
    status: true,
    uid: '$UID',
    username: '$USERNAME'
}
```
Keep in mind, the `mt_messaging_cred quota balance` key should be `float` or `int`.
Also notice there is an extra key `status`. This key is a special `bool` field. You have to include it in all `user`, `group`, and `smppccm` documents. The Realtime Moduler will use the value of this key to `Enable` if `True`, `Disable` if `False` the `user`, and `group`. In case of `smppccm` the Moduler will `start` the `smppccm` if `True` and `stop` it if `False`.

Also keep in mind the Moduler will not copy any files to the Jasmin instance. all communications are done through `Telnet`. So, in case of `MoInterceptor`, and `MtInterceptor`. You will have to make the script accessible to the Jasmin server. Example of a `MtInterceptor` document:
```
{
    _id: '$ORDER',
    filters: 'premium_numbers',
    order: '$ORDER',
    script: 'python3(/tmp/premium.py)',
    type: 'StaticMTInterceptor'
}
```
You will have to make the sure Jasmin have access to `/tmp/premium.py` before adding the document to MongoDB.


To start the Realtime Moduler. you have to export the fallowing variables:

#### export:
```
JASMIN_CLI_HOST                 =       **REQUIRED:NoDefault**
JASMIN_CLI_PORT                 =               8990
JASMIN_CLI_TIMEOUT              =                30
JASMIN_CLI_AUTH                 =               True
JASMIN_CLI_USERNAME             =             jcliadmin
JASMIN_CLI_PASSWORD             =              jclipwd
JASMIN_CLI_STANDARD_PROMPT      =              "jcli : "
JASMIN_CLI_INTERACTIVE_PROMPT   =                "> "
MONGODB_CONNECTION_STRING       =       **REQUIRED:NoDefault**
MONGODB_MODULES_DATABASE        =       **REQUIRED:NoDefault**
```
#### Then run:
```
jasminrealtimed --moduler
```


## Realtime Biller:
Sync User balance with a specified MongoDB collection's key. Can be used to Sync multiple instances of Jasmin if pared with configurations sync. This Realtime service can be used to keep a `user` balance in sync if where set to update the same Database and Collection of the Realtime Moduler service.
To start the Realtime Biller. you have to export the fallowing variables:

#### export:
```
AMQP_BROKER_HOST                =       **REQUIRED:NoDefault**
AMQP_BROKER_PORT                =               5672
MONGODB_CONNECTION_STRING       =       **REQUIRED:NoDefault**
MONGODB_BILL_DATABASE           =       **REQUIRED:NoDefault**
MONGODB_BILL_COLLECTION         =       **REQUIRED:NoDefault**
MONGODB_BILL_BALANCE_KEY        =       **REQUIRED:NoDefault**
```
#### Then run:
```
jasminrealtimed --biller
```


## Realtime Logger:
Log all sms to a MongoDB collection.
To start the Realtime Logger. you have to export the fallowing variables:

#### export:
```
AMQP_BROKER_HOST                =       **REQUIRED:NoDefault**
AMQP_BROKER_PORT                =               5672
MONGODB_CONNECTION_STRING       =       **REQUIRED:NoDefault**
MONGODB_LOGS_DATABASE           =       **REQUIRED:NoDefault**
MONGODB_LOGS_COLLECTION         =       **REQUIRED:NoDefault**
```
#### Then run:
```
jasminrealtimed --logger
```
