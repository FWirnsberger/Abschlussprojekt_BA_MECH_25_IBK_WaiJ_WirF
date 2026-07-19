import logging

class BatterySizing:
    """
    Hier wird der elektrische Energiebedarf und die notwendige Batteriekapazität für eine Strecke berechnet.
    """

    def __init__(self, 
                 nominal_voltage_v: float = 37,             #10 x 3,7 ergibt die nominale Spannung der Batterie
                 reserve_factor: float = 0.2)-> None:      #es wird mit 20% Reserve gerechnet
        """
        Argumente:
            nominal_voltage_v:  
                Nennspannung des ganzen Akkupacks mit 10 Zellen in Serie und 3,7V pro Zelle

            reserve_factor:
                Gibt die Energiereserve wieder.
        """

        #Fehlererkennung
        if nominal_voltage_v <= 0:
            raise ValueError("Die Nennspannung muss größer 0 Volt sein!")
        
        if reserve_factor < 0:
            raise ValueError("Die Reserve muss größer 0 sein!")
        
        self.nominal_voltage_v = nominal_voltage_v
        self.reserve_factor = reserve_factor

    
    def calculate_energy_requirement(self, 
                                     motor_power_profile: list[float],
                                     duration_profile: list[float],
                                     motor_efficiency: list[float],
                                     )-> float:
        """
        Hier wird der elektrische Energiebedarf in Wh für die Strecke berechnet

        Argumente:
            motor_power_profile: 
                beinhaltet die mechanische Motorleistung pro Streckenabschnitt in Wh, Fahrerleistung nich berücksichtigt
            
            duration_profile: 
                beinhaltet die Dauer der einzelnen Streckenabschnitte

            motor_efficiency: 
                Motorwirkungsgrad zwischen 0 und 1 zulässsig

        Returns:
            total_energy_wh:
                elektrische Energiebedarf in Wh
        """

        #Fehlererkennung
        if len(motor_power_profile) != len(duration_profile):
            raise ValueError("Leistungs- und Zeitprofil müssen gleich lang sein!")
        
        if not 0 < motor_efficiency < 1:
            raise ValueError("Der Motorwirkungsgrad muss zwischen 0 und 1 liegen!")
        
        total_energy_wh = 0.0

        for motor_power, duration in zip(motor_power_profile, duration_profile):
            if duration <= 0:
                continue        #aktueller Durchlauf wird übersprungen, wenn ein Zeitabschnitt 0 wäre

            mechanical_power = max(0.0, motor_power)        #wir haben keine Rekuperation beim EBike, daher keine negative Leistung am Motor

            electrical_power = mechanical_power / motor_efficiency  #Elektrische Leistung die der Akku abgeben muss

            energy_wh = electrical_power *  duration / 3600

            total_energy_wh += energy_wh

        logging.info("Elektrischer Energiebedarf wurde berechnet.")

        return total_energy_wh
    

    def calculate_required_energy(self, energy_requirement_wh: float) -> float:
        """
        hier wird die Energiereserve zum Energiebedarf hinzugerechnet

        Argumente:
            energy_requirement_wh:
                Energiebedarf ohne Reserve

        Returns:
            Batterieenergie inkl. Reserve
        """
        
        #Fehlererkennung
        if energy_requirement_wh < 0:
            raise ValueError("Der Energiebedarf muss größer 0 sein und darf nicht negativ sein!")
        
        required_energy_wh = energy_requirement_wh * (1.0 + self.reserve_factor)

        return required_energy_wh
    
    def calculate_required_capacity_ah(self, required_energy_wh: float)-> float:
        """
        Hier wird die Energiemenge in die Kapatzität umgerechnet.

        Formel zum Rechnen:
            C_Ah = E_Wh / U_V
        """

        #Fehlererkennung
        if required_energy_wh < 0:
            raise ValueError("Die benötigte Energie darf nicht negativ sein!")
        
        required_capacity_ah = (required_energy_wh / self.nominal_voltage_v)

        return required_capacity_ah
    