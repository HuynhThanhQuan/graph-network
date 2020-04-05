from core.data_structure import exception as ds_exc
from core.data_structure import vertex as ds_vertex


class Edge:
    def __init__(self, src_endpoint, tgt_endpoint, **kwargs):
        if src_endpoint is None:
            raise ds_exc.InputNullSourceEndpoint()
        if isinstance(src_endpoint, ds_vertex.Vertex) is False:
            raise ds_exc.SourceEndpointNotVertexInstance()
        if tgt_endpoint is None:
            raise ds_exc.InputNullTargetEndpoint()
        if isinstance(tgt_endpoint, ds_vertex.Vertex) is False:
            raise ds_exc.TargetEndpointNotVertexInstance()

        self.src_endpoint = src_endpoint
        self.tgt_endpoint = tgt_endpoint
        self.kwargs = kwargs
        self.__is_valid__()

    def __src2tgt__(self):
        pass

    def __tgt2src__(self):
        pass

    def __is_valid__(self):
        raise ds_exc.NotImplementedError()


class DirectionalEdge(Edge):
    def __init__(self, src_endpoint, tgt_endpoint, **kwargs):
        super().__init__(src_endpoint=src_endpoint, tgt_endpoint=tgt_endpoint, **kwargs)

    def __tgt2src__(self):
        raise ds_exc.DirectionalEdgeRequestReverse()

    def __is_valid__(self):
        pass
    

class Loop(Edge):
    def __init__(self, src_endpoint, tgt_endpoint, **kwargs):
        super().__init__(src_endpoint=src_endpoint, tgt_endpoint=tgt_endpoint, **kwargs)

    def __is_valid__(self):
        if self.src_endpoint.id != self.tgt_endpoint.id:
            raise ds_exc.LoopHasDifferentEndpoints()


class ParallelEdge(Edge):
    def __init__(self, src_endpoint, tgt_endpoint, **kwargs):
        super().__init__(src_endpoint=src_endpoint, tgt_endpoint=tgt_endpoint, **kwargs)

    def __is_valid__(self):
        #TODO: how to recognize a parallel edge from multigraph
        pass


class PendantEdge(Edge):
    def __init__(self, src_endpoint, tgt_endpoint, **kwargs):
        super().__init__(src_endpoint=src_endpoint, tgt_endpoint=tgt_endpoint, **kwargs)
    
    def __is_valid__(self):
        if not isinstance(self.src_endpoint, ds_vertex.PendantVertex) and not isinstance(self.tgt_endpoint, ds_vertex.PendantVertex):
            raise ds_exc.PendantEdgeMustConnectPendantVertex()