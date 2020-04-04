### Abstraction
class Graph:
    def __init__(self):
        self.V = None
        self.E = None

### Fundamental graphs
class NullGraph(Graph):
    def __init__(self):
        self.V = set()
        self.E = set()

    def __is_qualified__(self):
        if self.V is None:
            raise 

class EmptyGraph(Graph):
    pass

class SimpleGraph(Graph):
    pass


class MultiGraph(Graph):
    pass


class SubGraph(Graph):
    pass


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


