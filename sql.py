import sqlite3
from sqlite3 import Error, Connection
import log


def create_connection(db_file: str) -> Connection:
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        log.error(f'{e}')


def create_table(conn, create_table_request) -> None:
    if conn is None:
        return log.error(f"Can't create the DB connection")

    try:
        c = conn.cursor()
        c.execute(create_table_request)
    except Error as e:
        log.error(f'{e}')


def create_history_table(conn) -> None:
    sql = """CREATE TABLE IF NOT EXISTS history_table (
             chat_id text NOT NULL,
             history blob,
             UNIQUE(chat_id)
             );"""
    create_table(conn, sql)


def insert_history(conn, chat_id: str, history: bytes):
    sql = f"""INSERT INTO history_table(chat_id, history)
              VALUES(?, ?)"""
    cur = conn.cursor()
    cur.execute(sql, (chat_id, history))
    conn.commit()
    return cur.lastrowid


def get_history(conn, chat_id: str) -> bytes|None:
    sql = f"SELECT history FROM history_table WHERE chat_id= ?"
    cur = conn.cursor()
    cur.execute(sql, (chat_id,))
    rows = cur.fetchall()
    if len(rows) == 0:
        return None
    return rows[0][0]


def update_history(conn, chat_id: str, history: bytes) -> None:
    sql = f"""UPDATE history_table SET history = ? WHERE chat_id = ?"""
    cur = conn.cursor()
    cur.execute(sql,(history, chat_id))
    conn.commit()


def delete_history(conn, chat_id: str) -> None:
    sql = f"""DELETE FROM history_table WHERE chat_id = ?"""
    cur = conn.cursor()
    cur.execute(sql, (chat_id,))
    conn.commit()


def history_exists(conn, chat_id: str) -> bool:
    result = get_history(conn, chat_id)
    if result is not None:
        return True
    return False


if __name__=='__main__':
    pass