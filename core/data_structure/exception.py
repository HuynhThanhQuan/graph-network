class GraphDataStructureException(Exception):
    def __init__(self, message):
        super().__init__(message)


class UninitializedGraph(GraphDataStructureException):
    def __init__(self, message='Graph object is not initialized'):
        super().__init__(message)
