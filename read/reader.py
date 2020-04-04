import os

"""
Guild how to read your graph

Description:
    I provided several methods to read graph-network data but not limit other formats, please implement your own format as your need


### Graph Kinds & Data Structure
    UNDIRECTED-GRAPH            <SYMMETRIC-MATRIX, UPPER-MATRIX>
    DIRECTED-GRAPH              <ASYMETRTIC-MATRIX>
    TREE                        <TREE-HIERARCHY>
    MULTI-GRAPH

### Data IO Structure
    SYMMETRIC-MATRIX
        Square matrix N * N
        Numpy array or list of lists 
        Upper matrix must be symetric with lower matrix
    ASYMMETRIC-MATRIX
        Square matrix N * N
        Numpy array or list of lists 
    UPPER-MATRIX
        Can be a list of upper matrix (total length of each row is decreased by 1) or numpy array with all elements in lower matrix are zeros
    TREE-HIERARCHY
        A list of NODE_TREE objects or a multi-level nested dictionary
"""


class GraphReader():
    def __init__(self):
        pass

    def _prior_action_(self):
        pass

    def _post_action_(self):
        pass
