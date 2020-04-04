class DatabaseException(Exception):
    def __init__(self, message):
        super(DatabaseException, self).__init__(message)


class DataRetrieverInvalidConfigure(DatabaseException):
    def __init__(self, message="Invalid configure, cannot find data"):
        super(DataRetrieverInvalidConfigure, self).__init__(message)


class DataRetrieverReturnEmptyData(DatabaseException):
    def __init__(self, message="Return empty generator, invalid format for analyzing"):
        super(DataRetrieverReturnEmptyData, self).__init__(message)


class DatabaseNullHostException(DatabaseException):
    def __init__(self, message='Null host exception, must be specific value'):
        super(DatabaseNullHostException, self).__init__(message)


class DatabaseNullPortException(DatabaseException):
    def __init__(self, message='Null port exception, must be specific value'):
        super(DatabaseNullPortException, self).__init__(message)


class DatabaseNullDBNameException(DatabaseException):
    def __init__(self, message='Null database name exception, must be specific value'):
        super(DatabaseNullDBNameException, self).__init__(message)


class DatabaseNullUserException(DatabaseException):
    def __init__(self, message='Null user exception, must be specific value'):
        super(DatabaseNullUserException, self).__init__(message)


class DatabaseNullPasswordException(DatabaseException):
    def __init__(self, message='Null password exception, must be specific value'):
        super(DatabaseNullPasswordException, self).__init__(message)


class DatabasePassingNullValueException(DatabaseException):
    def __init__(self, message='Null password exception, must be specific value'):
        super(DatabasePassingNullValueException, self).__init__(message)

