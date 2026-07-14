from abc import ABC, abstractmethod


class BatteryBase(ABC):
    """
    Basisklasse für alle Batterietypen.
    Hier werden allgemeine Eigenschaften und Funktionen einer Batterie verwaltet.
    """

    @abstractmethod
    def __init__(self, capacity_nom_Ah: float, initial_soc: float = 1.0):
        self.C_nom = capacity_nom_Ah * 3600.0  # Kapazität in As
        self.soc = initial_soc
        self.R_int = 0.08
        self.Vmin = 32.0
        self.Vmax = 42.0
        self.Vnom = 37.0

    @abstractmethod
    def apply_current(self, current: float, duration: float) -> None:
        """
        Zieht oder lädt Strom über eine bestimmte Zeitdauer.
        Verändert den Ladezustand (SoC).
        """
        pass

    @abstractmethod
    def voltage(self, current: float = 0.0) -> float:
        """
        Gibt die aktuelle Spannung der Batterie unter Last zurück.
        """
        pass
