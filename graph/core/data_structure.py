"""
Fundamental defintions and data structure of Graph-Network
    GRAPH
        A superclass for all kind of graphs
        A graph must have nodes (edges can be ignored)
        Graph can be distiguished to 2 types: DISCRETED-GRAPH and CONNECTED-GRAPH

    DISCRETED-GRAPH
        A graph that contains multi-subgraphs where subgraph can be a DISCRETED-GRAPH as well


    CONNECTED-GRAPH
        A graph that is enclosured by nodes and edges, all nodes must have a connection to the graph by at least 1 edge


    NODE 
        Presentation of an entity or instance 
    EDGE
        Presentation of a connection/linkage/relationships between nodes
        Must have a '_source' and '_target' attributes, where values are ID of nodes
"""

