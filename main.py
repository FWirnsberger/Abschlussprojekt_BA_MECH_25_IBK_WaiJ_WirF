import logging
from src.calculations.route_data_kinematics import RouteData
from src.models.gps_point import GPSPoint
from src.models.e_bike import EBike
from src.models.motor import Motor
from src.models.battery_lipo import BatteryLiPo
from src.models.battery_nmc import BatteryNMC
from src.calculations.e_bike_physics import EBikePhysics
from src.simulation.e_bike_simulator import EBikeSimulator
from src.calculations.battery_sizing import BatterySizing

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
    route.filter_speed(window_size=5)       #Geschwindigkeit mit Fenstergröße 5 filtern
    route.calculate_acceleration(max_acceleration_m_s2=1.0) #Beschleunigung aus der gefilterten Geschwindigkeit berechnen und auf ±3.5 m/s² begrenzen

    
    # Test ob Daten richtig sind
    print(route.data[['time', 'distance_m', 'speed_raw_m_s', 'speed_m_s', 'acceleration_raw_m_s2', 'acceleration_m_s2', 'slope']].head(10))
    
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
    formated_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    #Durchschnittsgeschwindigkeit berechnen
    average_speed_m_s= route.calculate_average_speed(total_distance_m, total_time_s)
    average_speed_km_h = average_speed_m_s * 3.6
    
    #Anstieg, Abstieg berechnen
    total_ascent, total_descent = route.calculate_total_elevation()

    #Ausgabe der statischen Werte
    print("\n----------Daten über die Fahrt:----------")
    print(f"Zurückgelegte Strecke: {total_distance_km:.2f} km")
    print(f"Benötigte Zeit: {formated_time}")
    print(f"Durchschnittsgeschwindigkeit: {average_speed_km_h:.2f} km/h")
    print(f"Anstieg: {total_ascent:.2f} m")
    print(f"Abstieg: {total_descent:.2f} m")

    #---------------------------------------------------------------
    # Hier startet die E-Bike Simulation
    #---------------------------------------------------------------
    print("\n---------- Simulation startet ----------")

    #Unsere Objekte benennen
    my_bike = EBike(rider_mass = 70.0,        #70 kg Fahrer
                    bike_mass = 10.0,         #10 kg Bike
                    rider_power_w = 100)      #100 Watt leistet der Fahrer maximal

    my_motor = Motor(motor_constant = 1.5, 
                     efficiency = 0.85) # 85% Wirkungsgrad
      
    physics = EBikePhysics(ebike = my_bike)

    #Listen für den Simulator vorbereiten
    total_power_profile: list[float] = []
    rider_power_profile: list[float] = []
    motor_power_profile: list[float] = []
    motor_torque_profile: list[float] = []
    motor_current_profile: list[float] = []
    
    duration_profile: list[float] = []

    #Radradius für die Momenten Berechnung
    wheel_radius_m = my_bike.get_wheel_radius_m()

    # Die Routendaten (Pandas Tabelle) durchlaufen
    # Wir starten bei Index 1, da wir für das Delta_t den Abstand zum vorherigen Punkt brauchen
    for i in range(1, len(route.data)):
        
        
        # Werte aus der Tabelle auslesen
        speed = route.data.loc[i, 'speed_m_s']
        acceleration = route.data.loc[i, 'acceleration_m_s2']
        slope = route.data.loc[i, 'slope']
        dt = route.data.loc[i, 'delta_time_s']
        duration_profile.append(dt)
        
        
        #1. Schritt: gesamte mechanische Leistung berechen (Fahrer und Motor)
        total_power = physics.calculate_power(
            speed=speed,
            acceleration=acceleration,
            slope=slope
        )

        #2. Schritt: Leistung auf Fahrer und Motor aufteilen
        rider_power, motor_power = physics.split_power(total_power=total_power)

        #3. Schritt: Motordrehmoment berechnen (hier wird nur die motor_power übergeben, ohne Fahrerleitstung)
        motor_torque = my_motor.get_torque_from_power(
            motor_power=motor_power,
            speed=speed,
            wheel_radius=wheel_radius_m    
        )

        #4. Schritt: Motorstrom wird über das Motormoment berechnet
        motor_current = my_motor.get_current(torque=motor_torque)

        #Ergebnisse in den erstellten Listen speichern
        total_power_profile.append(total_power)
        rider_power_profile.append(rider_power)
        motor_power_profile.append(motor_power)
        motor_torque_profile.append(motor_torque)
        motor_current_profile.append(motor_current)

#Werte für die Diagramme im DataFrame speichern
    route.data["total_power_w"] = ([0.0] + total_power_profile)
    route.data["rider_power_w"] = ([0.0] + rider_power_profile)
    route.data["motor_power_w"] = ([0.0] + motor_power_profile)
    route.data["motor_torque_nm"] = ([0.0] + motor_torque_profile)
    route.data["motor_current_a"] = ([0.0] + motor_current_profile)

