import os
from time import time
import pandas as pd
from sqlalchemy import create_engine
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class AbstractDataSource:
    def __int__(self):
        pass


class AbstractDataSourcePointer(AbstractDataSource):
    def __int__(self):
        super(AbstractDataSourcePointer, self).__int__()

    def identify_pointer(self):
        pass


class DataSourceGenerator:
    def __init__(self, engine, offset=0, limit=10000, chunks=None):
        self.engine = engine
        self.offset = offset
        self.limit = limit
        self.chunks = chunks

    def __iter__(self):
        return self

    def __next__(self):
        start = time()
        sql = """select id, content from test_result_log offset %s limit %s""" % (self.offset, self.limit)
        data = pd.read_sql(sql, con=self.engine)
        logger.info('--- Querying data offset {} to {} within {}'.format(self.offset * self.limit,
                                                                         (self.offset + 1) * self.limit,
                                                                         time() - start))
        self.offset += self.limit
        yield data


class PostgresDBSourcePointer(AbstractDataSourcePointer):
    def __int__(self):
        self.host = os.getenv('KI_HOST')
        self.port = os.getenv('KI_PORT')
        self.db = os.getenv('KI_KITDB')
        self.user = os.getenv('KI_USER')
        self.password = os.getenv('KI_PASSWORD')
        self.chunksize = 10000

    def identify_pointer(self):
        logger.info('Estimating...')
        engine = create_engine('postgres://{}:{}@{}:{}/{}'.format(self.user, self.password,
                                                                  self.host, self.port, self.db))
        sql = """select count(*) from test_result_log """
        total_records = pd.read_sql(sql, con=engine)['count'][0]
        chunks = (total_records // self.chunksize) + 1
        logger.info('Estimate - Total records {} - Total chunks {} - '.format(total_records, chunks))
        generator = DataSourceGenerator(engine=engine, limit=self.chunksize, chunks=chunks)
        return generator


class DataSource:
    def __int__(self, pointer):
        self.pointer = pointer
        self._check_variable_types_()

    def _check_variable_types_(self):
        assert isinstance(self.pointer, AbstractDataSourcePointer), "Pointer must be instance of " \
                                                                    "AbstractDataSourcePointer"
