from src.db_manager import DBManager
import sqlite3
import os
import requests
import json
from datetime import datetime
from src.tcg_api import TCGAPI

class PokemonManager:
    def __init__(self):
        self.db = DBManager()
        self.tcg_api = TCGAPI()
    
    def add_trainer(self, name):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO trainers (name) VALUES (?)", (name,))
            conn.commit()
            return cursor.lastrowid
    
    def get_trainer(self, trainer_id=None, name=None):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            if trainer_id:
                cursor.execute("SELECT * FROM trainers WHERE id = ?", (trainer_id,))
            elif name:
                cursor.execute("SELECT * FROM trainers WHERE name = ?", (name,))
            else:
                return None
            
            row = cursor.fetchone()
            if row:
                return {'id': row[0], 'name': row[1]}
            return None
    
    def get_all_trainers(self):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM trainers")
            return [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
    
    def add_route(self, name):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO routes (name) VALUES (?)", (name,))
            conn.commit()
            return cursor.lastrowid
    
    def get_route(self, route_id=None, name=None):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            if route_id:
                cursor.execute("SELECT * FROM routes WHERE id = ?", (route_id,))
            elif name:
                cursor.execute("SELECT * FROM routes WHERE name = ?", (name,))
            else:
                return None
            
            row = cursor.fetchone()
            if row:
                return {'id': row[0], 'name': row[1], 'status': row[2]}
            return None
    
    def get_all_routes(self):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM routes")
            return [{'id': row[0], 'name': row[1], 'status': row[2]} for row in cursor.fetchall()]
    
    def close_route(self, route_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE routes SET status = 'closed' WHERE id = ?", (route_id,))
            conn.commit()
    
    def add_pokemon(self, name, route_id, trainer_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO pokemon (name, route_id, trainer_id) VALUES (?, ?, ?)",
                (name, route_id, trainer_id)
            )
            conn.commit()
            return cursor.lastrowid
    
    def get_pokemon(self, pokemon_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pokemon WHERE id = ?", (pokemon_id,))
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0], 
                    'name': row[1], 
                    'route_id': row[2], 
                    'trainer_id': row[3], 
                    'status': row[4]
                }
            return None
    
    def get_pokemon_by_route(self, route_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.*, t.name as trainer_name 
                FROM pokemon p 
                JOIN trainers t ON p.trainer_id = t.id 
                WHERE p.route_id = ?
            """, (route_id,))
            return [{
                'id': row[0], 
                'name': row[1], 
                'route_id': row[2], 
                'trainer_id': row[3], 
                'status': row[4],
                'trainer_name': row[5]
            } for row in cursor.fetchall()]
    
    def mark_pokemon_as_dead(self, pokemon_id):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Finde die Route des Pokémon
            cursor.execute("SELECT route_id FROM pokemon WHERE id = ?", (pokemon_id,))
            route_result = cursor.fetchone()
            
            if not route_result:
                return False
                
            route_id = route_result[0]
            
            # Markiere alle Pokémon auf dieser Route als tot
            cursor.execute("UPDATE pokemon SET status = 'dead' WHERE route_id = ?", (route_id,))
            
            # Schließe die Route
            cursor.execute("UPDATE routes SET status = 'closed' WHERE id = ?", (route_id,))
            
            conn.commit()
            return True
    
    def get_all_pokemon(self):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.*, t.name as trainer_name, r.name as route_name
                FROM pokemon p 
                JOIN trainers t ON p.trainer_id = t.id 
                JOIN routes r ON p.route_id = r.id
                ORDER BY r.name, t.name
            """)
            return [{
                'id': row[0], 
                'name': row[1], 
                'route_id': row[2], 
                'trainer_id': row[3], 
                'status': row[4],
                'trainer_name': row[5],
                'route_name': row[6]
            } for row in cursor.fetchall()]
        
    def is_pokemon_available(self, pokemon_name):
        """Prüft ob ein Pokémon bereits gefangen wurde"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM pokemon WHERE LOWER(name) = LOWER(?)", (pokemon_name,))
            return cursor.fetchone() is None

    def get_all_pokemon_names(self):
        """Gibt alle bereits gefangenen Pokémon-Namen zurück"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM pokemon")
            return [row[0] for row in cursor.fetchall()]
        
    def add_banned_pokemon(self, pokemon_name, reason="already caught"):
        """Fügt ein Pokémon zur Liste der verbotenen Pokémon hinzu"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO banned_pokemon (pokemon_name, reason) VALUES (?, ?)",
                    (pokemon_name, reason)
                )
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                # Pokémon ist bereits in der Liste
                return False
    
    def is_pokemon_banned(self, pokemon_name):
        """Prüft ob ein Pokémon verboten ist"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM banned_pokemon WHERE pokemon_name = ?", (pokemon_name,))
            return cursor.fetchone() is not None
    
    def get_all_banned_pokemon(self):
        """Gibt alle verbotenen Pokémon zurück"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM banned_pokemon")
            return [{'id': row[0], 'pokemon_name': row[1], 'reason': row[2]} for row in cursor.fetchall()]
    
    def set_active_pokemon(self, pokemon_id, trainer_id):
        """Setzt ein Pokémon als aktiv für einen Trainer"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Deaktiviere alle anderen aktiven Pokémon des Trainers
            cursor.execute(
                "UPDATE active_pokemon SET is_active = 0 WHERE trainer_id = ?",
                (trainer_id,)
            )
            
            # Setze das neue Pokémon als aktiv
            cursor.execute(
                "INSERT OR REPLACE INTO active_pokemon (pokemon_id, trainer_id, is_active) VALUES (?, ?, 1)",
                (pokemon_id, trainer_id)
            )
            
            conn.commit()
    
    def get_active_pokemon(self, trainer_id):
        """Gibt das aktive Pokémon eines Trainers zurück"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.* 
                FROM pokemon p
                JOIN active_pokemon ap ON p.id = ap.pokemon_id
                WHERE ap.trainer_id = ? AND ap.is_active = 1
            """, (trainer_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0], 
                    'name': row[1], 
                    'route_id': row[2], 
                    'trainer_id': row[3], 
                    'status': row[4]
                }
            return None
    
    def get_pokemon_data_from_api(self, pokemon_name):
        """Holt Daten von der PokeAPI für ein Pokémon"""
        try:
            response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}")
            if response.status_code == 200:
                data = response.json()
                return {
                    'name': data['name'],
                    'id': data['id'],
                    'sprite': data['sprites']['front_default'],
                    'types': [t['type']['name'] for t in data['types']],
                    'height': data['height'],
                    'weight': data['weight']
                }
            return None
        except:
            return None
    
    def get_evolution_chain(self, pokemon_name):
        """Holt die Evolutionskette für ein Pokémon"""
        try:
            # Zuerst Pokémon-Daten holen
            pokemon_data = self.get_pokemon_data_from_api(pokemon_name)
            if not pokemon_data:
                return None
            
            # Species-URL holen
            species_url = f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_data['id']}/"
            species_response = requests.get(species_url)
            
            if species_response.status_code != 200:
                return None
            
            species_data = species_response.json()
            evolution_chain_url = species_data['evolution_chain']['url']
            
            # Evolutionskette holen
            evolution_response = requests.get(evolution_chain_url)
            if evolution_response.status_code != 200:
                return None
            
            evolution_data = evolution_response.json()
            return self._parse_evolution_chain(evolution_data['chain'])
        except:
            return None
    
    def _parse_evolution_chain(self, chain):
        """Hilfsfunktion zum Parsen der Evolutionskette"""
        result = {
            'species': chain['species']['name'],
            'evolves_to': []
        }
        
        for evolution in chain['evolves_to']:
            result['evolves_to'].append(self._parse_evolution_chain(evolution))
        
        return result
    
    def get_banned_evolutions(self, pokemon_name):
        """Gibt alle Evolutionen zurück, die durch ein gefangenes Pokémon gesperrt sind"""
        evolution_chain = self.get_evolution_chain(pokemon_name)
        if not evolution_chain:
            return []
        
        # Sammle alle Pokémon in der Evolutionskette
        all_evolutions = []
        queue = [evolution_chain]
        
        while queue:
            current = queue.pop(0)
            all_evolutions.append(current['species'])
            queue.extend(current['evolves_to'])
        
        return all_evolutions
    
    def reset_game(self, player_names):
        """Setzt das Spiel zurück und erstellt neue Spieler"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Lösche alle Tabelleninhalte
            cursor.execute("DELETE FROM pokemon")
            cursor.execute("DELETE FROM routes")
            cursor.execute("DELETE FROM trainers")
            cursor.execute("DELETE FROM banned_pokemon")
            cursor.execute("DELETE FROM active_pokemon")
            
            # Füge neue Spieler hinzu
            for i, name in enumerate(player_names):
                cursor.execute("INSERT INTO trainers (name) VALUES (?)", (name,))
            
            conn.commit()

    def get_pokemon_card_info(self, pokemon_name):
        """Holt Karteninformationen für ein Pokémon"""
        return self.tcg_api.get_pokemon_card(pokemon_name)
    
    def get_pokemon_card_image_url(self, pokemon_name):
        """Gibt die URL des Pokémon-Kartenbildes zurück"""
        card = self.get_pokemon_card_info(pokemon_name)
        if card:
            return self.tcg_api.get_card_image_url(card)
        return None
    
    def get_pokemon_card_image_base64(self, pokemon_name):
        """Gibt das Pokémon-Kartenbild als Base64-String zurück"""
        card = self.get_pokemon_card_info(pokemon_name)
        if card:
            return self.tcg_api.get_card_image_base64(card)
        return None