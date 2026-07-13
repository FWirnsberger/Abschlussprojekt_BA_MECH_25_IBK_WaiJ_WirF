import logging 
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


class PlotGenerator:
    """
    hier werden die Grafiken aus den berechneten Werten erstellt
    """
    def __init__(self, data: pd.DataFrame, output_folder: str) -> None:
        """
        Argumente:
            data:   DataFrame mit den berechneten Daten der Strecke
            output_folder: Ordner in dem die Grafiken gespeichert werden
        """

        self.data = data
        self.output_folder = Path(output_folder)

        #Ordner automatisch erstellen
        self.output_folder.mkdir(parents= True, exist_ok= True)


    def create_speed_plot(self) -> Path:
        """
        Erstellt die Grafik des Geschwindigkeitsverlaufs

        Returns:
            Path: gibt den Pfad zur gespeicherten grafik wieder
        """

        #Fehlererkennung, prüfen ob Daten vorhanden sind
        if self.data is None:
            logging.error("Es wurden keine Daten an den PlotGenerator übergeben.")
            raise ValueError("Es wurden keine Daten an den PlotGenerator übergeben.")

        #prüfen ob die benötigten Spalten mit der Geschwindigkeit und Zeit vorhanden sind
        if "time" not in self.data.columns:
            logging.error("Die Spalte time fehlt im DataFrame.")
            raise ValueError("Die Spalte time fehlt.")

        if "speed_m_s" not in self.data.columns:
            logging.error("Die Spalte speed_m_s fehlt, wurde calculate_kinematics() ausgeführt?")
            raise ValueError("Die Spalte speed_m_s fehlt, wurde calculate_kinematics() ausgeführt?")
        

        #Zeit seit Fahrtbeginn berechnen, in minuten
        start_time = self.data["time"].iloc[0]

        time_minutes = (self.data["time"] - start_time).dt.total_seconds() / 60     #.dt.totalseconds ist von pandas und rechnet die zeitdifferenz in Sekunden um

        #Geschwindigkeit von m/s in km/h
        speed_km_h = self.data["speed_m_s"] * 3.6

        #Pfad der Grafik festlegen
        figure_path = self.output_folder / "Geschwindigkeitsprofil.png"

        #eine neue Grafik erstellen
        plt.figure(figsize=(12, 6)) #Breite und Höhe in Zoll
        #Verlauf zeichnen
        plt.plot(time_minutes, speed_km_h)      #x-Achse, y-Achse 
        #Beschriftung
        plt.title("Geschwindigkeitsverlauf der Fahrt")
        plt.xlabel("Fahrzeit [min]")
        plt.ylabel("Geschwindigkeit [km/h]")
        
        plt.grid()                              #Gitter einblenden
        plt.tight_layout()                      #Abstände automatisch anpassen
        
        #Grafik als png speichern
        plt.savefig(figure_path, dpi = 300)
        plt.close()                             #Grafik wird sofort wieder geschlossen, damit nichts aufploppt

        logging.info(f"Geschwindkeitsgrafik erstellt: {figure_path}")

        return figure_path
