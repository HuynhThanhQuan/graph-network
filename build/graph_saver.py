import json
import os
import pickle
from datetime import datetime
from graph.core import graph_manager as gm
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GraphSaver:
    def __init__(self, storage_location, format_type='pickle'):
        self.storage_location = storage_location
        self.format_type = format_type

    @staticmethod
    def __graph2json__(node_manager, stacktrace_manager):
        def node2dict(hash_id, node):
            return {'hash_id': hash_id,
                    'name': node.name,
                    'weight': node.weight,
                    'out_edge': node.out_edge,
                    'in_edge': node.in_edge,
                    'fre_id_stacktrace': node.fre_id_stacktrace}

        parent_json_object = dict()
        # Convert Node Manager to json object
        json_obj_nodes = [node2dict(hash_id, node) for hash_id, node in
                          node_manager.pool.items()]
        # Convert Stacktrace Manager to json object
        json_stacktrace_manager = dict()
        json_stacktrace_manager['uuid'] = stacktrace_manager.uuid
        json_stacktrace_manager['stacktrace'] = stacktrace_manager.stacktrace
        json_stacktrace_manager['node_stacktrace'] = {k: [gm.GraphUtil.__hash_md5__(_.name) for _ in v]
                                                      for k, v in stacktrace_manager.node_stacktrace.items()}
        json_stacktrace_manager['freq_stacktrace'] = stacktrace_manager.freq_stacktrace
        json_stacktrace_manager['uuid_nodes_map'] = {k: [gm.GraphUtil.__hash_md5__(_.name) for _ in v]
                                                     for k, v in stacktrace_manager.uuid_nodes_map.items()}
        # Update json object
        parent_json_object['node_pool'] = json_obj_nodes
        parent_json_object['stacktrace_manager'] = json_stacktrace_manager
        return parent_json_object

    def save(self, path, graph_manager):
        if self.format_type == 'pickle':
            self.__save_into_pkl_format__(path, graph_manager)
        elif self.format_type == 'hdf5':
            self.__save_into_hdf5_format__(path, graph_manager)
        else:
            self.__save_into_json_format__(path, graph_manager)

    def __save_into_json_format__(self, path, graph_manager):
        try:
            file_path = os.path.join(self.storage_location, path)
            graph_json_object = GraphSaver.__graph2json__(graph_manager.node_manager,
                                                          graph_manager.stacktrace_manager)
            logger.info('Storing Graph with {} into JSON format file'.
                        format(len(graph_manager.node_manager.pool.keys())))
            start = datetime.now()
            file = open(file_path, 'w')
            json.dump(graph_json_object, file, indent=4)
            file.close()
            logger.info('Stored Graph with {} nodes in {}'.format(len(graph_manager.node_manager.pool.keys()),
                                                                  datetime.now() - start))
        except FileExistsError as e:
            logger.error("File not found")
            logger.error(e.args[0])

    def __save_into_pkl_format__(self, path, graph_manager):
        try:
            file_path = os.path.join(self.storage_location, path)
            logger.info('Storing Graph with {} into pickle format file'.
                        format(len(graph_manager.node_manager.pool.keys())))
            start = datetime.now()
            file = open(file_path, 'wb')
            pickle.dump(graph_manager, file, pickle.HIGHEST_PROTOCOL)
            file.close()
            logger.info('Stored Graph with {} nodes in {}'.format(len(graph_manager.node_manager.pool.keys()),
                                                                  datetime.now() - start))
        except FileExistsError as e:
            logger.error("File not found")
            logger.error(e.args[0])

    def __save_into_hdf5_format__(self, path, graph_manager):
        # TODO Save to HDF5
        try:
            file_path = os.path.join(self.storage_location, path)
            graph_json_object = GraphSaver.__graph2json__(graph_manager.node_manager,
                                                          graph_manager.stacktrace_manager)
            logger.info('Storing Graph with {} into HDF5 format file'.
                        format(len(graph_manager.node_manager.pool.keys())))
            start = datetime.now()
            file = open(file_path, 'w')
            json.dump(graph_json_object, file, indent=4)
            file.close()
            logger.info('Stored Graph with {} nodes in {}'.format(len(graph_manager.node_manager.pool.keys()),
                                                                  datetime.now() - start))
        except FileNotFoundError as e:
            logger.error("File not found")
            logger.error(e.args[0])
