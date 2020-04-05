class Walk:
    """
        Walk is a sequence of vertices and edges where
            Vertex can be repeated
            Edges can be repeated
        Type of walks:
            Opened walk has starting vertex is not the same with ending vertex
            Closed walk has starting vertex is the same with ending vertex
    """
    pass


class Trail(Walk):
    """
        Trail is a walk but no repeated edges, also has opened and closed trail
            Vertex can be repeated
            Edge not repeated
    """
    pass


class Circuit(Trail):
    """
        Circuit is a closed trail
            Vertex can be repeated
            Edge not repeated
    """
    pass


class Path(Trail):
    """
        Path is a trail but not repeated vertices
            Vertex not repeated
            Edge not repeated
    """
    pass


class Cycle(Path):
    """
        Cycle is a closed path
            Vertex not repeated
            Edge not repeated
    """
    pass


# Special paths
class EulerPath(Path):
    """
        An Euler path is a path that uses every edge exactly once.
        An Euler path starts and ends at different vertices.
    """
    pass


class HamiltonianPath(Path):
    """
        A simple path in a graph G that passes through every vertex exactly once
    """
    pass


# Sequence
class Sequence(Walk):
    pass


class VertexSequence(Sequence):
    pass


class EdgeSequence(Sequence):
    pass


class VertexEdgeSequence(Sequence):
    pass