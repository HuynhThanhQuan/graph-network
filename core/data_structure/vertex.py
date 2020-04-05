class Vertex:
    def __init__(self, degree, **kwargs):
        self.degree = degree
        self.kwargs = kwargs


class IsolatedVertex(Vertex):
    def __init__(self, **kwargs):
        super().__init__(degree=0, **kwargs)


class PendantVertex(Vertex):
    def __init__(self, **kwargs):
        super().__init__(degree=1, **kwargs)

