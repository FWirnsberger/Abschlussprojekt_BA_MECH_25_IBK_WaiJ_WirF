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