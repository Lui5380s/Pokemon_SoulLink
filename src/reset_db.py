import os
import sqlite3

def reset_database():
    # Pfade definieren
    db_path = 'data/pokemon_manager.db'
    schema_path = 'database/schema.sql'
    
    # Datenbankdatei löschen, falls vorhanden
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Datenbank gelöscht.")
    
    # Verzeichnis für Datenbank erstellen, falls nicht vorhanden
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Neue Datenbank mit aktuellem Schema erstellen
    with sqlite3.connect(db_path) as conn:
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        conn.executescript(schema_sql)
        conn.commit()
    
    print("Datenbank wurde zurückgesetzt und mit aktuellem Schema neu erstellt.")

if __name__ == "__main__":
    reset_database()