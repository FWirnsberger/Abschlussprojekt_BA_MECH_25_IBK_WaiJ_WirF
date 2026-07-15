import numpy as np
from src.models.battery_pack import BatteryPack

class BatteryLiPo(BatteryPack):
    """
    Stellt eine LiPo Batterie dar (Lithium-Polymer).
    Erbt von der Battery Klasse.
    """
    def __init__(self, capacity_nom_Ah: float, initial_soc: float = 1.0):
        # LiPo, 8 mOhm pro Zelle * 10 = 80 mOhm Gesamtwiderstand
        # Vmin, Vmax und Vnom vom BatteryPack übernommen 
        super().__init__(
            capacity_nom_Ah = capacity_nom_Ah,
            internal_resistance_mOhm = 80.0,  
            initial_soc = initial_soc
        )

        # OCV-Kennlinien-Daten aus dem Datenblatt (X-Achse = SoC, Y-Achse = Spannung)
        self.soc_curve = [0.00, 0.04, 0.09, 0.13, 0.17, 0.21, 0.26, 0.30, 0.40, 0.52, 0.64, 0.76, 0.88, 1.00]
        self.ocv_curve = [32.00, 35.87, 36.85, 37.56, 37.87, 38.28, 38.81, 39.05, 39.55, 40.27, 40.70, 41.16, 41.65, 42.00]

    def voltage(self, current: float = 0.0) -> float:
        """
        Berechnet die Klemmenspannung mithilfe der OCV-Kennlinie und Interpolation.
        """
        # np.interp(gesuchter x wert, liste aller x werte, liste aller y werte)
        open_circuit_voltage = np.interp(self.soc, self.soc_curve, self.ocv_curve)
        
        # Klemmenspannung = OCV - (Strom * Innenwiderstand)
        return open_circuit_voltage - (self.R_int * current)