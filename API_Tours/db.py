import MySQLdb
from MySQLdb.cursors import DictCursor

def get_db_connection(config):
    return MySQLdb.connect(
        host=config.MYSQL_HOST,
        user=config.MYSQL_USER,
        passwd=config.MYSQL_PASSWORD,
        db=config.MYSQL_DB,
        port=config.MYSQL_PORT,
        cursorclass=DictCursor
    )