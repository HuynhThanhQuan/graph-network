class Vertex:
    def __init__(self, **kwargs):
        self.degree = None

class IsolatedVertex(Vertex):
    def __init__(self, **kwargs):
        self.degree = 0


class PendantVertex(Vertex):
    def __init__(self, **kwargs):
        self.degree = 1



 