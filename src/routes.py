from flask import render_template, request, jsonify, redirect, url_for, flash, session
import json
from src.tcg_api import TCGAPI

# TCG-API initialisieren
tcg_api = TCGAPI()

def init_routes(app, pm):
    @app.route('/')
    def index():
        routes = pm.get_all_routes()
        pokemon_list = pm.get_all_pokemon()
        trainers = pm.get_all_trainers()
        active_pokemon = {}
        
        for trainer in trainers:
            active_pokemon[trainer['id']] = pm.get_active_pokemon(trainer['id'])
        
        return render_template('index.html', 
                             routes=routes, 
                             pokemon_list=pokemon_list,
                             trainers=trainers,
                             active_pokemon=active_pokemon)
    
    @app.route('/new_encounter', methods=['GET', 'POST'])
    def new_encounter():
        if request.method == 'POST':
            route_name = request.form.get('route_name')
            encounters = []
            
            for i in range(3):
                trainer_id = request.form.get(f'trainer_{i}')
                pokemon_name = request.form.get(f'pokemon_{i}')
                
                if pokemon_name:  # Nur hinzufügen, wenn ein Pokémon angegeben wurde
                    encounters.append((trainer_id, pokemon_name))
            
            if not route_name or not encounters:
                flash("Bitte fülle alle Felder aus.", "error")
                return redirect(url_for('new_encounter'))
            
            # Prüfe auf verbotene Pokémon
            banned_pokemon = []
            for trainer_id, pokemon_name in encounters:
                if pm.is_pokemon_banned(pokemon_name):
                    banned_pokemon.append(pokemon_name)
            
            if banned_pokemon:
                flash(f"Folgende Pokémon sind verboten: {', '.join(banned_pokemon)}", "error")
                return redirect(url_for('new_encounter'))
            
            # Füge Route hinzu
            route = pm.get_route(name=route_name)
            if not route:
                route_id = pm.add_route(route_name)
            else:
                route_id = route['id']
                if route['status'] == 'closed':
                    flash("Diese Route ist bereits geschlossen!", "error")
                    return redirect(url_for('new_encounter'))
            
            # Füge Pokémon hinzu und zur Verbotsliste
            for trainer_id, pokemon_name in encounters:
                pokemon_id = pm.add_pokemon(pokemon_name, route_id, trainer_id)
                pm.add_banned_pokemon(pokemon_name, "gefangen")
                
                # Füge Evolutionen zur Verbotsliste hinzu
                evolutions = pm.get_banned_evolutions(pokemon_name)
                for evolution in evolutions:
                    if evolution != pokemon_name:
                        pm.add_banned_pokemon(evolution, f"Evolution von {pokemon_name}")
            
            flash("Begegnung erfolgreich hinzugefügt!", "success")
            return redirect(url_for('index'))
        
        trainers = pm.get_all_trainers()
        return render_template('new_encounter.html', trainers=trainers)
    
    @app.route('/mark_dead', methods=['GET', 'POST'])
    def mark_dead():
        if request.method == 'POST':
            route_id = request.form.get('route_id')
            pokemon_id = request.form.get('pokemon_id')
            
            if not route_id or not pokemon_id:
                flash("Bitte wähle eine Route und ein Pokémon aus.", "error")
                return redirect(url_for('mark_dead'))
            
            # Markiere Pokémon als tot
            success = pm.mark_pokemon_as_dead(pokemon_id)
            
            if success:
                # Finde den Trainer des Pokémon
                pokemon = pm.get_pokemon(pokemon_id)
                trainer_id = pokemon['trainer_id']
                
                flash("Pokémon als gestorben markiert! Bitte wähle ein neues aktives Pokémon.", "success")
                return redirect(url_for('change_active_pokemon', trainer_id=trainer_id))
            else:
                flash("Fehler beim Markieren des Pokémon als tot.", "error")
                return redirect(url_for('mark_dead'))
        
        routes = pm.get_all_routes()
        open_routes = [r for r in routes if r['status'] == 'open']
        return render_template('mark_dead.html', routes=open_routes)
    
    @app.route('/get_pokemon/<int:route_id>')
    def get_pokemon(route_id):
        pokemon_list = pm.get_pokemon_by_route(route_id)
        alive_pokemon = [p for p in pokemon_list if p['status'] == 'alive']
        
        return jsonify([{
            'id': p['id'],
            'name': p['name'],
            'trainer_name': p['trainer_name']
        } for p in alive_pokemon])
    
    @app.route('/change_active_pokemon/<int:trainer_id>', methods=['GET', 'POST'])
    def change_active_pokemon(trainer_id):
        trainer = pm.get_trainer(trainer_id)
        
        if request.method == 'POST':
            pokemon_id = request.form.get('pokemon_id')
            
            if pokemon_id:
                pm.set_active_pokemon(pokemon_id, trainer_id)
                flash(f"Aktives Pokémon für {trainer['name']} geändert.", "success")
                return redirect(url_for('index'))
        
        # Holen aller lebenden Pokémon des Trainers
        all_pokemon = pm.get_pokemon_by_trainer(trainer_id)
        alive_pokemon = [p for p in all_pokemon if p['status'] == 'alive']
        
        return render_template('active_pokemon.html', 
                              trainer=trainer, 
                              pokemon_list=alive_pokemon)
    
    @app.route('/banned_pokemon')
    def banned_pokemon():
        banned_pokemon = pm.get_all_banned_pokemon()
        return render_template('banned_pokemon.html', banned_pokemon=banned_pokemon)
    
    @app.route('/new_game', methods=['GET', 'POST'])
    def new_game():
        if request.method == 'POST':
            player_names = request.form.get('player_names')
            
            if not player_names:
                flash("Bitte gib mindestens einen Spielernamen ein.", "error")
                return redirect(url_for('new_game'))
            
            player_names = [name.strip() for name in player_names.split(',') if name.strip()]
            
            pm.reset_game(player_names)
            flash("Neues Spiel gestartet!", "success")
            return redirect(url_for('index'))
        
        return render_template('new_game.html')
    
    @app.route('/api/pokemon/<pokemon_name>')
    def get_pokemon_data(pokemon_name):
        data = pm.get_pokemon_data_from_api(pokemon_name)
        if data:
            return jsonify(data)
        else:
            return jsonify({'error': 'Pokémon nicht gefunden'}), 404
        
    @app.route('/api/tcg/card/<pokemon_name>')
    def get_tcg_card(pokemon_name):
        """Gibt Informationen zu einer Pokémon-Karte zurück"""
        card = tcg_api.get_pokemon_card(pokemon_name)
        if card:
            return jsonify({
                'name': card.name,
                'id': getattr(card, 'id', ''),
                'image_url': tcg_api.get_card_image_url(card),
                'set': getattr(card, 'set', {}),
                'rarity': getattr(card, 'rarity', ''),
                'artist': getattr(card, 'artist', '')
            })
        else:
            return jsonify({'error': 'Karte nicht gefunden'}), 404
    
    @app.route('/api/tcg/image/<pokemon_name>')
    def get_tcg_image(pokemon_name):
        """Gibt das Kartenbild als Base64-String zurück"""
        image_base64 = tcg_api.get_card_image_base64(pokemon_name)
        if image_base64:
            return jsonify({'image': f"data:image/png;base64,{image_base64}"})
        else:
            return jsonify({'error': 'Bild nicht gefunden'}), 404
    
    @app.route('/api/tcg/search/<query>')
    def search_tcg_cards(query):
        """Such nach Pokémon-Karten"""
        results = tcg_api.search_pokemon_cards(query)
        return jsonify([{
            'name': card.name,
            'id': getattr(card, 'id', ''),
            'image_url': tcg_api.get_card_image_url(card)
        } for card in results])
    
    @app.route('/card_search')
    def card_search():
        """Seite für die Karten-Suche"""
        return render_template('card_search.html')