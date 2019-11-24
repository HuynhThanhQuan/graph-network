import os
from graph.core import graph_manager
from graph.build import graph_loader, graph_saver, graph_version_history
from graph.build import graph_distributor as g_dis


class GraphEnvVar:
    STORAGE_LOCATION = 'default'
    FOLDER_STORAGE = 'graph_storage'
    LOAD_GRAPH = True
    SAVE_GRAPH = False
    ALGORITHMS = 'default'
    MAX_STORAGE = 10
    CHUNK_SIZE = 5000
    MAX_ITER_DATA = 10000
    FORCE_SPEEDUP = False
    GRAPH_DISTRIBUTED = True
    DISTRIBUTED_LOCATION = 'distributed'

    def __init__(self, kwargs):
        GraphEnvVar.STORAGE_LOCATION = kwargs.get('storage_location', 'default')
        GraphEnvVar.FOLDER_STORAGE = kwargs.get('folder_storage', 'graph_storage')
        GraphEnvVar.LOAD_GRAPH = bool(kwargs.get('load_graph', True))
        GraphEnvVar.SAVE_GRAPH = bool(kwargs.get('save_graph', False))
        GraphEnvVar.ALGORITHMS = kwargs.get('algorithms', 'default')
        GraphEnvVar.MAX_STORAGE = int(kwargs.get('max_storage', 10))
        GraphEnvVar.CHUNK_SIZE = int(kwargs.get('chunk_size', 5000))
        GraphEnvVar.MAX_ITER_DATA = int(kwargs.get('max_iter_data', 10000))
        GraphEnvVar.FORCE_SPEEDUP = bool(kwargs.get('force_speedup', False))
        GraphEnvVar.GRAPH_DISTRIBUTED = bool(kwargs.get('graph_distributed', True))
        GraphEnvVar.DISTRIBUTED_LOCATION = kwargs.get('distributed_location', 'distributed')
        GraphEnvVar.init_services()

    @staticmethod
    def init_services():
        if GraphEnvVar.GRAPH_DISTRIBUTED is True:
            if GraphEnvVar.DISTRIBUTED_LOCATION == 'distributed':
                GraphEnvVar.DISTRIBUTED_LOCATION = os.path.join(os.path.dirname(
                    os.path.dirname(os.path.dirname(__file__))), 'distributed')
            if not os.path.exists(GraphEnvVar.DISTRIBUTED_LOCATION):
                # Find Distributed Location for graph storage
                os.mkdir(GraphEnvVar.DISTRIBUTED_LOCATION)

    @staticmethod
    def init_graph_distributed():
        if GraphEnvVar.GRAPH_DISTRIBUTED is True:
            g_dis.init_distributed_clusters()

    @staticmethod
    def continue_build_graph_distributed_with_hashcode(hashcode_analysis):
        g_dis.continue_distributed_clusters(hashcode_analysis)


class GraphConfigMechanism:
    def __init__(self, storage_location, load_graph, save_graph):
        self.storage_location = storage_location
        self.load_graph = load_graph
        self.save_graph = save_graph
        self.graph_loader = None
        self.graph_saver = None
        self.graph_version_history = None
        self.__init_configure__()

    def __init_configure__(self):
        self.__check_location__()
        self.__init_graph_version_history__()
        self.__init_graph_loader__()

    def __check_location__(self):
        if self.storage_location == 'default':
            self.storage_location = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                 GraphEnvVar.FOLDER_STORAGE)
        else:
            self.storage_location = os.path.join(self.storage_location, GraphEnvVar.FOLDER_STORAGE)

    def __init_graph_version_history__(self):
        self.graph_version_history = graph_version_history.GraphVersionHistory(self.storage_location)

    def __init_graph_loader__(self):
        self.graph_loader = graph_loader.GraphLoader(self.storage_location)
        self.graph_loader.node_manager = graph_manager.NodeManager()
        self.graph_loader.stacktrace_manager = graph_manager.StacktraceManager()
        if self.load_graph is True:
            current_graph_version = self.graph_version_history.active_latest_version()
            if current_graph_version is not None:
                self.graph_loader.load(current_graph_version.uuid)

    def __post_action__(self, _graph_manager):
        if self.save_graph is True:
            graph_version = self.graph_version_history.register(_graph_manager)
            self.graph_saver = graph_saver.GraphSaver(self.storage_location)
            self.graph_saver.save(graph_version.path, _graph_manager)
