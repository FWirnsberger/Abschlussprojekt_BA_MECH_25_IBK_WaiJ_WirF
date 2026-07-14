from src.models.battery_pack import BatteryPack

class NMCBattery(BatteryPack):
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