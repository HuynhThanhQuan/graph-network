import os
import configparser
from graph.build import graph_configure
from bigdata.build import bigdata_configure
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

GLOBAL_INIT = os.path.abspath(os.path.join(os.path.dirname(__file__), 'global.ini'))
CONFIGURATION = {}
config = configparser.ConfigParser(allow_no_value=True)


def init():
    global config
    try:
        config.read(GLOBAL_INIT)
        print('=====GLOBAL CONFIG=====')
        for section in config.sections():
            print("[%s]" % section)
            for options in config.options(section):
                print("%s=%s" % (options, config.get(section, options)))
            print()
        print('=======================')
        print('Connected to Server "{}" - port "{}" - database "{}"'.format(os.environ.get('KI_HOST'),
                                                                            os.environ.get('KI_PORT'),
                                                                            os.environ.get('KI_KITDB')))
        init_graph_config(config)
        init_bigdata_config(config)
    except Exception as e:
        print('Exception occured')
        print(e.args[0])
        print('Error while setting global variables')
        print('All settings will be set default by its instance')
        print('Please contact adminstrator for settings')


def init_graph_config(graph_conf):
    graph_configure.GraphEnvVar(dict(graph_conf['graph']))
    CONFIGURATION['graph'] = graph_configure.GraphConfigMechanism(
        storage_location=graph_conf.get('graph', 'storage_location'),
        load_graph=bool(graph_conf.get('graph', 'load_graph')),
        save_graph=bool(graph_conf.get('graph', 'save_graph')))


def init_bigdata_config(bigdata_conf):
    bigdata_configure.BigDataEnvVar(dict(bigdata_conf['bigdata']))
