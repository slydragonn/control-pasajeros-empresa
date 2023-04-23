import pandas as pd
import numpy as np

class Bus:
    def get_buses_data(self, data, bus_number:str):
        bus_data = data[(data['mDescription'] == bus_number) & (data['p_total'] != 'N')] 
        array_of_passengers = pd.DataFrame(bus_data.loc[:, ['regId', 'mDescription', 'p_doorId', 'p_ingresos', 'p_salidas', 'p_bloqueos', 'p_station', 'gps_datetime']]).to_numpy()
        
        return array_of_passengers


    def get_passengers(self, passengers_list:list):
        last_date = ''
        passengers = {}
        metro = ["049 - Metro", "051 - Metro", "052 - Metro", "057 - Metro", "058", "059", "064", "067 - Metro", "62 Metro"]
        
        for i in passengers_list:
            date = str(i[7][0:10])

            if date != last_date:
                passengers[date] = {"bus": i[1], "r": 0, "p1": 0, "d": 0, "p2": 0, "debe": 0, "novedades": [], "descuento": 0}
                

            if i[2] == 1 and ((i[6] != "Terminal Arrieritas") and (i[6] != "Terminal arrieritas") and (i[6] != "Respaldo")):
                passengers[date]["p1"] += i[3]


            if i[2] == 2:
                if (i[6] == "Terminal Arrieritas") or (i[6] == "Terminal arrieritas") or (i[6] == "Respaldo") or (i[5] > 9 and i[4] > 4):
                    passengers[date]["descuento"] += i[3]
                    continue


                if (i[3] > 4) or (i[5] > 4 and i[3] > 0) or ((i[4] > 1) and (i[3] > 0)):
                    passengers[date]["novedades"].append({"p2": i[3], "bloqueos": i[5],"salidas": i[4], "fecha": i[7], "lugar": i[6]})
                    

                if  (i[5] < 10 and i[4] < 5) and ((i[6] != "Terminal Arrieritas") and (i[6] != "Terminal arrieritas") and (i[6] != "Respaldo")):
                    passengers[date]["p2"] += i[3]


            last_date = str(i[7][0:10])

        for value in passengers.values():
            if value["bus"] in metro:
                if value["p1"] >= 320 and value["p2"] > 20:
                    value["debe"] = value["p2"] - 20
                if value["p1"] <= 319 and value["p2"] > 10:
                    value["debe"] = value["p2"] - 10
            else:
                if value["p1"] >= 250 and value["p2"] > 20:
                    value["debe"] = value["p2"] - 20
                if value["p1"] <= 249 and value["p2"] > 10:
                    value["debe"] = value["p2"] - 10
            

        return passengers
    

    def get_driver_data(self, drivers_data, bus_number):
        driver_data = drivers_data [(drivers_data['Vehículo'] == bus_number)]
        array_of_driver = pd.DataFrame(driver_data.loc[:, ["Vehículo", 'Fecha de Inicio', 'Conductor']]).to_numpy()
        return array_of_driver
    
    def get_driver_name(self, names_list: list):
        drivers = {}
        last_date = ''

        for i in names_list:
            date = str(i[1])[0:10]

            if date == 'nan':
                continue

            if date != last_date:
                drivers[date] = {"conductor": []}
            
            drivers[date]["conductor"].append(i[2])

            last_date = str(i[1])[0:10]

        for value in drivers.values():
            drivers_count = []
            for i in np.unique(value["conductor"]):
                drivers_count.append([i, value["conductor"].count(i)])

            last_value = {"count": 0, "name": ""}    
            for i in drivers_count:
                if last_value["count"] < i[1]:
                    value["conductor"] = i[0]
                    last_value["count"] = i[1]
                    last_value["name"] = i[0]
                else:
                    value["conductor"] = last_value["name"]

        return drivers
    

    def get_travels_data(self, data, bus_number:str):
        bus_data = data[(data['Vehículo'] == bus_number)]    
        travels_data = pd.DataFrame(bus_data.loc[:, ['Vehículo', 'Itinerario', 'Conductor', 'Fecha de Inicio', 'Fecha de Finalización', 'Tiempo de viaje(minutos)', 'Despachador']]).to_numpy()
        
        return travels_data
    
    def get_number_of_travels(self, travels_data:list):
        last_date = ''
        last_terminal = ''
        travel_number = 0
        travels = {}
        metro = ["049 - Metro", "051 - Metro", "052 - Metro", "057 - Metro", "058", "059", "064", "067 - Metro", "62 Metro"]

        for travel in reversed(travels_data):
            date = str(travel[3])[0:10]
            def myFunct(x):
                if x[0] == travel[0] and str(x[3])[0:10] == date and (x[6] == 'terminalarrieritas'):
                    return True
                else:
                    return False
                

            if date != last_date:
                travel_number = 0
                filtered = list(filter(myFunct, travels_data))
                travel_number = len(filtered)

                travels[date] = {
                    "ida": 
                    { "c": 0, "vm": 0, "vt": 0, "m": 0, "cr": 0, "total": 0}, 
                    "vuelta": 
                    {"c": 0, "vm": 0, "vt": 0, "m": 0, "cr": 0, "total": 0},
                    "novedades": [],
                    "despachos": [],
                    "metro": False
                }
                last_terminal = ''

            if (last_terminal == '') and (travel[6] != 'arrieritasws') and (not(travel[0] in metro)):
                jornada = "Mañana" if int(travel[4][11:13]) < 12 else "Tarde"
                travels[date]["despachos"].append({
                        "terminal": "Medellin",
                        "jornada": jornada,
                        "despachador": "Carlos Correa" if jornada == "Mañana" else "alexander gonzalez",
                        "empresa": "Arrieritas" if jornada == "Mañana" else "Mocatan",
                        "despachos": f'\nBUS {travel[0]}. no genero despacho en el {travel_number} viaje {travel[4][11:16]}'
                })

                travels[date]["novedades"].insert(0, f'BUS {travel[0]}. no genero despacho en el {travel_number} viaje {travel[4][11:16]}')


            if travel[6] == last_terminal and ((travel[1] != 'Minorista - La 50') and (travel[1] != 'Minorista - Variante')) and (travel[1] != 'Minorista - Tablaza Variante') and (not(travel[0] in metro)):
                if travel[6] == 'terminalarrieritas':
                    jornada = "Mañana" if int(travel[4][11:13]) < 12 else "Tarde"
                    travels[date]["despachos"].append({
                        "terminal": "Medellin",
                        "jornada": jornada,
                        "despachador": "Carlos Correa" if jornada == "Mañana" else "alexander gonzalez",
                        "empresa": "Arrieritas" if jornada == "Mañana" else "Mocatan",
                        "despachos": f'\nBUS {travel[0]}. no genero despacho en el {travel_number} viaje {travel[4][11:16]}'
                    })

                    travels[date]["novedades"].insert(0, f'BUS {travel[0]}. no genero despacho en el {travel_number} viaje {travel[4][11:16]}')
                
                if travel[6] == 'arrieritasws':
                    jornada = "Mañana" if int(travel[4][11:13]) < 12 else "Tarde"
                    travels[date]["despachos"].append({
                        "terminal": "Terminal",
                        "jornada": jornada,
                        "despachador": "Elkin cossio" if jornada == "Mañana" else "santiago Estrada",
                        "empresa": "Arrieritas",
                        "despachos": f'\nBUS {travel[0]}. no genero despacho en el {travel_number} viaje {travel[4][11:16]}'
                    })

                    travels[date]["novedades"].insert(0, f'BUS {travel[0]}. no genero despacho en el {travel_number} viaje {travel[4][11:16]}')
                    

            if (travel[1] != 'Minorista - La 50') and (travel[1] != 'Minorista - Variante') and (travel[1] != 'Minorista - Tablaza Variante'):
                last_terminal = travel[6]
            


            if travel[6] == 'terminalarrieritas':
                travel_number -= 1

                if ('Metro' in travel[1]) or (travel[1] == 'Circular'):
                    travels[date]["metro"] = True
                    if travel[1] == 'Variante Miel Metro' and (travel[5] > 40):
                        travels[date]["ida"]["vm"] += 1
                        travels[date]["ida"]["total"] += 1
                    if travel[1] == 'Variante tablaza Metro' and (travel[5] > 40):
                        travels[date]["ida"]["vt"] += 1
                        travels[date]["ida"]["total"] += 1
                    if travel[1] == 'Metro La 50' and (travel[5] > 40):
                        travels[date]["ida"]["c"] += 1
                        travels[date]["ida"]["total"] += 1
                    if travel[1] == 'Circular' and (travel[5] > 40):
                        travels[date]["ida"]["cr"] += 1
                        travels[date]["ida"]["total"] += 1
                    
                if travel[1] == 'Caldas - Medellin - Tablaza Variante' and (travel[5] > 40):
                    travels[date]["ida"]["vt"] += 1
                    travels[date]["ida"]["total"] += 1
                if travel[1] == 'Caldas - Medellin - Variante' and (travel[5] > 40):
                    travels[date]["ida"]["vm"] += 1
                    travels[date]["ida"]["total"] += 1
                if travel[1] == 'Caldas - Medellín - La 50' and (travel[5] > 40):
                    travels[date]["ida"]["c"] += 1
                    travels[date]["ida"]["total"] += 1
                if ((travel[1] == 'Minorista - La 50') or (travel[1] == 'Minorista - Variante') or (travel[1] == 'Minorista - Tablaza Variante')) and (travel[5] > 40):
                    travels[date]["ida"]["m"] += 1
                    travels[date]["vuelta"]["m"] += 1
                    travels[date]["ida"]["total"] += 1
                    travels[date]["vuelta"]["total"] += 1
                    
                

            if travel[6] == 'arrieritasws':
                if travel[1] == 'Variante Miel Caldas' and (travel[5] > 40):
                    travels[date]["vuelta"]["vm"] += 1
                    travels[date]["vuelta"]["total"] += 1
                if travel[1] == 'Variante Tablaza Caldas' and (travel[5] > 40):
                    travels[date]["vuelta"]["vt"] += 1
                    travels[date]["vuelta"]["total"] += 1
                if travel[1] == 'Medellin - Caldas' and (travel[5] > 40):
                    travels[date]["vuelta"]["c"] += 1
                    travels[date]["vuelta"]["total"] += 1

            last_date = str(travel[3])[0:10]
        

        for key in travels.keys():
            if not travels[key]["metro"]:
                if travels[key]["ida"]["total"] == travels[key]["vuelta"]["total"]:
                    travels[key]["despachos"] = False

        
        return travels