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
    
    print("\n----------Daten über die Fahrt:----------")
    print(f"Zurückgelegte Strecke: {total_distance_km:.2f} km")
   


if __name__ == "__main__":
    main()