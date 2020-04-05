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




class DirectionalEdgeRequestReverse(GraphDataStructureException):
    def __init__(self, message='Directional edge do not permit reverse traversal'):
        super().__init__(message)


class InputNullSourceEndpoint(GraphDataStructureException):
    def __init__(self, message='Input source endpoint must not be null'):
        super().__init__(message)


class InputNullTargetEndpoint(GraphDataStructureException):
    def __init__(self, message='Input target endpoint must not be null'):
        super().__init__(message)


class SourceEndpointNotVertexInstance(GraphDataStructureException):
    def __init__(self, message='Source endpoint must be a Vertex instance'):
        super().__init__(message)


class TargetEndpointNotVertexInstance(GraphDataStructureException):
    def __init__(self, message='Target endpoint must be a Vertex instance'):
        super().__init__(message)


class LoopHasDifferentEndpoints(GraphDataStructureException):
    def __init__(self, message='Target endpoint must be a Vertex instance'):
        super().__init__(message)


class PendantEdgeMustConnectPendantVertex(GraphDataStructureException):
    def __init__(self, message='Pendant edge must have pendant vertex'):
        super().__init__(message)


class ProhibitSubgraphInitialization(GraphDataStructureException):
    def __init__(self, message='Prohibit initialize subgraph, subgraph must be detached from a super-graph'):
        super().__init__(message)


class InputInvalidVertexInstance(GraphDataStructureException):
    def __init__(self, message='Input vertices must be instance of Vertex'):
        super().__init__(message)


class InputInvalidEdgeInstance(GraphDataStructureException):
    def __init__(self, message='Input edges must be instance of Edge'):
        super().__init__(message)


class ConnectedGraphHasIsolatedVertex(GraphDataStructureException):
    def __init__(self, message='Connected graph has isolated vertex'):
        super().__init__(message)


class DirectedGraphHasUndirectedEdge(GraphDataStructureException):
    def __init__(self, message='All edges of Directed Graph must be Directional Edge instance'):
        super().__init__(message)


class TreeHasMoreThanOneParent(GraphDataStructureException):
    def __init__(self, message='Tree must have only one parent and contain no cycle'):
        super().__init__(message)