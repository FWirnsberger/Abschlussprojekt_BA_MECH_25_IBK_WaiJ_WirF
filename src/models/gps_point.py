from datetime import datetime
from src.calculations.geo_utils import GeoUtils

class GPSPoint:
    """Repräsentiert einen einzelnen GPS-Messpunkt."""

    def __init__(self, lat: float, lon: float, ele: float, time: datetime, temp: float):
        # _ im UML-Diagramm bedeutet "private". 

        self._lat = lat
        self._lon = lon
        self._ele = ele
        self._time = time
        self._temp = temp

    def get_distance_to(self, other: 'GPSPoint') -> float:
        """
        Berechnet die distanz (m) von diesem punkt zu einem anderen GPSPoint.
        """
        # GeoUtils aufrufen
        # (self) übergeben private Variablen von uns selber 
        # (other) Variablen von einem anderen Punkt an die haversine Formel übergeben

        return GeoUtils.haversine_distance(self._lat, self._lon, other._lat, other._lon)

             
    def get_time_difference_to(self, other: 'GPSPoint') -> float:
        """
        Gibt die Zeitdifferenz in sec. zu einem anderen punkt zurück.
        """
        # .total_seconds() wandelt die datetime-Differenz in echte Sekunden um
        dt = (other._time - self._time).total_seconds()
        return abs(dt) # abs() macht die Zeit immer positiv


    # "Getter", falls ich die Werte mal abfragen möchte
    @property
    def lat(self) -> float:
        return self._lat

    @property
    def lon(self) -> float:
        return self._lon
    
    @property
    def ele(self) -> float:
        return self._ele