class GraphException(Exception):
    def __init__(self, message):
        super(GraphException, self).__init__(message)


class GraphStorageInvalidLocation(GraphException):
    def __init__(self, message='Invalid graph storage location'):
        super(GraphStorageInvalidLocation, self).__init__(message)


class GraphStorageUnableInitialize(GraphException):
    def __init__(self, message='Unable to initialize Graph Storage'):
        super(GraphStorageUnableInitialize, self).__init__(message)


class GraphStorageExceedMaximumAttemps(GraphException):
    def __init__(self, message='Exceed maximum number of attempt to configure Graph Storage'):
        super(GraphStorageExceedMaximumAttemps, self).__init__(message)


class GraphStorageErrorDeletingGraphVersion(GraphException):
    def __init__(self, message='Error deleting oldest Graph Version history'):
        super(GraphStorageErrorDeletingGraphVersion, self).__init__(message)


class GraphDistributedLocationNotFound(GraphException):
    def __init__(self, message='Not found location for Graph Distributing mechanism'):
        super(GraphDistributedLocationNotFound, self).__init__(message)


class GraphDistributorInitMasterFailed(GraphException):
    def __init__(self, message='Fail to init master node in Graph distribution'):
        super(GraphDistributorInitMasterFailed, self).__init__(message)


class GraphDistributorSlaveSectionNotDefined(GraphException):
    def __init__(self, message='Unidentify SLAVE Section in Master INI config'):
        super(GraphDistributorSlaveSectionNotDefined, self).__init__(message)
