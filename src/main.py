import pandas as pd
from geo_utils import GeoUtils

class RouteData:
    """Klasse zum Einlesen und Verwalten der GPS-Routendaten."""

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        # Daten werden erst beim Aufruf von load_data geladen
        self.data = None 

    def load_data(self) -> None:
        print(f"Lese CSV aus: {self.file_path}")
        # sep=';' da die GPS-Daten mit ; getrennt sind
        self.data = pd.read_csv(self.file_path, sep=';')
        # String-Zeitstempel in echte datetime-Objekte umwandeln
        # (Wichtig für die spätere Berechnung von delta t)
        self.data['time'] = pd.to_datetime(self.data['time'])
        print("Daten erfolgreich geladen.")

    def calculate_kinematics(self) -> None:
        """Berechnet Distanz (ds) und Geschwindigkeit (v) zwischen den GPS-Punkten."""
        if self.data is None:
            print("Fehler: Keine Daten geladen!")
            return

        print("Berechne Distanzen und Geschwindikeiten...")
        
        # Listen zum Speichern der Ergebnisse 
        distances = [0.0]
        speeds = [0.0]
        
        # Wir iterieren durch die Tabelle ab der zweiten Zeile (index 1)
        for i in range(1, len(self.data)):
            # Koordinaten von Punkt A (vorheriger Punkt)
            lat1 = self.data.loc[i-1, 'lat']
            lon1 = self.data.loc[i-1, 'lon']
            
            # Koordinaten von Punkt B (aktueller Punkt)
            lat2 = self.data.loc[i, 'lat']
            lon2 = self.data.loc[i, 'lon']
            
            # Distanz in Metern (ds)
            ds = GeoUtils.haversine_distance(lat1, lon1, lat2, lon2)
            distances.append(ds)
            
            # Zeitdifferenz in Sekunden (dt)
            time1 = self.data.loc[i-1, 'time']
            time2 = self.data.loc[i, 'time']
            dt = (time2 - time1).total_seconds()
            
            # Geschwindigkeit in m/s (v = ds / dt)
            if dt > 0:
                v = ds / dt
            else:
                v = 0.0
                
            speeds.append(v)
            
        # Ergebnisse als neue Spalten zum DataFrame hinzufügen
        self.data['distance_m'] = distances
        self.data['speed_m_s'] = speeds
        
        print("Kinematik erfolgreich berechnet.")


if __name__ == "__main__":
    
    # Pfad für die CSV Daten
    path = "data/final_project_input_data.csv" 
    
    route = RouteData(path)
    route.load_data()
    route.calculate_kinematics()
    
    # Test ob Daten richtig sind
    print(route.data[['time', 'lat', 'lon', 'distance_m', 'speed_m_s']].head())