class Motor:
    """
    Model des Motors mit seinen physikalischen Eigenschaften 
    und den darasu berechneten elekt. Größen
    """

    def __init__(self,  motor_constant: float = 1.5):
        
        # Öffentliche Attribute 
        self.motor_constant = motor_constant
            

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