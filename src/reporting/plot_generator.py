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

    def get_time_minutes(self)-> pd.Series:
        """
        Hier wird die vergangene Fahrzeit in Minuten berechnet, für die Graphen.
        """ 
        if self.data is None:
            raise ValueError("Es wurden keine Daten übergeben.")

        if "time" not in self.data.columns:
            raise ValueError("Die Spalte time fehlt im DataFrame.")

        start_time = self.data["time"].iloc[0]

        return (self.data["time"] - start_time).dt.total_seconds() / 60
    

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
        #Maximalwert
        max_index = speed_km_h.idxmax()

        max_speed = speed_km_h.loc[max_index]
        max_time = time_minutes.loc[max_index]

        average_speed = speed_km_h.mean()

        plt.scatter(
            max_time,
            max_speed,
            color="red",
            zorder=5,
            label=f"Maximum ({max_speed:.1f} km/h)"
        )
        #Max wert daneben schreiben
        plt.annotate(
        f"{max_speed:.1f} km/h",
        (max_time, max_speed),
        xytext=(10, 10),
        textcoords="offset points"
        )

        #Durchschnittsgeschwindigkeit einzeichen
        plt.axhline(
        y=average_speed,
        linestyle="--",
        color="red",
        label=f"Durchschnitt ({average_speed:.1f} km/h)"
        )

        plt.margins(x=0)    #y-achse bei 0
        plt.legend()
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

    def create_acceleration_plot(self) -> Path:
        """
        Erstellt die Grafik des Beschleunigungsverlaufs.
        """

        if "acceleration_m_s2" not in self.data.columns:
            raise ValueError("Die Spalte acceleration_m_s2 fehlt.")

        time_minutes = self.get_time_minutes()
        figure_path = self.output_folder / "Beschleunigungsprofil.png"

        plt.figure(figsize=(12, 6))

        plt.plot(
            time_minutes,
            self.data["acceleration_m_s2"]
        )
        plt.margins(x=0)
        plt.title("Beschleunigungsverlauf der Fahrt")
        plt.xlabel("Fahrzeit [min]")
        plt.ylabel("Beschleunigung [m/s²]")
        plt.grid()
        plt.tight_layout()

        plt.savefig(figure_path, dpi=300)
        plt.close()

        logging.info(f"Beschleunigungsgrafik erstellt: {figure_path}")

        return figure_path
    
    def create_power_plot(self) -> Path:
        """
        Erstellt eine gemeinsame Grafik für Gesamt-, Fahrer- und Motorleistung.
        """

        required_columns = [
            "total_power_w",
            "rider_power_w",
            "motor_power_w",
        ]

        for column in required_columns:
            if column not in self.data.columns:
                raise ValueError(f"Die Spalte {column} fehlt.")

        time_minutes = self.get_time_minutes()
        figure_path = self.output_folder / "Leistungsprofil.png"

        plt.figure(figsize=(12, 6))

        plt.plot(
            time_minutes,
            self.data["total_power_w"],
            label="Gesamtleistung"
        )

        plt.plot(
            time_minutes,
            self.data["rider_power_w"],
            label="Fahrerleistung"
        )

        plt.plot(
            time_minutes,
            self.data["motor_power_w"],
            label="Motorleistung"
        )
        plt.margins(x=0)
        plt.title("Leistungsverlauf der Fahrt")
        plt.xlabel("Fahrzeit [min]")
        plt.ylabel("Mechanische Leistung [W]")
        plt.legend()
        plt.grid()
        plt.tight_layout()

        plt.savefig(figure_path, dpi=300)
        plt.close()

        logging.info(f"Leistungsgrafik erstellt: {figure_path}")

        return figure_path
    
    def create_motor_torque_plot(self) -> Path:
        """
        Erstellt die Grafik des Motordrehmoments.
        """

        if "motor_torque_nm" not in self.data.columns:
            raise ValueError("Die Spalte motor_torque_nm fehlt.")

        time_minutes = self.get_time_minutes()
        figure_path = self.output_folder / "Motordrehmomentprofil.png"

        plt.figure(figsize=(12, 6))

        plt.plot(
            time_minutes,
            self.data["motor_torque_nm"]
        )
        plt.margins(x=0)
        plt.title("Drehmomentverlauf des Motors")
        plt.xlabel("Fahrzeit [min]")
        plt.ylabel("Motordrehmoment [Nm]")
        plt.grid()
        plt.tight_layout()

        plt.savefig(figure_path, dpi=300)
        plt.close()

        logging.info(f"Drehmomentgrafik erstellt: {figure_path}")

        return figure_path
    
    def create_motor_current_plot(self) -> Path:
        """
        Erstellt die Grafik des Motorstroms.
        """

        if "motor_current_a" not in self.data.columns:
            raise ValueError("Die Spalte motor_current_a fehlt.")

        time_minutes = self.get_time_minutes()
        figure_path = self.output_folder / "Motorstromprofil.png"

        plt.figure(figsize=(12, 6))

        plt.plot(
            time_minutes,
            self.data["motor_current_a"]
        )
        plt.margins(x=0)
        plt.title("Stromverlauf des Motors")
        plt.xlabel("Fahrzeit [min]")
        plt.ylabel("Motorstrom [A]")
        plt.grid()
        plt.tight_layout()

        plt.savefig(figure_path, dpi=300)
        plt.close()

        logging.info(f"Motorstromgrafik erstellt: {figure_path}")

        return figure_path
    
    def create_soc_plot(self) -> Path:
        """
        Erstellt eine gemeinsame Grafik des Ladezustands beider Batterien.
        """

        required_columns = [
            "soc_lipo",
            "soc_nmc",
        ]

        for column in required_columns:
            if column not in self.data.columns:
                raise ValueError(f"Die Spalte {column} fehlt.")

        time_minutes = self.get_time_minutes()
        figure_path = self.output_folder / "Ladezustandsprofil.png"

        plt.figure(figsize=(12, 6))

        plt.plot(
            time_minutes,
            self.data["soc_lipo"] * 100,
            label="LiPo"
        )

        plt.plot(
            time_minutes,
            self.data["soc_nmc"] * 100,
            label="NMC"
        )
        plt.margins(x=0)
        plt.title("Ladezustand der Batterien")
        plt.xlabel("Fahrzeit [min]")
        plt.ylabel("Ladezustand [%]")
        plt.ylim(0, 100)
        plt.legend()
        plt.grid()
        plt.tight_layout()

        plt.savefig(figure_path, dpi=300)
        plt.close()

        logging.info(f"SoC-Grafik erstellt: {figure_path}")

        return figure_path
    
    def create_voltage_plot(self) -> Path:
        """
        Erstellt eine gemeinsame Grafik der Batteriespannungen.
        """

        required_columns = [
            "voltage_V_lipo",
            "voltage_V_nmc",
        ]

        for column in required_columns:
            if column not in self.data.columns:
                raise ValueError(f"Die Spalte {column} fehlt.")

        time_minutes = self.get_time_minutes()
        figure_path = self.output_folder / "Spannungsprofil.png"

        plt.figure(figsize=(12, 6))

        plt.plot(
            time_minutes,
            self.data["voltage_V_lipo"],
            label="LiPo"
        )

        plt.plot(
            time_minutes,
            self.data["voltage_V_nmc"],
            label="NMC"
        )

        plt.margins(x=0)
        plt.title("Spannungsverlauf der Batterien")
        plt.xlabel("Fahrzeit [min]")
        plt.ylabel("Batteriespannung [V]")
        plt.legend()
        plt.grid()
        plt.tight_layout()

        plt.savefig(figure_path, dpi=300)
        plt.close()

        logging.info(f"Spannungsgrafik erstellt: {figure_path}")

        return figure_path
    
    def create_elevation_plot(self) -> Path:
        """
        Erstellt das Höhenprofil über der zurückgelegten Strecke.
        """

        required_columns = [
            "distance_m",
            "ele",
        ]

        for column in required_columns:
            if column not in self.data.columns:
                raise ValueError(f"Die Spalte {column} fehlt.")

        # Kumulierte Strecke bilden und in Kilometer umrechnen
        distance_km = self.data["distance_m"].cumsum() / 1000

        figure_path = self.output_folder / "Hoehenprofil.png"

        plt.figure(figsize=(12, 6))

        plt.plot(
            distance_km,
            self.data["ele"]
        )

        plt.margins(x=0)
        plt.title("Höhenprofil der Strecke")
        plt.xlabel("Zurückgelegte Strecke [km]")
        plt.ylabel("Höhe [m]")
        plt.grid()
        plt.tight_layout()

        plt.savefig(figure_path, dpi=300)
        plt.close()

        logging.info(f"Höhenprofil erstellt: {figure_path}")

        return figure_path
