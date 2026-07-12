import logging
from datetime import datetime
from src.calculations.route_data_kinematics import RouteData
from src.models.gps_point import GPSPoint

logging.basicConfig(format="%(asctime)s:%(levelname)s: %(message)s",
                    level=logging.INFO,)
 #                   filename="app.log")
 # fürs fertige Programm in die File app.log alle Meldungen schreiben

def main():
    
    # Pfad für die CSV Daten
    path = "data/final_project_input_data.csv" 
    
    route = RouteData(path)
    route.load_data()
    route.calculate_kinematics()
    
    # Test ob Daten richtig sind
    print(route.data[['time', 'distance_m', 'speed_m_s', 'acceleration_m_s2', 'slope']].head())

    logging.info("Starte Programm...\n")
    
    # --- TESTBEREICH FÜR GPS POINT ---
    print("--- Teste GPSPoint Klasse ---")
    
    # Punkt 1 (Zeile 1 aus deiner CSV)
    punkt_A = GPSPoint(
        lat=47.583114, 
        lon=12.170826, 
        ele=494.88, 
        time=datetime(2024, 8, 23, 16, 21, 14), 
        temp=28.7
    )
    
    # Punkt 2 (Zeile 2 aus deiner CSV)
    punkt_B = GPSPoint(
        lat=47.582910, 
        lon=12.170766, 
        ele=494.88, 
        time=datetime(2024, 8, 23, 16, 21, 16), 
        temp=28.8
    )
    
    # Jetzt lassen wir die Objekte die Arbeit machen:
    distanz = punkt_A.get_distance_to(punkt_B)
    zeit_diff = punkt_A.get_time_difference_to(punkt_B)
    
    print(f"Punkt A liegt auf Höhe: {punkt_A.ele} m") # Hier nutzen wir den Getter!
    print(f"Distanz zwischen A und B: {distanz:.2f} Meter")
    print(f"Zeitunterschied: {zeit_diff} Sekunden")
    print(f"Geschwindigkeit in diesem Abschnitt: {(distanz/zeit_diff):.2f} m/s")
    print("-----------------------------\n")

if __name__ == "__main__":
    main()