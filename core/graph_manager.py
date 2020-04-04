import numpy as np
from datetime import datetime
import hashlib
from graph.build import graph_configure as g_conf
from graph.build import graph_distributor as g_dis
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GraphManager:
    # TODO: AbstractGraph, AbstractGraphManager
    # TODO: AbstractNode, AbstractNodeManager
    # TODO: AbstractEdge, AbstractEdgeManager
    # TODO: Rename Stacktrace, StacktraceManager to Trace, TraceManager
    # TODO: AbstractTrace, AbstractTraceManager
    # TODO: Ranking

    def __init__(self, node_size=None, load_graph=True, save_graph=False,
                 configure=None,
                 storage_location='default'):
        self.node_size = node_size
        self.load_graph = load_graph
        self.save_graph = save_graph
        self.configure = configure
        self.storage_location = storage_location
        self.graph_configure = None
        self.node_manager = None
        self.stacktrace_manager = None
        self.init_config()

    def init_config(self):
        self.graph_configure = g_conf.GraphConfigMechanism(storage_location=self.storage_location,
                                                           load_graph=self.load_graph,
                                                           save_graph=self.save_graph) \
            if self.configure is None else self.configure
        self.node_manager = self.graph_configure.graph_loader.node_manager
        self.stacktrace_manager = self.graph_configure.graph_loader.stacktrace_manager

    def get_total_node_pool(self):
        return len(self.node_manager.pool.keys())

    def get_all_node_pool(self):
        return list(self.node_manager.pool.keys())

    def __valid_non_existing_data_in_graph__(self, uuid, data, static_attributes):
        if isinstance(uuid, int):
            uuid, data, static_attributes = [uuid], [data], [static_attributes]
        if isinstance(uuid, list):
            non_existing = list(zip(*[(_id, _data, _static_attribute) for _id, _data, _static_attribute in
                                      zip(uuid, data, static_attributes) if _id not in self.stacktrace_manager.uuid]))
            return ([], [], []) if len(non_existing) == 0 else (non_existing[0], non_existing[1], non_existing[2])
        return uuid, data, static_attributes

    def add(self, uuid, data, static_attributes=None, offset=0):
        assert isinstance(uuid, int) or all(isinstance(_, int) for _ in uuid)
        assert isinstance(data, str) or all(isinstance(_, list) for _ in data)

        num_data = len(data)
        if g_conf.GraphEnvVar.FORCE_SPEEDUP is True or num_data >= g_conf.GraphEnvVar.MAX_ITER_DATA:
            self.__prepare_speed_up__(data, num_data, offset, static_attributes, uuid)
        else:
            self.__prepare_one_shot__(data, num_data, static_attributes, uuid)
        self.__post_action__()

    def __prepare_one_shot__(self, data, num_data, static_attributes, uuid):
        if static_attributes is None:
            static_attributes = [{'static_attribute': None}] * num_data if isinstance(uuid, list) \
                else static_attributes
        valid_uuid, valid_data, valid_static_attributes = \
            self.__valid_non_existing_data_in_graph__(uuid, data, static_attributes)
        num_valid_data = len(valid_uuid)
        assert all(isinstance(_, int) for _ in valid_uuid)
        assert all(isinstance(_, list) for _ in valid_data)
        assert all(isinstance(_, dict) for _ in valid_static_attributes)
        if num_valid_data > 0:
            logger.info('Number of data to be added into Graph {}'.format(num_valid_data))
        self.__add_list_stacktrace__(valid_uuid, valid_data, valid_static_attributes)

    def __prepare_speed_up__(self, data, num_data, offset, static_attributes, uuid):
        if offset == 0:
            logger.info('Adding records into Graph by speed-up...')
        start = datetime.now()
        iterations = num_data // g_conf.GraphEnvVar.CHUNK_SIZE + 1 \
            if num_data % g_conf.GraphEnvVar.CHUNK_SIZE != 0 \
            else num_data // g_conf.GraphEnvVar.CHUNK_SIZE
        for i in range(iterations):
            start_idx = i * g_conf.GraphEnvVar.CHUNK_SIZE
            end_idx = min(num_data, (i + 1) * g_conf.GraphEnvVar.CHUNK_SIZE)
            if start_idx >= end_idx:
                break
            logger.info('--- Adding record {} to {} - Iterate {}/{}'.
                        format(offset + start_idx, offset + end_idx, i + 1, iterations))
            chunked_uuid = uuid[start_idx:end_idx]
            chunked_data = data[start_idx:end_idx]
            chunked_attributes = [{'static_attribute': None}] * len(chunked_uuid) \
                if static_attributes is None else static_attributes[start_idx:end_idx]
            self.__add_with_speedup__(chunked_uuid, chunked_data, chunked_attributes)
        logger.info('Added record {} to {} into Graph within {} - total {} nodes'.
                    format(offset, offset + num_data, datetime.now() - start, self.get_total_node_pool()))

    def save(self):
        self.graph_configure.__post_action__(self)

    def __add_single_stacktrace__(self, _id, stacktrace, static_attribute):
        self.node_manager.init_nodes(stacktrace, static_attribute)
        self.stacktrace_manager.track(self.node_manager.pool, _id, stacktrace)

    def __add_list_stacktrace__(self, ids, list_stacktrace, static_attributes):
        logger.info('Iteratively adding records into Graph...')
        start = datetime.now()
        for _id, stacktrace, static_attribute in zip(ids, list_stacktrace, static_attributes):
            self.__add_single_stacktrace__(_id, stacktrace, static_attribute)
        logger.info('Added {} records into Graph within {}'.format(len(ids), datetime.now() - start))

    def __add_with_speedup__(self, ids, list_stacktrace, static_attributes):
        flatten_methods = [method for method_stacktrace in list_stacktrace for method in method_stacktrace]
        flatten_static_attributes = [attribute for method_stacktrace in list_stacktrace for attribute in
                                     [static_attributes] * len(method_stacktrace)]
        self.node_manager.init_pool(flatten_methods, flatten_static_attributes)
        self.node_manager.init_edges(list_stacktrace)
        for _id, stacktrace in zip(ids, list_stacktrace):
            self.stacktrace_manager.track(self.node_manager.pool, _id, stacktrace)

    @staticmethod
    def convert_hash_stacktrace(stacktrace):
        return np.array([GraphUtil.__hash_md5__(method) for method in stacktrace])

    def __convert_to_ohv__(self, list_stacktrace):
        start = datetime.now()
        node_pool = np.array(list(self.node_manager.pool.keys()))
        logger.info('Lookingup {} records in {} nodes with'.format(len(list_stacktrace), len(node_pool)))
        ohv_stacktrace = np.array([np.isin(node_pool, GraphManager.convert_hash_stacktrace(stacktrace)).
                                  astype(np.int32) for stacktrace in list_stacktrace])
        logger.info('Lookup {} records in {} nodes with {}'.format(len(list_stacktrace),
                                                                   len(node_pool), datetime.now() - start))
        return node_pool, ohv_stacktrace

    @staticmethod
    def compare_ohv_stacktrace(ohv_stacktrace):
        logger.info('Shape of one-hot-matrix {}'.format(ohv_stacktrace.shape))
        start = datetime.now()
        ohv_shape = len(ohv_stacktrace)
        try:
            numerator = np.dot(ohv_stacktrace, ohv_stacktrace.T)
            assert numerator.shape == (ohv_stacktrace.shape[0], ohv_stacktrace.shape[0]), numerator.shape
            denominator = np.sqrt(np.sum(ohv_stacktrace ** 2, axis=1))[:, np.newaxis] * np.sqrt(
                np.sum(ohv_stacktrace ** 2, axis=1))[:, np.newaxis].T
            assert (denominator > 0).all(), "Denominator is zero"
            similarity_matrix = np.multiply(numerator, 1 / denominator)
        except MemoryError:
            logger.error('Unable to allocate memory for matrix shape ({}, {})'.format(ohv_shape, ohv_shape))
            raise MemoryError('Unable to allocate memory for matrix shape ({}, {})'.format(ohv_shape, ohv_shape))
        except Exception as e:
            logger.error('Failed to compare one-hot-vector due to {}'.format(e.args[0]))
            raise Exception(e.args[0])
        logger.info('Calculating one-hot-matrix {}'.format(datetime.now() - start))
        return similarity_matrix

    @staticmethod
    def get_top_k(array, k=3, reverse=False):
        if reverse is False:
            top_k_index = np.argsort(array)[-k:]
        else:
            top_k_index = np.argsort(array)[:k]
        return top_k_index

    def get_top_k_nodes_in_pool(self, k=3, reverse=False):
        nodes, weights = zip(*[(k, v.weight) for (k, v) in self.node_manager.pool.items()])
        top_k_index = GraphManager.get_top_k(weights, k, reverse)
        return np.array(nodes)[top_k_index][::-1], np.array(weights)[top_k_index][::-1]

    def get_top_k_stacktrace(self, k=3, reverse=False):
        stacktraces, weights = zip(*self.stacktrace_manager.freq_stacktrace.items())
        stacktraces = [self.stacktrace_manager.stacktrace[id_stacktrace] for id_stacktrace in stacktraces]
        top_k_index = GraphManager.get_top_k(weights, k, reverse)
        return np.array(stacktraces)[top_k_index][::-1], np.array(weights)[top_k_index][::-1]

    def get_top_k_neighbor_nodes(self, node_name, k=1, reverse=False):
        target_node = self.node_manager.get_node(node_name)
        nodes, counts = zip(*target_node.out_edge.items())
        top_k_index = GraphManager.get_top_k(counts, k, reverse)
        return np.array(nodes)[top_k_index][::-1], np.array(counts)[top_k_index][::-1]

    def get_top_k_stacktrace_along_node(self, node_name, k=1, reverse=False):
        target_node = self.node_manager.get_node(node_name)
        stacktraces, counts = zip(*target_node.fre_id_stacktrace.items())
        stacktraces = [self.stacktrace_manager.stacktrace[id_stacktrace] for id_stacktrace in stacktraces]
        top_k_index = GraphManager.get_top_k(counts, k, reverse)
        return np.array(stacktraces)[top_k_index][::-1], np.array(counts)[top_k_index][::-1]

    def __post_action__(self):
        g_dis.distribute(self)

        # Reset node and linkages
        self.node_manager = NodeManager()
        self.stacktrace_manager = StacktraceManager()


