import sqlite3
import os

class DBManager:
    def __init__(self, db_path='data/pokemon_manager.db'):
        # Pfade absolut setzen
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(current_dir, '..', db_path)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()
    
    def init_db(self):
        # Lese das Schema und initialisiere die Datenbank
        current_dir = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(current_dir, '..', 'database', 'schema.sql')
        
        with sqlite3.connect(self.db_path) as conn:
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            conn.executescript(schema_sql)
            conn.commit()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)