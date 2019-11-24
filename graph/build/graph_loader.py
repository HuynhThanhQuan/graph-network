import json
import os
import pickle
from datetime import datetime
from graph.core import graph_manager
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GraphLoader:
    def __init__(self, storage_location, format_type='pickle'):
        self.storage_location = storage_location
        self.file_format = format_type
        self.node_manager = None
        self.stacktrace_manager = None

    @staticmethod
    def __json2graph__(json_obj):
        def dict2node(dictionary):
            node = graph_manager.Node(dictionary['name'], dictionary['weight'])
            node.out_edge = dictionary['out_edge']
            node.in_edge = dictionary['in_edge']
            node.fre_id_stacktrace = dictionary['fre_id_stacktrace']
            # node.static_attribute = dictionary['static_attribute']
            return node

        try:
            # Read Node Manager from json oject
            node_manager = graph_manager.NodeManager()
            node_manager.pool = {dictionary['hash_id']: dict2node(dictionary) for dictionary in
                                 json_obj['node_pool']}

            # Read Stacktrace Manager from json object
            stacktrace_manager = graph_manager.StacktraceManager()
            stacktrace_manager.uuid = json_obj['stacktrace_manager']['uuid']
            stacktrace_manager.stacktrace = json_obj['stacktrace_manager']['stacktrace']
            stacktrace_manager.node_stacktrace = {k: [node_manager.pool[_] for _ in v] for k, v in
                                                  json_obj['stacktrace_manager']['node_stacktrace'].items()}
            stacktrace_manager.freq_stacktrace = json_obj['stacktrace_manager']['freq_stacktrace']
            stacktrace_manager.uuid_nodes_map = {k: [node_manager.pool[_] for _ in v] for k, v in
                                                 json_obj['stacktrace_manager']['uuid_nodes_map'].items()}
            return node_manager, stacktrace_manager
        except KeyError as error:
            logger.error('Failed to convert JSON to Graph Manager - No Key {}'.format(error.args[0]))
            return None

    def load(self, path):
        start = datetime.now()
        if os.path.exists(self.storage_location):
            if self.file_format == 'pickle':
                self.__load_from_pickle__(path)
            elif self.file_format == 'hdf5':
                self.__load_from_hdf5__(path)
            else:
                self.__load_from_json__(path)
        else:
            logger.info('Not found pretrained graph.pkl - Auto create and store graph into "{}"'.
                        format(self.storage_location))
            return
        logger.info('Read pretrained Graph {}'.format(datetime.now() - start))

    def __load_from_json__(self, path):
        try:
            file_path = os.path.join(self.storage_location, path)
            file = open(file_path, 'r')
            graph_json_object = json.load(file)
            file.close()
            self.node_manager, self.stacktrace_manager = GraphLoader.__json2graph__(graph_json_object)
            logger.info('Loaded pretrained Graph from "{}" location'.format(self.storage_location))
        except Exception as error:
            logger.error('Failed to load Graph from file due to "{}"'.format(error.args[0]))

    def __load_from_pickle__(self, path):
        try:
            file_path = os.path.join(self.storage_location, path)
            file = open(file_path, 'rb')
            _graph_manager = pickle.load(file)
            file.close()
            self.node_manager, self.stacktrace_manager = _graph_manager.node_manager, _graph_manager.stacktrace_manager
            logger.info('Loaded pretrained Graph from "{}" location'.format(self.storage_location))
        except Exception as error:
            logger.error('Failed to load Graph from file due to "{}"'.format(error.args[0]))

    def __load_from_hdf5__(self, path):
        # TODO load from HDF5
        try:
            file_path = os.path.join(self.storage_location, path)
            file = open(file_path, 'r')
            graph_json_object = json.load(file)
            file.close()
            self.node_manager, self.stacktrace_manager = GraphLoader.__json2graph__(graph_json_object)
            logger.info('Loaded pretrained Graph from "{}" location'.format(self.storage_location))
        except Exception as error:
            logger.error('Failed to load Graph from file due to "{}"'.format(error.args[0]))
