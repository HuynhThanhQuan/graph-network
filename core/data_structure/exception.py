### Python
class NotImplementedError(Exception):
    def __init__(self, message="Super class method is not implemented"):
        super().__init__(message)


### Graph
class GraphDataStructureException(Exception):
    def __init__(self, message):
        super().__init__(message)


class UninitializedGraph(GraphDataStructureException):
    def __init__(self, message='Graph object is not initialized'):
        super().__init__(message)


class NullGraphNotEmpty(GraphDataStructureException):
    def __init__(self, message='Null graph must has no vertex and no edge'):
        super().__init__(message)


class InvalidInputVertexClass(GraphDataStructureException):
    def __init__(self, message='Invalid input vertex class type'):
        super().__init__(message)


class EmptyGraphHasNoVertex(GraphDataStructureException):
    def __init__(self, message='Empty graph must have at least 1 node'):
        super().__init__(message)


class EmptyGraphHasEdge(GraphDataStructureException):
    def __init__(self, message='Empty graph must have no edge'):
        super().__init__(message)


class SimpleGraphHasLoop(GraphDataStructureException):
    def __init__(self, message='Simple graph must not have loop'):
        super().__init__(message)


class SimpleGraphHasParallelEdge(GraphDataStructureException):
    def __init__(self, message='Simple graph must not have parallel edge'):
        super().__init__(message)


class InputNullVertices(GraphDataStructureException):
    def __init__(self, message='Input vertices must not be null'):
        super().__init__(message)


class InputNullEdges(GraphDataStructureException):
    def __init__(self, message='Input edges must not be null'):
        super().__init__(message)


class MultiGraphHasNoParallelEdge(GraphDataStructureException):
    def __init__(self, message='Multigraph has at least 1 parallel edge'):
        super().__init__(message)


class SubGraphHasNoSuperGraphAttribute(GraphDataStructureException):
    def __init__(self, message='Subgraph class must have <super_graph> attribute'):
        super().__init__(message)


class SubGraphHasNoSuperGraph(GraphDataStructureException):
    def __init__(self, message='Subgraph must be detached from a super-graph'):
        super().__init__(message)
        

class TrivialGraphHasZeroOrMoreThanOneVertices(GraphDataStructureException):
    def __init__(self, message='Trivial graph has only one vertex'):
        super().__init__(message)


class TrivialGraphHasEdge(GraphDataStructureException):
    def __init__(self, message='Trivial graph has no edge'):
        super().__init__(message)