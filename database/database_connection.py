import os
from database import database_exception as db_exc


class DatabaseConnection:
    def __init__(self, **kwargs):
        self.authentication = kwargs.get('authentication')
        self.mode = kwargs.get('mode', 'env')
        self.data_config = kwargs.get('data_config')
        self.host = None
        self.port = None
        self.name = None
        self.user = None
        self.password = None
        self.init_db_variables(kwargs)
        self.check_variables(kwargs.get('connection'))

    def init_db_variables(self, variables):
        if self.authentication is None:
            if self.mode == 'env':
                self.host = os.getenv('KI_HOST')
                self.port = os.getenv('KI_PORT')
                self.name = os.getenv('KI_KITDB')
                self.user = os.getenv('KI_USER')
                self.password = os.getenv('KI_PASSWORD')
            else:
                self.host = variables.get('host')
                self.port = variables.get('port')
                self.name = variables.get('name')
                self.user = variables.get('user')
                self.password = variables.get('password')
        else:
            self.host = self.authentication.host
            self.port = self.authentication.port
            self.name = self.authentication.name
            self.user = self.authentication.user
            self.password = self.authentication.password

    def check_variables(self, connection):
        if connection == 'online':
            if self.host is None:
                raise db_exc.DatabaseNullHostException()
            if self.port is None:
                raise db_exc.DatabaseNullPortException()
            if self.name is None:
                raise db_exc.DatabaseNullDBNameException()
            if self.user is None:
                raise db_exc.DatabaseNullUserException()
            if self.password is None:
                raise db_exc.DatabaseNullPasswordException()
