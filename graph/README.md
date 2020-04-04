# GRAPH NETWORK

## Definition
### Graph Theory
    A graph is defined as G = (V, E) where:
        V: a set of all vertices
        E: a set of all edges

### Graph Representation
    GRAPH
        A superclass for all kind of graphs
        A graph must have nodes (edges can be ignored)

    NODE 
        Presentation of an entity or instance 

    EDGE
        Presentation of a connection/linkage/relationships between nodes
        Must have a '_source' and '_target' attributes, where values are ID of nodes

    PATH


### Graph variants
    GRAPH can be distiguished to 2 types: DISCRETED-GRAPH and CONNECTED-GRAPH

        DISCRETED-GRAPH
            A graph that contains multi-subgraphs where subgraph can be a DISCRETED-GRAPH as well

        CONNECTED-GRAPH
            A graph that is enclosured by nodes and edges, all nodes must have a connection to the graph by at least 1 edge

#### Special Graph
    UNDIRECTED-GRAPH
        A CONNECTED-GRAPH with a path from A to B can be traversed back from B to A

    DIRECTED-GRAPH
        A CONNECTED-GRAPH with only has 1 path from A to B

    TREE
        A DIRECTED-GRAPH