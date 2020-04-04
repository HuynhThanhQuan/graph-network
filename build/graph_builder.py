from datetime import datetime
from graph.core.graph_manager import GraphManager
from database.data_retriever import DataRetriever
from ki_django import global_config
from database import database_exception, data_inserter
from graph.build import graph_distributor as g_dis
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GraphBuilder:
    def __init__(self,
                 graph_parser,
                 graph_manager=None,
                 load_graph=False,
                 save_graph=False,
                 data_executor=None):
        self.graph_parser = graph_parser
        self.load_graph = load_graph
        self.save_graph = save_graph
        self.graph_manager = graph_manager
        self.data_executor = data_executor

    def load(self):
        if self.load_graph is True:
            self.read_global_variables()
        else:
            self.graph_manager = GraphManager(load_graph=self.load_graph)
        return self

    def build(self, data_retriever):
        start = datetime.now()
        logger.info('Preparing to build Graph')
        self.data_executor = data_retriever
        self.graph_manager = GraphManager(load_graph=self.load_graph, save_graph=True)
        generator = data_retriever.execute()
        if generator is not None:
            self.__fit_generator__(generator)
            logger.info('Building Graph completed taken {}'.format(datetime.now() - start))
            print('Reloading Global Config automatically')
            global_config.init()
        else:
            raise database_exception.DataRetrieverReturnEmptyData()

    def __fit_generator__(self, generator):
        logger.info('Initializing Graph Version')
        start = datetime.now()
        acc_offset = 0
        for data in generator:
            logger.info("--- Reading record {} to record {}".format(acc_offset, acc_offset + len(data)))
            uuid, error_logs, static_attributes = DataRetriever.get_only_necessary_data(data)
            self.__fit__(uuid, error_logs, static_attributes, offset=acc_offset)
            self.__record_process__(uuid)
            acc_offset += len(error_logs)
        logger.info("Read {} records within {}".format(acc_offset, datetime.now() - start))
        self.graph_manager.save()

    def fit(self, data_bundles):
        assert isinstance(data_bundles, tuple)
        uuid, error_logs = data_bundles
        self.__fit__(uuid, error_logs)

    def __fit__(self, uuid, error_logs, static_attributes=None, offset=0):
        assert error_logs is not None and uuid is not None
        assert len(error_logs) > 0 and len(uuid) > 0, "Size must be greater than 0"
        assert len(uuid) == len(error_logs), "UUID and Error Logs must be the same length"
        pro_uuid, pro_methods_list = uuid, self.graph_parser.parse(error_logs)
        self.graph_manager.add(pro_uuid, pro_methods_list, static_attributes, offset=offset)

    def read_global_variables(self):
        self.graph_manager = GraphManager(load_graph=self.load_graph,
                                          save_graph=self.save_graph,
                                          configure=global_config.CONFIGURATION.get('graph'))

    def __record_process__(self, uuids):
        d_insert = data_inserter.DataInserter(authentication=self.data_executor.get_authentication())
        return d_insert.__insert_analyzed_graph_uuid__(g_dis.g_distributor.master.hashcode, uuids)
