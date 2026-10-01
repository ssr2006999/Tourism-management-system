from mysql.connector import connect
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB


def get_db():
    return connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )


def query_db(query, params=None, fetch=False):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        if fetch:
            result = cursor.fetchall()
        else:
            result = cursor.lastrowid
        conn.commit()
        return result
    finally:
        cursor.close()
        conn.close()