class Node:
    def __init__(self, name, default_weight=0, static_attribute=None):
        self.name = name
        self.weight = default_weight
        self.out_edge = {}
        self.in_edge = {}
        self.fre_id_stacktrace = {}
        self.static_attribute = static_attribute


class NodeManager:
    def __init__(self):
        self.pool = {}

    def get_node(self, node_name):
        return self.pool[GraphUtil.__hash_md5__(node_name)]

    def init_nodes(self, stacktrace, static_attribute):
        for method in stacktrace:
            if method not in list(self.pool.keys()):
                self.pool[GraphUtil.__hash_md5__(method)] = Node(method, static_attribute=static_attribute)
            self.pool[GraphUtil.__hash_md5__(method)].weight += 1

        for i in range(len(stacktrace) - 1):
            node = self.pool[GraphUtil.__hash_md5__(stacktrace[i])]
            next_node = self.pool[GraphUtil.__hash_md5__(stacktrace[i + 1])]
            node.out_edge[GraphUtil.__hash_md5__(next_node.name)] = \
                node.out_edge.get(GraphUtil.__hash_md5__(next_node.name), 0) + 1
            next_node.in_edge[GraphUtil.__hash_md5__(node.name)] = \
                next_node.in_edge.get(GraphUtil.__hash_md5__(node.name), 0) + 1

        id_stacktrace = ' '.join(stacktrace)
        hash_id_stacktrace = GraphUtil.__hash_md5__(id_stacktrace)
        for method in stacktrace:
            self.pool[GraphUtil.__hash_md5__(method)].fre_id_stacktrace[hash_id_stacktrace] = \
                self.pool[GraphUtil.__hash_md5__(method)].fre_id_stacktrace.get(hash_id_stacktrace, 0) + 1

    def init_pool(self, flatten_methods, flatten_static_attributes):
        assert flatten_methods is not None, "Cannot initialize None node pools"
        assert flatten_static_attributes is not None, "None attribute"
        assert len(flatten_methods) == len(flatten_static_attributes), \
            "Mismatched shape between {} and {}".format(len(flatten_methods), len(flatten_static_attributes))
        nonexisted_nodes = {GraphUtil.__hash_md5__(method): Node(method, static_attribute=static_attribute)
                            for method, static_attribute in zip(flatten_methods, flatten_static_attributes)
                            if method not in list(self.pool.keys())}
        self.pool.update(nonexisted_nodes)

        for method in flatten_methods:
            self.pool[GraphUtil.__hash_md5__(method)].weight += 1

    def init_edges(self, list_stacktrace):
        for stacktrace in list_stacktrace:
            for i in range(len(stacktrace) - 1):
                node = self.pool[GraphUtil.__hash_md5__(stacktrace[i])]
                next_node = self.pool[GraphUtil.__hash_md5__(stacktrace[i + 1])]
                node.out_edge[GraphUtil.__hash_md5__(next_node.name)] = \
                    node.out_edge.get(GraphUtil.__hash_md5__(next_node.name), 0) + 1
                next_node.in_edge[GraphUtil.__hash_md5__(node.name)] = \
                    next_node.in_edge.get(GraphUtil.__hash_md5__(node.name), 0) + 1

            hash_id_stacktrace = GraphUtil.__hash_md5__(' '.join(stacktrace))
            for method in stacktrace:
                self.pool[GraphUtil.__hash_md5__(method)].fre_id_stacktrace[hash_id_stacktrace] = \
                    self.pool[GraphUtil.__hash_md5__(method)].fre_id_stacktrace.get(hash_id_stacktrace, 0) + 1


class StacktraceManager:
    def __init__(self):
        self.uuid = []
        self.stacktrace = {}
        self.node_stacktrace = {}
        self.freq_stacktrace = {}
        self.uuid_nodes_map = {}

    def track(self, node_pool, _id, stacktrace):
        self.uuid.append(_id)
        nodes_stacktrace = [node_pool[GraphUtil.__hash_md5__(st)] for st in stacktrace]
        hash_id_stacktrace = GraphUtil.__hash_md5__(' '.join(stacktrace))
        self.stacktrace[hash_id_stacktrace] = stacktrace
        self.node_stacktrace[hash_id_stacktrace] = nodes_stacktrace
        self.freq_stacktrace[hash_id_stacktrace] = self.freq_stacktrace.get(hash_id_stacktrace, 0) + 1
        self.uuid_nodes_map[_id] = nodes_stacktrace


class GraphUtil:
    @staticmethod
    def __hash_md5__(string):
        hash_object = hashlib.md5(string.encode())
        return hash_object.hexdigest()
