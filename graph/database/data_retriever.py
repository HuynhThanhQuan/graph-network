from sqlalchemy import create_engine
import pandas as pd
from datetime import datetime
import logging
from database import database_exception as db_exc
from graph.build import graph_configure as g_conf
from database.database_connection import DatabaseConnection
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ATTRIBUTES = ['project_id', 'tokenization', 'flakiness']
ID_COLS = {'uuid', 'error_stack_trace_id', 'error_details_id', 'execution_id', 'id'}


class DataRetriever(DatabaseConnection):
    def __init__(self, **kwargs):
        super(DataRetriever, self).__init__(**kwargs)

    @staticmethod
    def get_only_necessary_data(data):
        cols = set(list(data.columns))
        id_cols = list(ID_COLS & cols)
        data['uuid'] = data[id_cols[0]] if len(id_cols) > 0 else list(range(len(data)))

        # exist_cols = set(list(data.columns)) & set(ATTRIBUTES)
        # attributes = data[exist_cols].to_dict('records') if len(list(exist_cols)) > 0 else None
        data = data[['uuid', 'content']].dropna()
        uuids = data['uuid'].tolist()
        contents = data['content'].tolist()

        return uuids, contents, None

    @staticmethod
    def read_local(path):
        start = datetime.now()
        data = pd.read_csv(path)
        logger.info("Read {} records from local {} - {}".format(len(data), path, datetime.now() - start))
        return DataRetriever.get_only_necessary_data(data)

    @staticmethod
    def read_big_data_local(path, chunksize=10000):
        logger.info("Prepare reading data from local {}".format(path))
        generator = pd.read_csv(path, chunksize=chunksize, iterator=True)
        return generator

    def query(self, sql, message=None):
        start = datetime.now()
        engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(self.user,
                                                                    self.password,
                                                                    self.host,
                                                                    self.port,
                                                                    self.name))
        df = pd.read_sql(sql, con=engine)
        logger.info("Queried {} records '{}' - {}".format(len(df), message, datetime.now() - start))
        return df

    def query_project_id(self, project_id=22981):
        sql = """select def.test_result_id as uuid, trl.content as content, def.* from test_result_log trl inner join 
        (select * from test_result_stack_trace trst inner join (select etr.id, etr.start_time 
        from execution_test_result etr inner join 
        (select id from execution where project_id = %s) exe on etr.execution_id = exe.id) abc 
        on trst.test_result_id = abc.id order by start_time desc) def on trl.id = def.test_result_log_id""" % project_id
        data = self.query(sql, message="query_project_id")
        return DataRetriever.get_only_necessary_data(data)

    def query_random_stacktrace(self, number=1000):
        sql = """select trl.id as uuid, trl.content as content, etr.* from test_result_log trl inner join 
        (select * from execution_test_result where error_stack_trace_id is not null limit %s) etr 
        on trl.id = etr.error_stack_trace_id""" % number
        data = self.query(sql, message="query_random_stacktrace")
        return DataRetriever.get_only_necessary_data(data)

    def execute(self):
        global_request = self.data_config.get('global', False)
        if global_request is False:
            path = self.data_config.get('path')
            if path is not None:
                generator = self.read_big_data_local(path, self.data_config.get('chunksize', 5000))
                return generator
        else:
            return self.__query_generator_global_db__()
        return None

    def __query_generator_global_db__(self):
        mode = self.data_config.get('mode')
        hashcode_analysis = self.data_config.get('hashcode_analysis')
        chunksize = int(self.data_config.get('chunksize', 10000))

        # Estimate total pages
        logger.info('Estimating...')
        engine = create_engine('postgres://{}:{}@{}:{}/{}'.format(self.user, self.password,
                                                                  self.host, self.port, self.name))
        sql = """select count(*) from test_result_log """
        total_records = pd.read_sql(sql, con=engine)['count'][0]
        pages = (total_records // chunksize) + 1
        logger.info('Estimate - Total records {} - Total pages {} - '.format(total_records, pages))

        # Return generator of each page
        if mode is None:
            g_conf.GraphEnvVar.init_graph_distributed()
            for page in range(pages):
                start = datetime.now()
                engine = create_engine('postgres://{}:{}@{}:{}/{}'.format(self.user, self.password,
                                                                          self.host, self.port, self.name))
                current_paging = page * chunksize
                page_sql = """SELECT id, content FROM test_result_log OFFSET %s LIMIT %s""" % (current_paging,
                                                                                               chunksize)
                data = pd.read_sql(page_sql, con=engine)
                logger.info('--- Querying data offset {} to {} within {}'.format(current_paging,
                                                                                 current_paging + chunksize,
                                                                                 datetime.now() - start))
                yield data
        elif mode == 'continue':
            if hashcode_analysis is not None:
                g_conf.GraphEnvVar.continue_build_graph_distributed_with_hashcode(hashcode_analysis)
                for page in range(pages):
                    start = datetime.now()
                    engine = create_engine('postgres://{}:{}@{}:{}/{}'.format(self.user, self.password,
                                                                              self.host, self.port, self.name))
                    current_paging = page * chunksize
                    page_sql = """SELECT * FROM test_result_log WHERE id NOT IN 
                    (SELECT id FROM test_result_log_hashcode_analysis WHERE hashcode_analysis NOT LIKE '%s') 
                    ORDER BY id ASC OFFSET %s LIMIT %s""" % (hashcode_analysis, current_paging, chunksize)
                    data = pd.read_sql(page_sql, con=engine)
                    logger.info('--- Querying data offset {} to {} within {}'.format(current_paging,
                                                                                     current_paging + chunksize,
                                                                                     datetime.now() - start))
                    yield data
            else:
                raise db_exc.DatabasePassingNullValueException()
        else:
            # TODO: overlapped mode
            pass

    def get_authentication(self):
        return self
