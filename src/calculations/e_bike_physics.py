from src.models.e_bike import EBike

class EBikePhysics:
    """
    Zuständig für die physikalischen Berechnungen (Kräfte und Leistung).
    """

    def __init__(self, ebike: EBike) -> None:
        # Wir speichern uns das übergebene Fahrrad-Objekt. 
        # für später um zb. die Masse abfragen
        self.ebike = ebike
        
        # Physikalische Konstanten (als Type Hint direkt mit : float versehen)
        self.rho = 1.225  # Luftdichte in kg/m³
        self.g = 9.81     # Erdbeschleunigung in m/s²

    def calculate_power(self, 
                        speed: float, 
                        acceleration: float, 
                        slope: float) -> float:
        """
        Berechnet die benötigte mechanische Leistung (P = F * v) [W]

        Argumente:
            speed:
                Geschwindigkeit in m/s
            acceleration:
                Beschleunigung in m/s2
            slope:
            Steigung als Verhältnis (z.B: 0.05 = 5 % Steigung)
        """

        # Gesamtmasse abrufen
        mass = self.ebike.get_total_mass()
        
        # beschleunigungswiderstand (F = m * a)
        acceleration_force = mass * acceleration
        
        # steigungswiderstand (F = m * g * steigung)
        slope_force = mass * self.g * slope
        
        # luftwiderstand (F = 0.5 * rho * cw_a * v^2)
        drag_force = 0.5 * self.rho * self.ebike.cw_a * (speed ** 2)
        
        #Gesamtkraft
        total_force = acceleration_force + slope_force + drag_force
        
        #Mechanische Gesamtleistung (Fahrer und Motor)
        total_power = total_force * speed
        
        return total_power
    
    def split_power(self, total_power: float) -> tuple[float, float]:
        """
        Hier wird die benötigte Gesamtleistung auf Fahrer und Motor aufgeteilt.
        Der Fahrer liefert max. die in e_bike.py eingetragene Leistung, den Rest liefert der Motor.

        Argumente:
            total_power:
                gesamte benötigte mechanische Leistung in W
            
        Returns:
            Tuple bestehend aus 
                - Fahrerleistung in W
                - Motorleistung in W
        """

        #benötigte Leistung definieren
        required_power = max(0.0, total_power)      #kmax gibt den größeren Wert der zwei Variablen aus, das EBike hat keine Rekuperation daher kleinster Wert 0

        #die Leistung des Fahrers einstellen
        rider_power = min(self.ebike.rider_power_w, required_power)     #Hier wird der kleinere der beiden Werte als Fahrerleistung gespeichert

        #Leistung des Motors, er liefert den Rest
        motor_power = max(0.0, required_power - rider_power)

        return rider_power, motor_power

    
    def calculate_max_power(self, power_profile: list[float]) -> float:
        """
        Hier wird die maximale Leistung während der Fahrt berechnet.

        Argumente:
            power_profile (list[float]):
                ist eine Liste mit den berechneten Leistungen zwischen den GPS Punkten in Watt

        Returns:
            float mit der maximalen Mechanischen Leistung in Watt
        """

        #Fehlererkennung
        if not power_profile:       #falls keine Leistungswerte vorhanden sind
            return 0.0
        
        max_power = max(power_profile)

        return max_power
