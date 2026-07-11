import logging
from route_data import RouteData

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

if __name__ == "__main__":
    main()