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

    def calculate_force_and_power(self, speed: float, acceleration: float, slope: float) -> tuple[float, float]:
        """
        Berechnet die benötigte Kraft [N] mechanische Leistung [W]
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
        
        return f_total, power