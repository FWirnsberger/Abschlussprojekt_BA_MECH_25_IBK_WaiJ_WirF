import logging
from src.models.battery_base import BatteryBase
from src.models.motor import Motor
from src.models.e_bike import EBike
from src.calculations.e_bike_physics import EBikePhysics

class EBikeSimulator:
    """
    Simulator, der das E-Bike, den Motor und den Akku verbindet.
    Führt die zeitliche Simulation einer Route durch.
    """
    def __init__(self, e_bike: EBike, battery: BatteryBase, e_motor: Motor) -> None:
        self.e_bike = e_bike
        self.battery = battery
        self.e_motor = e_motor
        # Listen zum Speichern der Ergebnisse (für Plotting + Resultate)
        self.voltage_profile = []
        self.ampere_profile = []

    def simulate(self, power_profile: list[float], duration_profile: list[float]) -> None:
        """
        Simuliert den Ladezustand der Batterie über bestimmte Zeitabschnitte.
        """
        logging.info("Starte Simulation der Route...")
        # Listen leeren, falls die Simulation mehrmals gestartet wird
        self.voltage_profile = []
        self.ampere_profile = []
        
        # Initialisierung: Erste Spannung bei t=0 eintragen
        self.voltage_profile.append(self.battery.voltage())

        # Schleife über alle Zeiten
        for p, d in zip(power_profile, duration_profile):

            # Aktuelle Spannng abfragen
            current_voltage = self.battery.voltage()

            # Den Motor nach benötigten Strom fragen
            i = self.e_motor.get_current_draw(power=p, voltage=current_voltage)

            # Sicherheitsabfrage ob Akku leer
            if self.battery.is_empty() and i > 0:
                logging.warning("Batterie ist leer :(")
                i = 0.0  # Strom auf 0 setzen, Akku leer

            elif self.battery.is_full() and i < 0:
                logging.warning("Batter ist voll :)")
                i = 0.0  # Ladestrom auf 0, Akku voll 

            # Stromverlauf speichern
            self.ampere_profile.append(i)

            # dem Akku mitteilen, wieviel und wie lange wir Strom gezogen haben, 
            # damit neuer SoC berechnet werden kann
            self.battery.apply_current(current=i, duration=d)

            # neuen SoC abfragen und in den Verlauf eintragen
            v = self.battery.voltage(current=i)
            self.voltage_profile.append(v)

    logging.info("Simulation erfolgreich durchgeführt.")
