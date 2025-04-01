import sql
from settings import  DB_PATH
import pickle


class HistoryEntry:
    def __init__(self, chat_id: str, history: list):
        self.chat_id = chat_id
        self.history: list = history

    def update_history(self, history: list):
        self.history: list = history

    def save(self):
        conn = sql.create_connection(DB_PATH)        
        pickled_history = pickle.dumps(self.history)

        if sql.history_exists(conn, self.chat_id):
            sql.update_history(conn, self.chat_id, pickled_history)
        else:
            sql.insert_history(conn, self.chat_id, pickled_history)


class HistoryManager:
    def __init__(self):
        self.init_db_table()

    def entry_exists(self, chat_id: str):
        if self.get_history(chat_id) is not None:
            return True
        return False

    def get_history(self, chat_id: str) -> list | None:
        conn = sql.create_connection(DB_PATH)
        pickled_history = sql.get_history(conn, chat_id)
        if pickled_history is not None:
            history = pickle.loads(pickled_history)
            return history
        return None
    
    @staticmethod
    def delete_history_for_chat_id(chat_id: str):
        conn = sql.create_connection(DB_PATH)
        sql.delete_history(conn, chat_id)

    @staticmethod
    def init_db_table():
        conn = sql.create_connection(DB_PATH)
        sql.create_history_table(conn)


if __name__ == '__main__':
    hm = HistoryManager()
    he1 = HistoryEntry('11111', [1, 2, 3, 4])
    he2 = HistoryEntry('22222', [1, 2, 3, 4])
    he3 = HistoryEntry('33333', [1, 2, 3, 4])
