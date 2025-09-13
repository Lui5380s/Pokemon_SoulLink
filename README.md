# Pokémon Link Manager

Ein Tool zum Verwalten von Pokémon-Begegnungen für Soul Link Nuzlocke Challenges.

## Funktionen

- **Pokémon-Eindeutigkeit**: Jedes Pokémon kann nur einmal im gesamten Run gefangen werden
- **Soul Link Mechanik**: Wenn ein Pokémon stirbt, sterben alle Pokémon auf derselben Route
- **Routen-Management**: Geschlossene Routen können nicht mehr verwendet werden
- **GUI-Oberfläche**: Benutzerfreundliche Oberfläche mit PyQt5

## Installation

1. Installiere die Abhängigkeiten: `pip install -r requirements.txt`
2. Führe `python src/run_gui.py` aus

## Soul Link Regeln

1. **Pokémon-Eindeutigkeit**: Jedes Pokémon kann nur einmal gefangen werden
   - Wenn Player1 Pikachu fängt, kann kein anderer Spieler Pikachu fangen
   - Auch Entwicklungen (Vor- und Weiterentwicklungen) sind gesperrt
   
2. **Route-Linking**: Alle Pokémon auf einer Route sind verlinkt
   - Stirbt ein Pokémon, sterben alle Pokémon auf der Route
   - Die Route wird geschlossen

## GUI Features

- **Routen-Übersicht**: Zeigt alle Routen mit Status (offen/geschlossen)
- **Pokémon-Liste**: Alle Pokémon nach Routen gruppiert
- **Neue Begegnung**: Dialog zum Hinzufügen neuer Begegnungen
- **Pokémon markieren**: Markiert Pokémon als tot (mit Bestätigung)

## Verwendung

1. **Neue Begegnung hinzufügen**: 
   - Wähle Route und Pokémon für alle drei Trainer
   - Das System prüft automatisch auf doppelte Pokémon

2. **Pokémon als tot markieren**:
   - Wähle eine Route und ein Pokémon
   - Bestätige die Aktion (betrifft alle Pokémon der Route)

3. **Übersichten anzeigen**:
   - Routen, Pokémon und Trainer in separaten Tabs