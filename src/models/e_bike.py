class EBike:
    """
    Model des e-bikes mit seinen physikalischen Eigenschaften.
    """

    def __init__(self, rider_mass: float = 70.0, bike_mass: float = 10.0, 
                 cw_a: float = 0.5625, wheel_diameter_inch: float = 27.0, motor_constant: float = 1.5):
        
        # Öffentliche Attribute 
        self.rider_mass = rider_mass
        self.bike_mass = bike_mass
        self.cw_a = cw_a
        self.wheel_diameter_inch = wheel_diameter_inch
        self.motor_constant = motor_constant        
        # Für später
        self.battery = None
        self.motor = None

    def get_total_mass(self) -> float:
        """
        Berechnet und gibt die Gesamtmasse zurück.
        """
        return self.rider_mass + self.bike_mass

    def get_wheel_radius_m(self) -> float:
        """
        Umrechnung des Raddurchmessers von inch in meter und /2 für Radius
        (1 Zoll = 0.0254 Meter)
        """
        diameter_m = self.wheel_diameter_inch * 0.0254
        return diameter_m / 2.0