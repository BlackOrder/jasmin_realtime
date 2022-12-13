from .sources import MongoDB
import logging


class Moduler:
    def __init__(self, connection_string: str, modules_database: str, host: str, port: int = 8990, timeout: int = 10, auth: bool = True, username: str = "jcliadmin", password: str = "jclipwd", standard_prompt: str = "jcli : ", interactive_prompt: str = "> "):
        self.MONGODB_CONNECTION_STRING = connection_string
        self.MONGODB_MODULES_DATABASE = modules_database
        self.telnet_config: dict = {
            "host": host,
            "port": port,
            "timeout": timeout,
            "auth": auth,
            "username": username,
            "password": password,
            "standard_prompt": standard_prompt,
            "interactive_prompt": interactive_prompt
        }
        logging.info("Starting ::Moduler Socket::")
        
        mongosource = MongoDB(connection_string=self.MONGODB_CONNECTION_STRING,
                              database_name=self.MONGODB_MODULES_DATABASE)
        if mongosource.startConnection() is True:
            mongosource.stream(
                telnet_config=self.telnet_config, syncCurrentFirst=True)
