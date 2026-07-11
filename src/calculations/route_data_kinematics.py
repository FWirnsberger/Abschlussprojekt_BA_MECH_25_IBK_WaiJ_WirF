import pandas as pd
import logging
from src.calculations.geo_utils import GeoUtils

class RouteData:
    """Klasse zum Einlesen und Verwalten der GPS-Routendaten."""

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        # Daten werden erst beim Aufruf von load_data geladen
        self.data = None 

    def load_data(self) -> None:
        logging.info(f"Lese CSV aus: {self.file_path}")
        # sep=';' da die GPS-Daten mit ; getrennt sind
        self.data = pd.read_csv(self.file_path, sep=';')
        # String-Zeitstempel in echte datetime-Objekte umwandeln
        # (Wichtig für die spätere Berechnung von delta t)
        self.data['time'] = pd.to_datetime(self.data['time'])
        logging.info("Daten erfolgreich geladen.")

    def calculate_kinematics(self) -> None:
        """Berechnet Distanz, Geschwindigkeit, Beschleunigung und Steigung zwischen den GPS-Punkten."""
        if self.data is None:
            logging.error("Fehler: Keine Daten geladen!")
            return

        logging.info("Berechne Kinematik (Distanz, Geschwindigkeit, Beschleunigung, Steigung): ")
        
        # Listen zum Speichern der Ergebnisse (start bei 0.0)
        distances = [0.0]
        speeds = [0.0]
        accelerations = [0.0]
        slopes = [0.0]
        
        # Wir iterieren durch die Tabelle ab der zweiten Zeile (index 1)
        for i in range(1, len(self.data)):
            # Koordinaten von Punkt A (vorheriger Punkt)
            lat1 = self.data.loc[i-1, 'lat']
            lon1 = self.data.loc[i-1, 'lon']
            
            # Koordinaten von Punkt B (aktueller Punkt)
            lat2 = self.data.loc[i, 'lat']
            lon2 = self.data.loc[i, 'lon']
            
            # Distanz [m] (ds)
            ds = GeoUtils.haversine_distance(lat1, lon1, lat2, lon2)
            distances.append(ds)
            
            # Zeitdifferenz [s] (dt)
            time1 = self.data.loc[i-1, 'time']
            time2 = self.data.loc[i, 'time']
            dt = (time2 - time1).total_seconds()
            
            # Geschwindigkeit [m/s] (v = ds / dt)
            if dt > 0:
                v = ds / dt
            else:
                v = 0.0
                
            speeds.append(v)

            # Beschleunigung (a) [m/s^2] (a = (v_aktuell - v_vorher) / dt)
            v_prev = speeds[i-1]
            if dt > 0:
                a = (v - v_prev) / dt
            else:
                a = 0.0
            accelerations.append(a)
            
            # Steigung
            h1 = self.data.loc[i-1, 'ele'] 
            h2 = self.data.loc[i, 'ele']
            dh = h2 - h1
            
            if ds > 0:
                slope = dh / ds  
            else:
                slope = 0.0
            slopes.append(slope)
            
        # Ergebnisse als neue Spalten zum DataFrame hinzufügen
        self.data['distance_m'] = distances
        self.data['speed_m_s'] = speeds
        self.data['acceleration_m_s2'] = accelerations
        self.data['slope'] = slopes
        
        logging.info("Kinematik erfolgreich berechnet.")

def get_data(self) -> pd.DataFrame:
        """Gibt das berechnete DataFrame zurück. (Datenkapselung)"""
        return self.data