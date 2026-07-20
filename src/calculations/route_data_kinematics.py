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
        """
        Hier wird die Distanz, Rohgeschwindigkeit, Zeitdifferenz und Steigung zwischen zwei aufeinanderfolgenden 
        GPS Punkten.
        Anschließend wird die Geschwindigkeit gefiltert und daraus die Beschleunigung berechnet, da die Ausreißer 
        die Ergebnisse der Leistungsberechnung verfälschen
        """
        #Fehlererkenneung
        if self.data is None:
            logging.error("Fehler: Keine Daten geladen!")
            return
        
        logging.info("Distanz, Rohgeschwindigkeit, Zeitdifferenz und Steigung WERDEN berechnet.")

        distances = [0.0]               #Liste zum speichern der einzelnen Distanzen zw. den Punkten
        
        raw_speeds = [float("nan")]     #1. Wert kann nicht berechnet werden, da kein vorheriger Punkt existiert

        time_differences = [0.0]        #Liste für Zeiten

        slopes = [0.0]                  #Liste für Steigungen


        #die Datentabelle wird durchlaufen
        for i in range(1, len(self.data)):
            #vorheriger und aktualler GPS Punkt
            p_prev = self._points[i - 1]
            p_curr = self._points[i]

            #Distanz zwischen den beiden Punkten
            ds = p_prev.get_distance_to(p_curr)
            distances.append(ds)

            #Zeitdifferenz der beiden Punkte
            dt = p_prev.get_time_difference_to(p_curr)
            time_differences.append(dt)

            #Rohgeschwindigkeit berechnen in m/s
            if dt > 0:
                raw_speed = ds / dt
            else:
                raw_speed = float("nan")    #wenn dt < 0 wird kein gültiger Wert definiert
                logging.warning(f"ungültige Zeitdifferenz {dt:.2f} bei Index {i} !")

            raw_speeds.append(raw_speed)

            #Höhenunterschied berechnen in m
            dh = p_curr.ele - p_prev.ele

            #Steigung berechnen
            if ds > 0:
                slope = dh /ds
            else:
                slope = 0

            slopes.append(slope)

        #Die Ergibnisse werden in einem DataFrame gespeichert
        self.data["distance_m"] = distances
        self.data["delta_time_s"] = time_differences
        self.data["speed_raw_m_s"] = raw_speeds
        self.data["slope"] = slopes

        logging.info("Distanz, Rohgeschwindigkeit, Zeitdifferenz und Steigung WURDEN berechnet.")

    def filter_speed(self, window_size: int = 5)-> None: 
        """
        Hier wird die Rohgeschwindigkeit mit einem Medianfilter geglättet
        Der Medianfilter entfernt Ausreißer, indem er die Ausreißer durch den Median seiner benachbarten Werte ersetzt.
        
        Argumente
            window_size:
                Anzahl der Messwerte innerhalb des Filterfensters.
                Die Fenstergröße muss eine ungerade Zahl sein.
        """
        #Fehlererkennung
        if self.data is None:
            logging.error("Fehler: Keine Daten geladen!")
            return
        
        #wurde die Rohgeschwindigkeit berechnet?
        if "speed_raw_m_s" not in self.data.columns:
            logging.error("Fehler: Die Rohgeschwindigkeit wurde nicht berechnet!")
            return
        
        #Fenstergröße für Medianfilter überprüfen
        #Fenstergröße ist die Anzahl der Werte die für den Median betrachtet werden
        if window_size < 3:
            raise ValueError("Nur Fenstergrößen grüßer 3 zulässig.")
        
        if window_size % 2 == 0:
            raise ValueError("Fenstergröße muss einer ungeraden Zahl entsprechen!")
        
        logging.info(f"Die Geschwindigkeit wird mit einem Medianfilter und einer Fenstergröße von {window_size} berechnet.")

        #Medianfilter wird angewandt
        self.data["speed_m_s"] = (self.data["speed_raw_m_s"].rolling(
                window=window_size,
                center=True,
                min_periods=1   
            ).median()
        )
        
        #An Anfang und Ende fehlen die Werte, die werden aufgefüllt
        #bfill - backward fill, ffill - forward fill
        self.data["speed_m_s"] = (self.data["speed_m_s"].bfill().ffill())

        logging.info("Geschwindigkeit wurde gefiltert")


    def calculate_acceleration(self, max_acceleration_m_s2: float = 3.5) -> None:       #alle Beschleunigugen > 3.5 werden "abgeschnitten" um unrealistische Werte zu vermeiden
        """
        Hier wird die Beschleunigung aus der gefilterten Geschwindigkeit berechnet.
        Danach wird die Beschleunigung in einem realistischen und optimistischen Bereich von
        +- 3.5 m_s2 begrenzt

        Argumente: 
            max_acceleration_m_s2:
                max Betrag der Beschleunigung (selbst festgelegt)
        """

        #Fehlererkennung-Geschwindigkeit vorhanden?
        if "speed_m_s" not in self.data.columns:
            logging.error("Fehler: Die Geschwindigkeit wurde noch nicht gefiltert.")
            return
        
        #Fehlererkennung-Zeitdifferenzen vorhanden?
        if "delta_time_s" not in self.data.columns:
            logging.error("Fehler: Die Zeitdifferenz wurde noch nicht berechnet.")
            return
        
        #Fehlererkennung-liegt die max. zulässige Beschleunigung in einem plausiblen Bereich?
        if max_acceleration_m_s2 <= 0:
            raise ValueError("Die max. zulässige Beschleunigung muss größer 0 sein.")
            
        logging.info("Beschleunigung aus der gefilterten Geschwindigkeit wird berechnet.")

        #Listen zum Speichern der Ergebnisse
        raw_accelerations = [0.0]
        accelerations = [0.0]

        #jetzt wird die zuvor berechnete Tabelle durchlaufen
        for i in range(1, len(self.data)):
            current_speed = self.data.loc[i, "speed_m_s"]           #aktuelle gefilterte Geschwindigkeit
            previous_speed = self.data.loc[i - 1, "speed_m_s"]      #vorherige gefilterte Geschwindigkeit

            #Zeitdifferenz vom aktuellen Streckenabschnitt berechnen
            dt = self.data.loc[i, "delta_time_s"]

            #Beschleunigung berechnen
            if dt > 0:    #damit kann float (dt) mit integer (0) verglichen werden ohne Konflikte
                raw_acceleration = (current_speed - previous_speed) / dt
            else: 
                raw_acceleration = 0.0

            raw_accelerations.append(raw_acceleration)

            #Beschleunigung wird auf den bestimmten Bereich begrenzt
            limited_acceleration = max(
                -max_acceleration_m_s2, 
                min(
                    raw_acceleration, max_acceleration_m_s2
                    )
            )

            accelerations.append(limited_acceleration)

        #Rohe und die begrenzte Beschleunigung berechnen
        self.data["acceleration_raw_m_s2"] = raw_accelerations
        self.data["acceleration_m_s2"] = accelerations

        #Zur Information werden die Anzahl der begrenzten Werte berechnet
        limited_count = (self.data["acceleration_raw_m_s2"] != self.data["acceleration_m_s2"]).sum()

        logging.info(f"Es wurden {limited_count} Beschleunigungswerte auf +- {max_acceleration_m_s2:.2f} begrenzt.")
        logging.info("Beschleunigung wurde berechnet.")

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
    
    def calculate_air_density(self)-> None:
        """
        Hier wird die Luftdichte für jeden GPS-Punkt anhand der Höhe und der Umgebungstemperatur gemessen.
        """

        #Fehlererkennung
        if self.data is None:
            raise ValueError("Es wurden noch keine Routendaten geladen!")
        
        required_columns = ["ele", "temperature",]

        for column in required_columns:
            if column not in self.data.columns:
                raise ValueError(f"Die Spalte {column} fehlt!")
            
            #Konstanten aus dem Internet
            sea_level_pressure_pa = 101325.0
            standard_temperature_k = 288.15
            temperature_gradient_k_m = 0.0065
            gravitational_acceleration_m_s2 = 9.80665
            molar_mass_air_kg_mol = 0.0289644
            universal_gas_constant = 8.3144598
            specific_gas_constant_air = 287.05

            altitude_m = self.data["ele"]
            temperature_c = pd.to_numeric(self.data["temperature"], errors="coerce")
            temperature_k = temperature_c + 273.15

            #Luftdruck berechnen
            pressure_pa = sea_level_pressure_pa * (1.0 - (temperature_gradient_k_m * altitude_m / standard_temperature_k)) ** (gravitational_acceleration_m_s2 * molar_mass_air_kg_mol / (universal_gas_constant * temperature_gradient_k_m))

            #ideale Gasgleichung aus Thermo
            air_density = pressure_pa / (specific_gas_constant_air * temperature_k)

            self.data["air_density_kg_m3"] = air_density

            logging.info("Luftdichte wurde aus Höhe udn Temperatur erfolgreich berechnet.")



    def get_data(self) -> pd.DataFrame:
        """Gibt das berechnete DataFrame zurück. (Datenkapselung)"""
        return self.data