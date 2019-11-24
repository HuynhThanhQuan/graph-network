import os
from datetime import datetime
import pandas as pd
from graph.exception import graph_exception
from graph.core import graph_manager as gm
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GraphVersionHistory:
    RECORD_COLUMNS = ['uuid', 'timestamp', 'order', 'path', 'initial', 'successor', 'predecessor', 'activate']

    def __init__(self, storage_location, maximum_version=10):
        logger.info('Reading Graph Version History')
        self.storage_location = storage_location
        self.maximum_version = maximum_version
        self.history = []
        self.uuid_version_map = {}
        self.attempts = 0
        self.record_history = None
        self.record_history_path = None
        self.__read_graph_version_history_metadata__()

    def __validate_storage_location__(self):
        # Check number of attempts to re-configure Graph Storage
        if self.attempts >= 3:
            logger.error('Reach maximum number of attempt to configure Graph Storage')
            raise graph_exception.GraphStorageExceedMaximumAttemps()

        # Check validation of Storage base folder name convention
        folder_name = os.path.basename(self.storage_location)
        if folder_name != 'graph_storage':
            logger.error('Invalid graph storage location')
            raise graph_exception.GraphStorageInvalidLocation()

        # Check existing Storage, if not try to make directoy and re-configure, if yes then read its content
        if os.path.exists(self.storage_location) is False:
            logger.warning('Invalid Graph Storage location, automatic generate Graph Storage')
            try:
                os.makedirs(self.storage_location)
                self.attempts += 1
                self.__validate_storage_location__()
            except OSError as e:
                logger.error('Unable to generate Graph storage automatically')
                logger.error(e.args[0])
                raise graph_exception.GraphStorageUnableInitialize()
        else:
            self.__read_history__()

    def __read_history__(self):
        # Read or init record files
        self.record_history_path = os.path.join(self.storage_location, 'record_history.csv')
        if os.path.exists(self.record_history_path) is False:
            record_df = pd.DataFrame(columns=GraphVersionHistory.RECORD_COLUMNS)
            record_df.to_csv(self.record_history_path)
        self.record_history = pd.read_csv(self.record_history_path, usecols=GraphVersionHistory.RECORD_COLUMNS)
        self.record_history = self.record_history.sort_values(by=['order'])
        # Read data file to history
        for idx, record in self.record_history.iterrows():
            graph_version = GraphVersion(None)
            graph_version.uuid = record['uuid']
            graph_version.timestamp = record['timestamp']
            graph_version.successor = record['successor']
            graph_version.predecessor = record['predecessor']
            graph_version.initial_version = record['initial']
            graph_version.activate = record['activate']
            graph_version.path = record['path']
            graph_version.order = record['order']
            self.history.append(graph_version)
            self.uuid_version_map[graph_version.uuid] = graph_version

    def __read_graph_version_history_metadata__(self):
        self.__validate_storage_location__()

    def __trace_diff__(self):
        # TODO: Find difference between 2 graph versions
        pass

    def __trace_link_history__(self, graph_version):
        if len(self.history) >= 2:
            graph_version.predecessor = self.history[-2].uuid
            self.history[-2].successor = graph_version.uuid

    def __trace__(self, graph_version):
        self.history.append(graph_version)
        self.uuid_version_map[graph_version.uuid] = graph_version
        self.__trace_link_history__(graph_version)
        self.__trace_diff__()

    def register(self, graph_manager):
        self.__check_storage_capability__()
        total_version = len(self.history)
        graph_version = GraphVersion(graph_manager)
        graph_version.initial_version = True if total_version == 0 else False
        graph_version.order = total_version
        graph_version.timestamp = datetime.now()
        graph_version.uuid = gm.GraphUtil.__hash_md5__("{} | {}".
                                                       format(graph_version.order,
                                                              graph_version.timestamp.strftime("%Y-%m-%d %H:%M:%S")))
        graph_version.path = os.path.join(self.storage_location, '{}'.format(graph_version.uuid))
        self.__trace__(graph_version)
        # self.__add_record__(graph_version)
        self.__update_record__()
        return graph_version

    def activate(self, uuid=None, order=None):
        assert uuid is not None or order is not None
        graph_version = self.uuid_version_map[uuid] if uuid is not None else self.history[order]
        # TODO: dis-activate other graph version
        graph_version.activate = True
        self.__update_record__()
        return graph_version

    def active_latest_version(self):
        if len(self.history) > 0:
            graph = self.activate(order=-1)
            logger.info('Auto retrieve pretrained Graph: {}'.format(graph.uuid))
            return graph
        else:
            logger.info('Not found pretrained Graph, preparing initializing new Graph')
            return None

    def __update_record__(self):
        self.record_history = pd.DataFrame(columns=GraphVersionHistory.RECORD_COLUMNS)
        for graph_version in self.history:
            record = pd.DataFrame({'uuid': graph_version.uuid,
                                   'timestamp': graph_version.timestamp,
                                   'order': graph_version.order,
                                   'path': graph_version.path,
                                   'initial': graph_version.initial_version,
                                   'successor': graph_version.successor,
                                   'predecessor': graph_version.predecessor,
                                   'activate': graph_version.activate}, index=[0])
            self.record_history = self.record_history.append(record, ignore_index=True, sort=False)
        self.record_history.to_csv(self.record_history_path)

    def __check_storage_capability__(self):
        graph_version_history = os.listdir(self.storage_location)
        total_version = len(graph_version_history) - 1
        leftover = self.maximum_version - total_version
        if leftover < 5:
            if leftover > 0:
                logger.warning('Graph Version History is nearly full capacity')
                logger.warning('Consider to move them into other storage')
                logger.warning('Leftover capacity: {}'.format(leftover))
            else:
                logger.warning('Graph Version History is full capacity')
                logger.warning('Automatic delete the oldest version')
                # Remove oldest version automatically
                try:
                    os.remove(os.path.join(self.storage_location, graph_version_history[0]))
                except OSError as e:
                    logger.error('Unable to delete old Graph Version file')
                    logger.error(e.args[0])
                    logger.warning('Please contact administrator for support')
                    raise graph_exception.GraphStorageErrorDeletingGraphVersion()


class GraphVersion:
    def __init__(self, graph_manager):
        self.uuid = None
        self.graph_manager = graph_manager
        self.path = None
        self.successor = None
        self.predecessor = None
        self.initial_version = False
        self.data = None
        self.order = None
        self.activate = False
        self.timestamp = None
