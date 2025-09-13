from flask import Flask
from src.routes import init_routes
from src.db_manager import DBManager
from src.logic import PokemonManager
from dotenv import load_dotenv
import os

load_dotenv()  # Laden der Umgebungsvariablen aus der .env-Datei

def create_app():
    # Pfad zu den Templates im webapp-Ordner
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(base_dir, 'webapp', 'templates')
    static_dir = os.path.join(base_dir, 'webapp', 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    
    # Secret Key für Session-Management
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "fallback_dev_key")

    # Datenbank initialisieren
    db_manager = DBManager()
    pm = PokemonManager()
    
    # Standard-Trainer erstellen, falls nicht vorhanden
    if not pm.get_all_trainers():
        pm.add_trainer("Player1")
        pm.add_trainer("Player2")
        pm.add_trainer("Player3")
        print("Standard-Trainer erstellt: Player1, Player2, Player3")
    
    # Routen initialisieren
    init_routes(app, pm)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)