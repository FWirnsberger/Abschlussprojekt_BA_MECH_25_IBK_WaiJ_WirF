import numpy as np
from src.models.battery_pack import BatteryPack

class BatteryNMC(BatteryPack):
    """
    Stellt eine NMC Batterie dar (Nickel-Mangan-Cobalt).
    Erbt von der Battery Klasse.
    """
    def __init__(self, capacity_nom_Ah: float, initial_soc: float = 1.0):
        # NMC, 7 mOhm pro Zelle * 10 = 70 mOhm Gesamtwiderstand.
        # Vmin, Vmax und Vnom vom BatteryPack übernommen 
        super().__init__(
            capacity_nom_Ah = capacity_nom_Ah,
            internal_resistance_mOhm = 70.0, 
            initial_soc = initial_soc
        )

        # OCV-Kennlinien-Daten aus dem Datenblatt (X-Achse = SoC, Y-Achse = Spannung)
        self.soc_curve = [0.00, 0.04, 0.09, 0.13, 0.17, 0.21, 0.26, 0.30, 0.40, 0.52, 0.64, 0.76, 0.88, 1.00]
        self.ocv_curve = [32.00, 32.61, 33.17, 33.85, 34.24, 34.66, 35.39, 35.65, 36.65, 37.64, 38.91, 40.14, 41.08, 42.00]

    def voltage(self, current: float = 0.0) -> float:
        """
        Berechnet die Klemmenspannung mithilfe der OCV-Kennlinie und Interpolation.
        """
        # np.interp(gesuchter x wert, liste aller x werte, liste aller y werte)
        open_circuit_voltage = np.interp(self.soc, self.soc_curve, self.ocv_curve)
        
        # Klemmenspannung = OCV - (Strom * Innenwiderstand)
        return open_circuit_voltage - (self.R_int * current)