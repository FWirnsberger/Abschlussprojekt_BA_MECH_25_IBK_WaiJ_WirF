class Motor:
    """
    Model des Motors mit seinen physikalischen Eigenschaften 
    und den darasu berechneten elekt. Größen
    """

    def __init__(self,  motor_constant: float = 1.5, efficiency: float = 0.85):
        """
        Motor mit Motorkonstante und Wirkungsgrad.
        """
        # Überprüfung des wirkungsgrads (muss zw. 0.0 und 1.0 liegen)
        if not (0.0 <= efficiency <= 1.0):
            raise ValueError("Der Wirkungsgrad muss zwischen 0.0 und 1.0 liegen!")
        # Öffentliche Attribute 
        self.motor_constant = motor_constant
        self.efficiency = efficiency


    def get_torque(self, force: float, wheel_radius: float) -> float:
        """
        Berechnet und gibt das Drehmoment zurück (in Nm) mit Antriebskraft und Radradius
        """
        return force * wheel_radius

    def get_current(self, torque: float) -> float:
        """
        Berechnet und gibt den benötigten Motorstrom zurück (in A) 
        mit Drehmoment und Motorkonstante.
        """
        return torque / self.motor_constant
    
    def get_current_draw(self, power: float, voltage: float) -> float:
        """
        Berechnet den benötigten Batteriestrom (in A) mit der 
        mechanischen Leistung (W), aktuellen Spannung (V) und dem Wirkungsgrad.
        """
        # Wenn keine Leistung benötigt wird
        if power <= 0.0:
            return 0.0

        # Elektrische Leistung berechnen (P_el = P_mech / eta)
        electric_power = power / self.efficiency

        # Stromstärke berechnen (I = P_el / U)
        current = electric_power / voltage
        
        return current