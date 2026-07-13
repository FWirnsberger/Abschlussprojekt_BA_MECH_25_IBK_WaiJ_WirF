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
        


        
        