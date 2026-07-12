import logging
from src.calculations.route_data_kinematics import RouteData
from src.models.gps_point import GPSPoint

logging.basicConfig(format="%(asctime)s:%(levelname)s: %(message)s",
                    level=logging.INFO,)
 #                   filename="app.log")
 # fürs fertige Programm in die File app.log alle Meldungen schreiben

def main():
    
    # Pfad für die CSV Daten
    path = "data/final_project_input_data.csv" 
    
    #RouteData - Objekt erstellen
    route = RouteData(path)

    #GPS-Daten laden
    route.load_data()

    #Teilstrecken, Geschwindigkeiten, Beschleunigungen und Steigungen berechnen
    print()
    route.calculate_kinematics()

    # Test ob Daten richtig sind
    print(route.data[['time', 'distance_m', 'speed_m_s', 'acceleration_m_s2', 'slope']].head())

    #gesamt Strecke berechnen
    total_distance_m = route.calculate_total_distance()
    total_distance_km = total_distance_m / 1000

    #benötigte Zeit berechnen
    total_time_s = route.calculate_total_time()

    total_time_min = total_time_s / 60
    total_time_h = total_time_s / 3600

    hours = int(total_time_s // 3600)     #// ganz Zahlige Division; % gibt den Rest aus
    minutes = int((total_time_s % 3600) // 60)
    seconds = int(total_time_s % 60)

    #Ausgabe der statischen Werte
    print("\n----------Daten über die Fahrt:----------")
    print(f"Zurückgelegte Strecke: {total_distance_km:.2f} km")
    print(f"Benötigte Zeit: {hours:02d}h {minutes:02d} min {seconds:02d} s")


if __name__ == "__main__":
    main()