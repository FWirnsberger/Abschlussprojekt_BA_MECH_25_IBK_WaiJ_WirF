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

    def calculate_power(self, speed: float, acceleration: float, slope: float) -> float:
        """
        Berechnet die benötigte mechanische Leistung (P = F * v) [W]
        """

        # Gesamtmasse abrufen
        m = self.ebike.get_total_mass()
        
        # beschleunigungswiderstand (F = m * a)
        f_a = m * acceleration
        
        # steigungswiderstand (F = m * g * steigung)
        f_s = m * self.g * slope
        
        # luftwiderstand (F = 0.5 * rho * cw_a * v^2)
        f_d = 0.5 * self.rho * self.ebike.cw_a * (speed ** 2)
        
        # gesamtkraft berechnen
        f_total = f_a + f_s + f_d
        
        # leistung = F * v
        power = f_total * speed
        
        return power
    
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
