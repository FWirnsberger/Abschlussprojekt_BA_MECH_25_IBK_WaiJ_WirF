class Motor:
    """
    Model des Motors mit seinen physikalischen Eigenschaften 
    und den darasu berechneten elekt. Größen
    """

    def __init__(self,  
                 motor_constant: float = 1.5, 
                 efficiency: float = 0.85):
        """
        Motor mit Motorkonstante und Wirkungsgrad.
        """
        # Überprüfung des wirkungsgrads (muss zw. 0.0 und 1.0 liegen)
        if not (0.0 <= efficiency <= 1.0):
            raise ValueError("Der Wirkungsgrad muss zwischen 0.0 und 1.0 liegen!")
        
        if motor_constant <= 0:
            raise ValueError("Die Motorkonstante muss muss größer 0 sein")

        #  Öffentliche Attribute 
        self.motor_constant = motor_constant
        self.efficiency = efficiency

    def get_torque_from_power(self,
                              motor_power: float,
                              speed: float,
                              wheel_radius: float)-> float:
        """
        Hier wird nur das Motordrehmoment aus der mechanischen Motorleistung berechnet.

        Argumente:
            motor_power: 
                Leistung des Motors in W
            speed:
                Geschwindigkeit in m/s
            wheel_radius:
                Radradius in m
        """

        if motor_power <= 0.0:
            return 0.0
        
        if speed <= 0.1:
            return 0.0
        
        motor_force = motor_power / speed
        motor_torque = motor_force * wheel_radius

        return motor_torque


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
        #gegen 0 Division absichern
        if voltage <= 0.0:
            raise ValueError("Die Batteriespannung muss größer 0 V sein.")
    
        # Elektrische Leistung berechnen (P_el = P_mech / eta)
        electric_power = power / self.efficiency

        # Stromstärke berechnen (I = P_el / U)
        current = electric_power / voltage
        
        return current  