import logging
from src.calculations.route_data_kinematics import RouteData
from src.models.gps_point import GPSPoint
from src.models.e_bike import EBike
from src.models.motor import Motor
from src.models.battery_lipo import BatteryLiPo
from src.calculations.e_bike_physics import EBikePhysics
from src.simulation.e_bike_simulator import EBikeSimulator

#für Plots
from src.reporting.plot_generator import PlotGenerator
from src.reporting.report_generator import ReportGenerator


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
    print() #Absatz
    route.calculate_kinematics()

    # Test ob Daten richtig sind
    print(route.data[['time', 'distance_m', 'speed_m_s', 'acceleration_m_s2', 'slope']].head())

    #---------------------------------------------------------------
    #Hier werden die statischen Parameter berechnet
    #---------------------------------------------------------------

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

    #Durchschnittsgeschwindigkeit berechnen
    average_speed_m_s= route.calculate_average_speed(total_distance_m, total_time_s)
    average_speed_km_h = average_speed_m_s * 3.6
    
    #Anstieg, Abstieg berechnen
    total_ascent, total_descent = route.calculate_total_elevation()

    #Ausgabe der statischen Werte
    print("\n----------Daten über die Fahrt:----------")
    print(f"Zurückgelegte Strecke: {total_distance_km:.2f} km")
    print(f"Benötigte Zeit: {hours:02d}h {minutes:02d} min {seconds:02d} s")
    print(f"Durchschnittsgeschwindigkeit: {average_speed_km_h:.2f} km/h")
    print(f"Anstieg: {total_ascent:.2f} m")
    print(f"Abstieg: {total_descent:.2f} m")

    #---------------------------------------------------------------
    # Hier startet die E-Bike Simulation
    #---------------------------------------------------------------
    print("\n---------- Simulation startet ----------")

    #Unsere Objekte benennen
    my_bike = EBike(rider_mass=75.0, bike_mass=25.0) # 75 kg Fahrer, 25 kg Bike
    my_motor = Motor(motor_constant=1.5, efficiency=0.85) # 85% Wirkungsgrad
    my_battery = BatteryLiPo(capacity_nom_Ah=50.0, initial_soc=1.0) # 15 Ah Akku, 100% voll
    
    physics = EBikePhysics(ebike=my_bike)

    #Listen für den Simulator vorbereiten
    power_profile = []
    duration_profile = []

    # Die Routendaten (Pandas Tabelle) durchlaufen
    # Wir starten bei Index 1, da wir für das Delta_t den Abstand zum vorherigen Punkt brauchen
    for i in range(1, len(route.data)):
        
        # Dauer dieses Streckenabschnitts berechnen (in Sekunden)
        t_current = route.data.loc[i, 'time']
        t_previous = route.data.loc[i-1, 'time']
        dt = (t_current - t_previous).total_seconds()
        duration_profile.append(dt)
        
        # Werte aus der Tabelle auslesen
        v = route.data.loc[i, 'speed_m_s']
        a = route.data.loc[i, 'acceleration_m_s2']
        s = route.data.loc[i, 'slope']
        
        # Mechanische Leistung vom Physik-Rechner berechnen lassen
        p_mech = physics.calculate_power(speed=v, acceleration=a, slope=s)
        power_profile.append(p_mech)
        
         

    #Simulator starten
    simulator = EBikeSimulator(e_bike=my_bike, battery=my_battery, e_motor=my_motor)
    simulator.simulate(power_profile=power_profile, duration_profile=duration_profile)

    #Ergebnisse ausgeben
    print("Simulation erfolgreich beendet!")
    print(f"Verbleibender Akku (SoC): {my_battery.soc * 100:.2f} %")
    print(f"Endspannung unter Last:   {my_battery.voltage():.2f} V")
    #---------------------------------------------------------------

    #---------------------------------------------------------------
    #Hier werden die Plots und der Bericht erstellt
    #---------------------------------------------------------------
    plot_generator = PlotGenerator(data = route.data, output_folder = "output/figures")
    speed_plod_path = plot_generator.create_speed_plot()
    
    report_generator = ReportGenerator(         #es wird ein neues Bericht Objekt erstellt und der Ausgabeordner und Titel festgelegt
        output_directory = "output/report", 
        title = "Auswertung der Fahrradsimulation"
    )

    report_generator.add_figure(                #die erstellte Geschwindigkeitsgrafik wird hinzugefügt
        image_path=speed_plod_path,
        caption="Geschwindigkeitsverlauf während der gesamten Fahrt.",
        label="fig:speed-profile"
    )

    tex_path = report_generator.create_tex_file()
    pdf_path = report_generator.export_pdf(tex_path)

    print(f"PDF-Bericht erstelle: {pdf_path}")



if __name__ == "__main__":
    main()