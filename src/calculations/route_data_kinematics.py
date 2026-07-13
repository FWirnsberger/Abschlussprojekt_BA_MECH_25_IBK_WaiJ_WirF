import pandas as pd
import logging
from src.models.gps_point import GPSPoint

class RouteData:
    """Klasse zum Einlesen und Verwalten der GPS-Routendaten."""

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        # Daten werden erst beim Aufruf von load_data geladen
        self.data = None 
        self._points = []

    def load_data(self) -> None:
        logging.info(f"Lese CSV aus: {self.file_path}")
        # sep=';' da die GPS-Daten mit ; getrennt sind
        self.data = pd.read_csv(self.file_path, sep=';')
        # String-Zeitstempel in echte datetime-Objekte umwandeln
        # (Wichtig für die spätere Berechnung von delta t)
        self.data['time'] = pd.to_datetime(self.data['time'])
        logging.info("GPSPoint-Objekte erstellen aus der CSV")
        self._points = []

        # jede zeile wird durchgegangen und ein objekt erstellt
        for index, row in self.data.iterrows():
            punkt = GPSPoint(
                lat=row['lat'],
                lon=row['lon'],
                ele=row['ele'],
                time=row['time'],
                temp=row['temperature']
            )
            self._points.append(punkt)
            
        logging.info(f"{len(self._points)} GPSPoint-Objekte erfolgreich geladen.")

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
        
        # Wir iterieren durch die Tabelle ab der zweiten zeile (start index 1)
        for i in range(1, len(self.data)):
            p_prev = self._points[i-1] # Der vorherige Punkt A
            p_curr = self._points[i]   # Der aktuelle punkt B
            
            # Koordinaten von Punkt B
            lat2 = self.data.loc[i, 'lat']
            lon2 = self.data.loc[i, 'lon']
            
            # Distanz [m] (ds)
            # Punkt A berechnet die Distanz zu Punkt B
            ds = p_prev.get_distance_to(p_curr)
            distances.append(ds)
            
            # Zeitdifferenz [s] (dt)
            dt = p_prev.get_time_difference_to(p_curr)
            
            # Geschwindigkeit [m/s] (v = ds / dt)
            if dt > 0:
                v = ds / dt
            else:
                v = 0.0
                
            speeds.append(v)

            # Beschleunigung (a) [m/s^2] (a = (v - v_prev) / dt)
            v_prev = speeds[i-1]
            if dt > 0:
                a = (v - v_prev) / dt
            else:
                a = 0.0
            accelerations.append(a)
            
            # Steigung
            # mit Getter (.ele), um höhe abzufragen
            dh = p_curr.ele - p_prev.ele
            
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

    def calculate_total_distance(self) -> float:
        """
        Hier wird die gesamte zurückgelegte Strecke in Meter berechnet, in km wird erst im main umgewandelt.
        """

        #Fehlererkennung falls keine Daten geladen wurden
        if self.data is None:
            logging.error("Fehler: Keine Daten geladen!")
            return 0.0
        
        #Fehlererkennung falls die Funktion "calculate_kinematics" nicht ausgeführt wurde
        if 'distance_m' not in self.data.columns:
            logging.error("Fehler: Die Kinematik wurde nicht berechnet!")
            return 0.0
        
        #Summe aus den einzelnen Teilstrecken zw. den GPS Punkten
        total_distance = self.data['distance_m'].sum()
        
        logging.info(f"Gesamte Strecke wurde berechnet.")

        return total_distance
    
    def calculate_total_time(self)-> float:
        """
        Berechnung der gesamten Fahrzeit
        """

        #Fehlererkennung 
        if self.data is None:
            logging.error("Fehler: Keine Daten geladen!")
            return 0.0
        
        #gesamte Zeit mit dem ersten und letzten Zeitstempel der CSV-Datei berechnen
        #"time geht auf die Spalte, iloc auf die nötige Zeile"
        start_time = self.data["time"].iloc[0]
        end_time = self.data["time"].iloc[-1]

        total_time = (end_time - start_time).total_seconds()
        logging.info("Gesamt Fahrzeit wurde berechnet.")

        return total_time
    

    def calculate_average_speed(self, total_distance : float, total_time: float) -> float:
        """
        Berechnung der Durchschnittsgeschwindigkeit

        Args:
            total_distance (float): gesamte zurückgelegte Strecke[m]
            total_time (float): gesamte Fahrzeit[s]

        Returns: 
            float: Durchschnittsgeschwindigkeit [m/s]
        """

        #Fehlererkennung
        if self.data is None:
            logging.error("Fehler: Keine Daten geladen!")
            return 0.0
        
        #Division durch 0 verhindern
        if total_time <= 0:
            logging.error("Fehler: Gesamtzeit beträgt 0 Sekunden!")
            return 0.0
        
        average_speed = total_distance / total_time 
        logging.info("Durchschnittsgeschwindigkeit wurde berechnet.")

        return average_speed


    def calculate_total_elevation(self) -> tuple[float, float]:
        """
        Berechnung des Anstiegs und Abstieg über die Strecke

        Returns:
            tuple[float, float]: (gesamter Anstieg [m], gesamter Abstieg [m])
        """
        #Fehlererkennung
        if self.data is None:
            logging.error("Fehler: Keine Daten geladen!")
            return 0.0, 0.0
        
        total_ascent = 0.0
        total_descent = 0.0

        #alle GPS durchlaufen
        for i in range(1, len(self._points)):
            p_previous = self._points[i-1]
            p_currently = self._points[i]

            #Höhenunterschied zwischen zwei Punkten berechnen
            dh = p_currently.ele - p_previous.ele

            #Anstieg
            if dh > 0:
                total_ascent += dh
            #Abstieg
            elif dh < 0:
                total_descent += abs(dh)

        logging.info("Höhenmeter wurden berechnet.")
            
        return total_ascent, total_descent

def get_data(self) -> pd.DataFrame:
        """Gibt das berechnete DataFrame zurück. (Datenkapselung)"""
        return self.data