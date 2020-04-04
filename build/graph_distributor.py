import uuid
import pickle
from graph.exception import graph_exception as g_exc
import logging
import os
import psutil
import configparser
import hashlib
from graph.build import graph_configure as g_conf
from time import time
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


g_distributor = None


class GraphDistributor:

    class Master:
        def __init__(self, hashcode, directory, keep_work=False):
            self.hashcode = hashcode
            self.directory = directory
            self.is_alive = True
            self.zero_fault_tolerance = True
            self.num_slaves = 0
            self.config_file_path = os.path.join(self.directory, 'master.ini')
            if keep_work is False:
                self.init_INI_config()
            else:
                self.read_INI_config()

        def init_INI_config(self):
            config = configparser.ConfigParser(allow_no_value=True)
            config['MASTER'] = {'DirectoryPath': self.directory}
            config['SLAVE'] = {}
            with open(self.config_file_path, 'w') as config_file:
                config.write(config_file)

        def read_INI_config(self):
            config = configparser.ConfigParser(allow_no_value=True)
            config.read(self.config_file_path)

        def register_slave(self, slave):
            self.num_slaves += 1
            config = configparser.ConfigParser(allow_no_value=True)
            config.read(self.config_file_path)
            slaves = config['SLAVE']
            slaves[slave] = slave
            with open(self.config_file_path, 'w') as config_file:
                config.write(config_file)

    def __init__(self):
        self.directory = g_conf.GraphEnvVar.DISTRIBUTED_LOCATION
        self.master = None

    def init_clusters(self):
        # Define master
        timestamp = time()
        _uuid = uuid.uuid4()
        master_hashcode = hashlib.sha256('{}-{}'.format(_uuid, timestamp).encode('utf-8')).hexdigest()
        try:
            master_path = os.path.join(self.directory, master_hashcode)
            if not os.path.exists(master_path):
                os.mkdir(master_path)
            self.master = GraphDistributor.Master(master_hashcode, master_path)
            logger.info('Distributed Mechanism is initialized by default')
            logger.info('Master Node {} is created'.format(master_hashcode))
            logger.info('Master INI config is stored at {}'.format(master_path))
        except Exception:
            raise g_exc.GraphDistributorInitMasterFailed()

    def continue_working_clusters(self, hashcode_analysis):
        # Continue track master cluster
        master_hashcode = hashcode_analysis
        try:
            master_path = os.path.join(self.directory, master_hashcode)
            if not os.path.exists(master_path):
                os.mkdir(master_path)
            self.master = GraphDistributor.Master(master_hashcode, master_path, keep_work=True)
            logger.info('Distributed Mechanism is initialized by default')
            logger.info('Continue building Graph with Master Node {}'.format(master_hashcode))
        except Exception:
            raise g_exc.GraphDistributorInitMasterFailed()

    def register_slave(self, slave):
        timestamp = time()
        _uuid = uuid.uuid4()
        slave_hashcode = hashlib.sha256('{}-{}'.format(_uuid, timestamp).encode('utf-8')).hexdigest()
        self.master.register_slave(slave_hashcode)
        slave_path = os.path.join(self.master.directory, slave_hashcode)
        pickle.dump(slave, open(slave_path, 'wb'))
        logger.info('Registered distributed graph {} - node size {} to '
                    'Master node'.format(slave_hashcode, slave.get_total_node_pool()))

    def __check_master_alive__(self):
        if self.master is not None:
            return self.master.is_alive
        return False

    def __check_master_working_properly__(self):
        if not self.__check_master_alive__():
            return False
        if not os.path.exists(self.master.directory):
            return False
        if not os.path.exists(self.master.config_file_path):
            return False

        # Read and check master content
        config = configparser.ConfigParser(allow_no_value=True)
        config.read(self.master.config_file_path)
        try:
            slaves = config['SLAVE']
            for slave_hashcode in slaves:
                if not os.path.exists(os.path.join(self.master.directory, slave_hashcode)):
                    return False
        except KeyError:
            logger.error(g_exc.GraphDistributorSlaveSectionNotDefined().args[0])
            return False
        return True


def monitor(graph_man):
    print('[MONITORING] Graph nodes: {}'.format(graph_man.get_total_node_pool()))
    print('[MONITORING] CPU Stats: {}'.format(psutil.cpu_stats()))
    print('[MONITORING] CPU Frequency: {}'.format(psutil.cpu_freq()))
    print('[MONITORING] Virtual Memory: {}'.format(psutil.virtual_memory()))
    print('[MONITORING] Swap Memory: {}'.format(psutil.swap_memory()))
    print('[MONITORING] Disk Usage: {}'.format(psutil.disk_usage('/')))
    # print('[MONITORING] Network connections: {}'.format(psutil.net_connections()))


def unload_data(graph_man):
    global g_distributor
    if g_distributor is not None:
        if psutil.virtual_memory().percent >= 70:
            logger.info('Graph is distributed to ensure the overloaded memory of machine')
            g_distributor.register_slave(graph_man)


def distribute(graph_man):
    monitor(graph_man)
    unload_data(graph_man)


def init_distributed_clusters():
    global g_distributor
    g_distributor = GraphDistributor()
    g_distributor.init_clusters()


def continue_distributed_clusters(hashcode_analysis):
    global g_distributor
    g_distributor = GraphDistributor()
    g_distributor.continue_working_clusters(hashcode_analysis)
