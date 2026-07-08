import pandas as pd

class RouteData:
    """Klasse zum Einlesen und Verwalten der GPS-Routendaten."""

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        # Daten werden erst beim Aufruf von load_data() geladen
        self.data = None 

    def load_data(self) -> None:
        print(f"Lese CSV aus: {self.file_path}")
        
        # sep=';' da die GPS-Daten mit ; getrennt sind
        self.data = pd.read_csv(self.file_path, sep=';')
        
        # String-Zeitstempel in echte datetime-Objekte umwandeln
        # (Wichtig für die spätere Berechnung von delta t)
        self.data['time'] = pd.to_datetime(self.data['time'])
        
        print("Daten erfolgreich geladen.")


if __name__ == "__main__":
    
    # Pfad für die CSV Daten
    path = "data/final_project_input_data.csv" 
    
    route = RouteData(path)
    route.load_data()
    
    # Test ob Daten richtig sind
    print(route.data.head())