#Maximalwerte Berechnen, vielleicht zeichne ich die Punkte in den Diagrammen ein
    #Maximale Gesamtleistung
    max_total_power_w = physics.calculate_max_power(total_power_profile)

    #Maximale Fahrerleistung
    max_rider_power_w = physics.calculate_max_power(rider_power_profile)

    #Maximale Motorleistung
    max_motor_power_w = physics.calculate_max_power(motor_power_profile)

    #Maximales Motordrehmoment
    max_motor_torque_nm = max(motor_torque_profile, default=0.0)

    #Maximaler Motorstrom
    max_motor_current_a = max(motor_current_profile, default=0.0)

#Maximalwerte ausgeben
    print("\n---------- Leistungsdaten ----------")
    print(
        f"Maximale Gesamtleistung: "
        f"{max_total_power_w:.2f} W"
    )
    print(
        f"Maximale Fahrerleistung: "
        f"{max_rider_power_w:.2f} W"
    )
    print(
        f"Maximale Motorleistung: "
        f"{max_motor_power_w:.2f} W"
    )
    print(
        f"Maximales Motordrehmoment: "
        f"{max_motor_torque_nm:.2f} Nm"
    )
    print(
        f"Maximaler Motorstrom: "
        f"{max_motor_current_a:.2f} A"
    )

    #--------------------------------------------------------------------------------    
    #Energiebedarf und Batteriekapazität berechnen
    #--------------------------------------------------------------------------------
    battery_sizing = BatterySizing(nominal_voltage_v = 37.0, reserve_factor = 0.2)
    
    #Elektrischer Energiebedarf der Strecke ohne Reserve
    energy_requirement_wh = (
        battery_sizing.calculate_energy_requirement(
            motor_power_profile = motor_power_profile,
            duration_profile = duration_profile,
            motor_efficiency = my_motor.efficiency
        )
    )

    #benötigte Energie inkl der verwendeten Reserve
    required_energy_wh = (
        battery_sizing.calculate_required_energy(
            energy_requirement_wh = energy_requirement_wh
        )
    )

    #benötigte Batteriekapazität in Ah bei 37 V
    required_capacity_ah = (
        battery_sizing.calculate_required_capacity_ah(
            required_energy_wh = required_energy_wh
        )
    )

    print("\n---------- Batterieauslegung ----------")
    print(
        f"Elektrischer Energiebedarf der Strecke: "
        f"{energy_requirement_wh:.2f} Wh"
    )
    print(
        f"Gewählte Reserve: "
        f"{battery_sizing.reserve_factor * 100:.0f} %"
    )
    print(
        f"Benötigte Batterieenergie inklusive Reserve: "
        f"{required_energy_wh:.2f} Wh"
    )
    print(
        f"Benötigte Batteriekapazität bei "
        f"{battery_sizing.nominal_voltage_v:.1f} V: "
        f"{required_capacity_ah:.2f} Ah"
    )

    battery_lipo = BatteryLiPo(capacity_nom_Ah = required_capacity_ah, 
                               initial_soc = 1.0) #  100% voll
    
    battery_nmc = BatteryNMC(capacity_nom_Ah = required_capacity_ah, 
                             initial_soc = 1.0) #  100% voll
    
    #--------------------------------------------------------------------------------    
    #Simulation für LiPo
    #--------------------------------------------------------------------------------
    print("\nStarte Simulation für LiPo Akku")

    my_battery = battery_lipo

    #Simulator starten
    simulator_lipo = EBikeSimulator(e_bike = my_bike, battery = battery_lipo, e_motor = my_motor)
    simulator_lipo.simulate(motor_power_profile = motor_power_profile, duration_profile = duration_profile)
    
    # Lipo ergebnisse für Plot speichern
    # Strom war in der schleife, also [0.0] davor. Voltage und SoC haben den schon den richtigen startwert.
    route.data['current_A_lipo'] = [0.0] + simulator_lipo.ampere_profile
    route.data['voltage_V_lipo'] = simulator_lipo.voltage_profile
    route.data['soc_lipo'] = simulator_lipo.soc_profile
    
    #Ergebnisse ausgeben
    print("Simulation für LiPO fertig.")
    #mit __str__ im battery_pack wird der verbleibende SoC und SPannung berechnet
    #Ergebnisse ausgeben
    print(f"Ergebnis LiPo: {battery_lipo}")  
    #--------------------------------------------------------------------------------
    #Simulation für NMC
    #--------------------------------------------------------------------------------
    print("\nSimulation für NMC Akku")

    my_battery = battery_nmc
    #Simulator starten
    simulator_nmc = EBikeSimulator(e_bike = my_bike, battery = battery_nmc, e_motor = my_motor)
    simulator_nmc.simulate(motor_power_profile = motor_power_profile, duration_profile = duration_profile)

    # NMC ergebnisse für Plot speichern
    # Strom war in der schleife, also [0.0] davor. Voltage und SoC haben den schon den richtigen startwert.
    route.data['current_A_nmc'] = [0.0] + simulator_nmc.ampere_profile
    route.data['voltage_V_nmc'] = simulator_nmc.voltage_profile
    route.data['soc_nmc'] = simulator_nmc.soc_profile
    #Ergebnisse ausgeben
    print("Simulation fertig")
    print(f"Ergebnis NMC: {battery_nmc}")   
    print()


    # brauchen wir nicht mehr, da im battery_pack das mit __str__ ausgegeben wird 
    #print(f"Verbleibender Akku (SoC): {current_battery.soc * 100:.2f} %")
    #print(f"Endspannung unter Last:   {current_battery.voltage():.2f} V")
    #---------------------------------------------------------------

    #---------------------------------------------------------------
    #Hier werden die Plots und der Bericht erstellt
    #---------------------------------------------------------------
    plot_generator = PlotGenerator(data = route.data, output_folder = "output/figures")
    speed_plot_path = plot_generator.create_speed_plot()
    acceleration_plot_path = plot_generator.create_acceleration_plot()
    power_plot_path = plot_generator.create_power_plot()
    motor_torque_plot_path = plot_generator.create_motor_torque_plot()
    motor_current_plot_path = plot_generator.create_motor_current_plot()
    soc_plot_path = plot_generator.create_soc_plot()
    voltage_plot_path = plot_generator.create_voltage_plot()
    elevation_plot_path = plot_generator.create_elevation_plot()
    
    report_generator = ReportGenerator(         #es wird ein neues Bericht Objekt erstellt und der Ausgabeordner und Titel festgelegt
        output_directory = "output/report", 
        title = "Auswertung der Fahrradsimulation"
    )

    #----------------Grafiken hinzufügen--------------------
    report_generator.add_figure(                #die erstellte Geschwindigkeitsgrafik wird hinzugefügt
        image_path=speed_plot_path,
        caption="Geschwindigkeitsverlauf während der gesamten Fahrt.",
        label="fig:speed-profile"
    )
        # Beschleunigungsverlauf
    report_generator.add_figure(
        image_path=acceleration_plot_path,
        caption="Beschleunigungsverlauf während der gesamten Fahrt.",
        label="fig:acceleration-profile"
    )

    # Leistungsverlauf
    report_generator.add_figure(
        image_path=power_plot_path,
        caption=(
            "Verlauf der mechanischen Gesamtleistung sowie der "
            "Fahrer- und Motorleistung."
        ),
        label="fig:power-profile"
    )

    # Motordrehmoment
    report_generator.add_figure(
        image_path=motor_torque_plot_path,
        caption="Verlauf des vom Motor erzeugten Drehmoments.",
        label="fig:motor-torque-profile"
    )

    # Motorstrom
    report_generator.add_figure(
        image_path=motor_current_plot_path,
        caption="Verlauf des aus dem Motordrehmoment berechneten Motorstroms.",
        label="fig:motor-current-profile"
    )

    # Ladezustand
    report_generator.add_figure(
        image_path=soc_plot_path,
        caption="Vergleich des Ladezustands von LiPo- und NMC-Batterie.",
        label="fig:soc-profile"
    )

    # Batteriespannung
    report_generator.add_figure(
        image_path=voltage_plot_path,
        caption="Vergleich der Spannungsverläufe von LiPo- und NMC-Batterie.",
        label="fig:voltage-profile"
    )

    # Höhenprofil
    report_generator.add_figure(
        image_path=elevation_plot_path,
        caption="Höhenprofil entlang der zurückgelegten Strecke.",
        label="fig:elevation-profile"
    )

    #----------------Kennwerte für die ZUsammenfassung hinzufügen--------------------
    report_generator.add_summary_value("Gesamtstrecke", f"{total_distance_km:.2f} km")    
    report_generator.add_summary_value("Fahrzeit", formated_time)
    report_generator.add_summary_value("Durchschnittsgeschwindigkeit", f"{average_speed_km_h:.2f} km/h")
    report_generator.add_summary_value("Anstieg", f"{total_ascent:.1f} m")
    report_generator.add_summary_value("Abstieg", f"{total_descent:.1f} m")
    report_generator.add_summary_value("Maximale Gesamtleistung", f"{max_total_power_w:.1f} W")
    report_generator.add_summary_value("Maximale Motorleistung", f"{max_motor_power_w:.1f} W")
    report_generator.add_summary_value("Elektrischer Energiebedarf", f"{energy_requirement_wh:.1f} Wh")
    report_generator.add_summary_value("Batterieenergie inkl. Reserve", f"{required_energy_wh:.1f} Wh")
    report_generator.add_summary_value("Erforderliche Batteriekapazität", f"{required_capacity_ah:.2f} Ah")
    report_generator.add_summary_value("LiPo End-SoC", f"{battery_lipo.soc * 100:.1f} \\%")
    report_generator.add_summary_value("LiPo Endspannung", f"{battery_lipo.voltage():.2f} V")
    report_generator.add_summary_value("NMC End-SoC", f"{battery_nmc.soc * 100:.1f} \\%")
    report_generator.add_summary_value("NMC Endspannung",f"{battery_nmc.voltage():.2f} V")
    

    tex_path = report_generator.create_tex_file()
    pdf_path = report_generator.export_pdf(tex_path)

    print(f"PDF-Bericht erstelle: {pdf_path}")



if __name__ == "__main__":
    main()