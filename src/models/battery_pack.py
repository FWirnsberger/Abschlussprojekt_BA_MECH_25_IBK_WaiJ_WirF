from battery_base import BatteryBase

class BatteryPack(BatteryBase):
    """
    Berechnet die Spannung anhand des SoC (State of Charge).
    """
    def __init__(
        self,
        capacity_nom_Ah: float,
        internal_resistance_mOhm: float,
        initial_soc: float = 1.0,
        # Achtung in der Angabe Vmin und Vmax ist pro Zelle angegeben -> mal 10
        Vmin: float = 32.0 ,
        Vmax: float = 42.0,
        Vnom: float = 37.0
    ):
        
        # Kapazität in As umrechnen (Amperestunden * 3600 Sekunden)
        self.C_nom = capacity_nom_Ah * (60.0 * 60.0)
        # SoC (State of Charge) muss zwischen 0.0 (0%) und 1.0 (100%) liegen
        self.soc = max(0.0, min(initial_soc, 1.0))
        # Innenwiderstand von Milliohm in Ohm umrechnen
        self.R_int = internal_resistance_mOhm * 1e-3

        self.Vmin = Vmin
        self.Vmax = Vmax
        self.Vnom = Vnom
        

    def apply_current(self, current: float, duration: float) -> None:
        """
        Aktualisiert den Ladezustand.
        current > 0 -> entladen
        current < 0 -> laden
        """
        # dsoc = Änderung des Ladezustands
        dsoc = -(current * duration) / self.C_nom
        self.soc = max(0.0, min(self.soc + dsoc, 1.0))

    def voltage(self, current: float = 0.0) -> float:
        """
        Berechnet die Klemmenspannung: Leerlaufspannung minus Spannungsabfall am Innenwiderstand.
        """
        open_circuit_voltage = self.Vmin + self.soc * (self.Vmax - self.Vmin)
        return open_circuit_voltage - self.R_int * current
    
    def is_empty(self) -> bool:
        """Abfrage, ob die Batterie leer ist."""
        return self.soc <= 1e-9

    def is_full(self) -> bool:
        """Abfrage, ob die Batterie voll ist."""
        return self.soc >= 1.0 - 1e-9

    def __str__(self) -> str:
        """gibt die aktuellen Daten der Batterie aus"""
        return f"BatteryPack(SoC={self.soc * 100:.1f}%, V={self.voltage():.2f} V)"