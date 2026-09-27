from functools import lru_cache
import requests

API_URL = "https://api.tcgdex.net/v2/en/cards"


class TCGAPI:
    """Zugriff auf Pokémon-Sammelkarten über die TCGdex REST-API (https://tcgdex.dev)"""

    def _fetch_cards(self, name):
        """Holt alle Karten, deren Name den Suchbegriff enthält (nur Karten mit Bild)"""
        try:
            response = requests.get(API_URL, params={"name": name}, timeout=10)
            response.raise_for_status()
            return [card for card in response.json() if card.get("image")]
        except (requests.RequestException, ValueError) as e:
            print(f"Fehler beim Abrufen der Karten: {e}")
            return []

    @lru_cache(maxsize=256)
    def get_pokemon_card(self, pokemon_name):
        """Gibt eine Karte zurück, deren Name exakt passt – sonst die erste Teilübereinstimmung"""
        cards = self._fetch_cards(pokemon_name)
        for card in cards:
            if card["name"].lower() == pokemon_name.lower():
                return card
        return cards[0] if cards else None

    def search_pokemon_cards(self, query, limit=10):
        """Sucht nach Karten basierend auf einem Suchbegriff"""
        return self._fetch_cards(query)[:limit]

    @staticmethod
    def get_card_image_url(card, quality="high"):
        """Gibt die URL des Kartenbildes zurück"""
        if card and card.get("image"):
            return f"{card['image']}/{quality}.png"
        return None
