import pandas as pd

class RouteData:
    def __init__(self, file_path: str):
        """
        Initialisiert die RouteData-Klasse und lädt die CSV-Daten.
        """
        self.file_path = file_path
        self.data = None

    def load_data(self):
        """
        Lädt die GPS-Daten aus der CSV-Datei in einen Pandas DataFrame.
        """
        print(f"Lade Daten von {self.file_path}...")
        # Die Daten sind mit Semikolon getrennt, daher sep=';'
        self.data = pd.read_csv(self.file_path, sep=';')
        
        # Den Zeitstempel in ein echtes Datum/Zeit-Format umwandeln
        self.data['time'] = pd.to_datetime(self.data['time'])
        
        print("Daten erfolgreich geladen!")
        print(self.data.head()) # Zeigt die ersten 5 Zeilen an

# === Hauptprogramm ===
if __name__ == "__main__":
    
    datei_pfad = "final_project_input_data.csv" 
    
    # Ein Objekt unserer Klasse erstellen
    meine_route = RouteData(datei_pfad)
    
    # Die Methode zum Laden aufrufen
    meine_route.load_data()