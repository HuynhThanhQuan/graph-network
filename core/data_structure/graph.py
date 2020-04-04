from core.data_structure import vertex as ds_vertex
from core.data_structure import edge as ds_edge
from core.data_structure import traverse as ds_traverse
from core.data_structure import exception as ds_exc


class Graph:
    def __init__(self, vertices=[], edges=[], **kwargs):
        if vertices is None:
            raise ds_exc.InputNullVertices()
        if edges is None:
            raise ds_exc.InputNullEdges()
        self.V = set(vertices)
        self.E = set(edges)
        self.__is_valid__()

    def __is_valid__(self):
        raise NotImplementedError()


### Fundamental graphs
class NullGraph(Graph):
    """
        Null graph has both empty set of vertices and empty set of edges
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __is_valid__(self):
        if len(self.V) != 0 or len(self.E) != 0:
            raise ds_exc.NullGraphNotEmpty()


class TrivialGraph(Graph):
    """
        Trivial graph in which has only one vertex (isolated vertex)
    """
    def __init__(self, vertices, **kwargs):
        super().__init__(vertices=vertices, **kwargs)
        
    def __is_valid__(self):
        if len(self.V) != 1:
            raise ds_exc.TrivialGraphHasZeroOrMoreThanOneVertices()
        if len(self.E) != 0:
            raise ds_exc.TrivialGraphHasEdge()

    
class EmptyGraph(Graph):
    """
        Empty graph has an empty set of edges only (must have at least 1 vertex)
    """
    def __init__(self, vertices, **kwargs):
        super().__init__(vertices=vertices, **kwargs)
            
    def __is_valid__(self):
        if all(isinstance(v, ds_vertex.Vertex) for v in self.V) is False:
            raise ds_exc.InvalidInputVertexClass()
        if len(self.V) == 0:
            raise ds_exc.EmptyGraphHasNoVertex()
        if len(self.E) != 0:
            raise ds_exc.EmptyGraphHasEdge()


class SimpleGraph(Graph):
    """
        Simple graph in which no parallel edges or loops
    """
    def __init__(self, vertices, edges, **kwargs):
        super().__init__(vertices=vertices, edges=edges, **kwargs)

    def __is_valid__(self):
        if any(isinstance(e, ds_edge.Loop) for e in self.E):
            raise ds_exc.SimpleGraphHasLoop()
        if any(isinstance(e, ds_edge.ParallelEdge) for e in self.E):
            raise ds_exc.SimpleGraphHasParallelEdge()


class MultiGraph(Graph):
    """
        Multigraph in which can contain multiple edges connect the same pair of endpoints
    """
    def __init__(self, vertices, edges, **kwargs):
        super().__init__(vertices=vertices, edges=edges, **kwargs)
        
    def __is_valid__(self):
        if any(isinstance(e, ds_edge.ParallelEdge) for e in self.E) is False:
            raise ds_exc.MultiGraphHasNoParallelEdge()
        

class SubGraph(Graph):
    """
        Subgraph is detached from a super-graph (or Graph), super-graph must be known
    """
    def __is_valid__(self):
        if hasattr(self, 'super_graph') is False:
            raise ds_exc.SubGraphHasNoSuperGraphAttribute()
        if self.super_graph is None:
            raise ds_exc.SubGraphHasNoSuperGraph()


### Graph Variants
class ConnectedGraph(Graph):
    pass


class DisconnectedGraph(Graph):
    pass


class DirectedGraph(ConnectedGraph):
    pass


class UndirectedGraph(ConnectedGraph):
    pass


class DirectedAcyclicGraph(DirectedGraph):
    pass


class Tree(DirectedAcyclicGraph):
    pass


