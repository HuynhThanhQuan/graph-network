from database.database_connection import DatabaseConnection
import psycopg2 as ps
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DataInserter(DatabaseConnection):
    def __init__(self, **kwargs):
        super(DataInserter, self).__init__(**kwargs)

    def insert_value(self, sql):
        try:
            conn = ps.connect(host=self.host,
                              port=self.port,
                              database=self.name,
                              user=self.user,
                              password=self.password)
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except (Exception, ps.Error) as e:
            logger.error('Failed to execute SQL', e.args[0])
            return False
        finally:
            if conn is not None:
                cursor.close()
                conn.close()
            return True

    def __update_analyzed_graph_uuid__(self, hashcode_analysis, uuids):
        sql = """UPDATE test_result_log_hashcode_analysis SET hashcode_analysis = %s WHERE id = %s"""
        records = [(hashcode_analysis, uuid) for uuid in uuids]
        try:
            conn = ps.connect(host=self.host,
                              port=self.port,
                              database=self.name,
                              user=self.user,
                              password=self.password)
            cursor = conn.cursor()
            cursor.executemany(sql, records)
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except (Exception, ps.Error) as e:
            logger.error('Failed to execute SQL __update_analyzed_graph_uuid__', e.args[0])
            return False
        finally:
            if conn is not None:
                cursor.close()
                conn.close()
            return True

    def __insert_analyzed_graph_uuid__(self, hashcode_analysis, uuids):
        sql = """INSERT INTO test_result_log_hashcode_analysis(id, hashcode_analysis) VALUES (%s, %s)"""
        records = [(uuid, hashcode_analysis) for uuid in uuids]
        try:
            conn = ps.connect(host=self.host,
                              port=self.port,
                              database=self.name,
                              user=self.user,
                              password=self.password)
            cursor = conn.cursor()
            cursor.executemany(sql, records)
            conn.commit()
            cursor.close()
            conn.close()
            logger.info('Recorded analyzed test result log Ids')
            return True
        except (Exception, ps.Error) as e:
            logger.error('Failed to execute SQL __insert_analyzed_graph_uuid__', e.args[0])
            return False
        finally:
            if conn is not None:
                cursor.close()
                conn.close()
            return True
