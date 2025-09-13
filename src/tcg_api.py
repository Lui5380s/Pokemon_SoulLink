from tcgdexsdk import TCGdex, Language
from tcgdexsdk.enums import Quality, Extension
import requests
from io import BytesIO
from PIL import Image
import base64

class TCGAPI:
    def __init__(self):
        self.sdk = TCGdex(Language.EN)
    
    def get_pokemon_card(self, pokemon_name):
        """Holt Karteninformationen für ein Pokémon"""
        try:
            # Versuche, die Karte über den Namen zu finden
            # Beachte: Die SDK unterstützt keine direkte Suche nach Namen,
            # also müssen wir eine alternative Methode verwenden
            cards = self.sdk.card.get_all_sync(limit=100)
            
            for card in cards:
                if hasattr(card, 'name') and card.name.lower() == pokemon_name.lower():
                    return card
            
            # Wenn nicht gefunden, versuche es mit einer Teilübereinstimmung
            for card in cards:
                if hasattr(card, 'name') and pokemon_name.lower() in card.name.lower():
                    return card
                    
            return None
        except Exception as e:
            print(f"Fehler beim Abrufen der Karte: {e}")
            return None
    
    def get_card_image_url(self, card, quality=Quality.HIGH, extension=Extension.PNG):
        """Gibt die URL des Kartenbildes zurück"""
        if card and hasattr(card, 'get_image_url'):
            return card.get_image_url(quality, extension)
        return None
    
    def get_card_image_data(self, card, quality=Quality.HIGH, extension=Extension.PNG):
        """Lädt das Kartenbild herunter und gibt die Bilddaten zurück"""
        try:
            if card and hasattr(card, 'get_image'):
                return card.get_image(quality, extension)
            return None
        except Exception as e:
            print(f"Fehler beim Herunterladen des Bildes: {e}")
            return None
    
    def get_card_image_base64(self, card, quality=Quality.HIGH, extension=Extension.PNG):
        """Gibt das Kartenbild als Base64-String zurück"""
        image_data = self.get_card_image_data(card, quality, extension)
        if image_data:
            return base64.b64encode(image_data).decode('utf-8')
        return None
    
    def search_pokemon_cards(self, query, limit=10):
        """Such nach Pokémon-Karten basierend auf einem Suchbegriff"""
        try:
            all_cards = self.sdk.card.get_all_sync(limit=100)
            results = []
            
            for card in all_cards:
                if hasattr(card, 'name') and query.lower() in card.name.lower():
                    results.append(card)
                    if len(results) >= limit:
                        break
            
            return results
        except Exception as e:
            print(f"Fehler bei der Suche: {e}")
            return []