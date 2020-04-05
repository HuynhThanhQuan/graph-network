from core.data_structure import vertex as ds_vertex
from core.data_structure import edge as ds_edge
from core.data_structure import traverse as ds_traverse
from core.data_structure import exception as ds_exc


class Graph:
    def __init__(self, vertices=[], edges=[], **kwargs):
        """
            Initialize a valid Graph object
            
            Args:
                vertices: list of Vertex objects (must not be null)
                edges: list of Edge objects (must not be null)
        """
        if vertices is None:
            raise ds_exc.InputNullVertices()
        if edges is None:
            raise ds_exc.InputNullEdges()
        if len(vertices) != 0 and all(isinstance(v, ds_vertex.Vertex) for v in vertices) is False:
            raise ds_exc.InputInvalidVertexInstance()
        if len(edges) != 0 and all(isinstance(e, ds_edge.Edge) for e in edges) is False:
            raise ds_exc.InputInvalidEdgeInstance()
        self.V = set(vertices)
        self.E = set(edges)
        self.kwargs = kwargs
        self.__prior_checking__()

    def __prior_checking__(self):
        raise NotImplementedError()

    def __post_checking__(self):
        raise NotImplementedError()


### Basic Graphs
class NullGraph(Graph):
    """
        Null graph has both empty set of vertices and empty set of edges
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __prior_checking__(self):
        if len(self.V) != 0 or len(self.E) != 0:
            raise ds_exc.NullGraphNotEmpty()


class TrivialGraph(Graph):
    """
        Trivial graph in which has only one vertex (isolated vertex)
    """
    def __init__(self, vertices, **kwargs):
        super().__init__(vertices=vertices, **kwargs)
        
    def __prior_checking__(self):
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
            
    def __prior_checking__(self):
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

    def __prior_checking__(self):
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
        
    def __prior_checking__(self):
        if any(isinstance(e, ds_edge.ParallelEdge) for e in self.E) is False:
            raise ds_exc.MultiGraphHasNoParallelEdge()
        

class SubGraph(Graph):
    """
        Subgraph is detached from a super-graph (or Graph), super-graph must be known
    """
    def __init__(self):
        raise ds_exc.ProhibitSubgraphInitialization()

    def __prior_checking__(self):
        """
            A special class, SubGraph class must have valid <super_graph> attribute
        """
        if hasattr(self, 'super_graph') is False:
            raise ds_exc.SubGraphHasNoSuperGraphAttribute()
        if self.super_graph is None:
            raise ds_exc.SubGraphHasNoSuperGraph()


### Graph Variants
class ConnectedGraph(Graph):
    """
        A graph that is enclosured by vertices and edges, all vertices must have at least 1 edge to the graph
    """
    def __init__(self, vertices, edges, **kwargs):
        super().__init__(vertices=vertices, edges=edges, **kwargs)

    def __prior_checking__(self):
        """
            Compare 2 sets of vertex IDs and endpoint IDs of edges
            If mismatched between 2 sets, it means connected graph has isolated vertices
        """
        vertex_ids = set([v.id for v in self.V])
        endpoint_ids = []
        for e in self.E:
            endpoint_ids.append(e.src_endpoint.id)
            endpoint_ids.append(e.tgt_endpoint.id)
        endpoint_ids = set(endpoint_ids)
        if vertex_ids != endpoint_ids:
            raise ds_exc.ConnectedGraphHasIsolatedVertex()
        

class DisconnectedGraph(Graph):
    """
        A graph that can contains many sub-graphs or isolated vertices where subgraph can be a DISCONNECTED-GRAPH as well
    """
    def __init__(self, vertices, edges, **kwargs):
        super().__init__(vertices=vertices, edges=edges, **kwargs)

    def __prior_checking__(self):
        """
            No any constraint for this kind of graph
        """
        pass


class UndirectedGraph(ConnectedGraph):
    """
        A CONNECTED-GRAPH in which all edges can be traversed forward and backward
    """
    def __init__(self, vertices, edges, **kwargs):
        super().__init__(vertices=vertices, edges=edges, **kwargs)

    def __prior_checking__(self):
        super().__prior_checking__()


class DirectedGraph(ConnectedGraph):
    """
        A CONNECTED-GRAPH in which every edge can only be traversed in 1 direction
    """
    def __init__(self, vertices, edges, **kwargs):
        super().__init__(vertices=vertices, edges=edges, **kwargs)

    def __prior_checking__(self):
        """
            A valid connected-graph with all edges must be DirectionalEdge objects
        """
        super().__prior_checking__()
        if all(isinstance(e, ds_edge.DirectionalEdge) for e in self.E) is False:
            raise ds_exc.DirectedGraphHasUndirectedEdge()


class DirectedAcyclicGraph(DirectedGraph):
    """
        A DIRECTED-GRAPH that is sorted in topological order or impossible to come back to the same vertex by traversing any edges
    """
    def __init__(self, vertices, edges, **kwargs):
        super().__init__(vertices=vertices, edges=edges, **kwargs)

    def __prior_checking__(self):
        """
            Find cycle in the graph (can be found by Deep-First Search)
        """
        #TODO: how to find cycle in graph, by what algorithm
        pass


class Tree(DirectedAcyclicGraph):
    """
        A DIRECTED-ACYCLIC-GRAPH but a child can have only one parent
    """
    def __init__(self, vertices, edges, **kwargs):
        super().__init__(vertices=vertices, edges=edges, **kwargs)

    def __prior_checking__(self):
        """
            A valid DirectedAcyclicGraph and child vertex has only 1 parent, except the first vertex
        """
        super().__prior_checking__()
        if all(len(v.parents) <=1 for v in self.V) is False:
            raise ds_exc.TreeHasMoreThanOneParent()


