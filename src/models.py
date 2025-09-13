class Trainer:
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name
    
    def __str__(self):
        return f"Trainer {self.id}: {self.name}"

class Route:
    def __init__(self, id=None, name=None, status='open'):
        self.id = id
        self.name = name
        self.status = status
    
    def __str__(self):
        status_icon = "🟢" if self.status == 'open' else "🔴"
        return f"Route {self.id}: {self.name} {status_icon}"

class Pokemon:
    def __init__(self, id=None, name=None, route_id=None, trainer_id=None, status='alive'):
        self.id = id
        self.name = name
        self.route_id = route_id
        self.trainer_id = trainer_id
        self.status = status
    
    def __str__(self):
        status_icon = "❤️" if self.status == 'alive' else "💀"
        return f"Pokémon {self.id}: {self.name} ({status_icon})"

class LinkGroup:
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name
        self.pokemon_list = []
    
    def __str__(self):
        return f"Link-Gruppe {self.id}: {self.name} ({len(self.pokemon_list)} Pokémon)"