"""Edits to bring original rosse geometry into AFN Single Sided Ventilation Example """

from helpers import diff
from schedules import * 
from icecream import ic 
ic.configureOutput(includeContext=True)

# ============================================================================ #
# ! Helpers 
def create_AFN_surface(name="Default"):
    return {
                "surface_name": name,
                "window_door_opening_factor_or_crack_factor": 1,
                "leakage_component_name": "SliderWindow"
            }
# TODO make doors reference crack => make door leakafe component...

def create_AFN_zone(name="Default"):
    return {
            "single_sided_wind_pressure_coefficient_algorithm": "Standard",
            "ventilation_control_mode": "Constant",
            "zone_name": name,
            }

def create_zoneventilation_object(name="Default"):
        return {
            "zone_or_space_name": name,
            "opening_area": 2.25, #m2
            # "opening_area_fraction_schedule_name": "Constant",
            "opening_effectiveness": "Autocalculate",
            "effective_angle": 0,
            # "discharge_coefficient_for_opening": "Autocalculate",

            }

# ============================================================================ # ! General 

def add_object(obj, model, fx, multiple=False):
    model[obj] = {}
    if multiple:
        for ix, name in enumerate(model["Zone"].keys()):
            model[obj][f"{obj} {ix+1}"] = fx(name)
    else:
        model[obj] = fx()
    return model 




def add_zone_vent(model):
        vent_obj = "ZoneVentilation:WindandStackOpenArea"
        nv_sched_name = "Nat Vent Sched"

        model = add_object(vent_obj, model, create_zoneventilation_object, multiple=True)
        
        model["Schedule:Compact"][nv_sched_name] = create_schedule_object()

        model[vent_obj][f"{vent_obj} 2"]["opening_area_fraction_schedule_name"] = nv_sched_name

        return model

# def add_matching_door(model):
#     return


# ============================================================================ #
# ! Rosse Openstudio Edits on AFN 

def rosse_on_afn(afn_model, rosse_model):
    model = afn_model.copy()
    # of the building defining properties, find the overlap 
    rosse_model_properties = ["BuildingSurface:Detailed", "FenestrationSurface:Detailed", "Construction", "Material", "Material:AirGap", 'Material:NoMass', "WindowMaterial:Glazing", "Zone", "GlobalGeometryRules"]

    afn_model_properties = ["BuildingSurface:Detailed", "FenestrationSurface:Detailed", "Construction", "Material", "Material:AirGap", "WindowMaterial:Gas", "WindowMaterial:Glazing", "Zone", "GlobalGeometryRules"]

    dif, un, inter = diff(rosse_model_properties, afn_model_properties)

    # afn model vals = rosse_mdel vals 
    for item in inter:
        model[item] = rosse_model[item]

    
    # fix the properties that are not in the intersection 
    # delete gas material...
    model.pop("WindowMaterial:Gas")
    # add material: no mass to afn_model 
    model['Material:NoMass'] = rosse_model["Material:NoMass"]


    # first delete all afn components to see how 
    props_afn = []
    for i in model.keys():
        if "AirflowNetwork" in i:
            props_afn.append(i)
            # print(i)

    for i in props_afn:
        model.pop(i)

    return model 


def add_afn_to_model(afn_model, model):
    # ~ add vent availability schedules
    closed_sched = "always_closed"
    model["Schedule:Compact"][closed_sched] = create_schedule_object(closed_sched)
    model["Schedule:File"] = {}
    model["Schedule:File"]["Window Operation"] = {
        "file_name": "/Users/julietnwagwuume-ezeoke/_UILCode/buildingEnergyModel/scripts/constants/annual_wo_sched.csv",
        "column_number": 2,
        "rows_to_skip_at_top": 1
    }

    # ~ define simulation control 
    # print(model.keys())
    model["AirflowNetwork:SimulationControl"] = afn_model["AirflowNetwork:SimulationControl"]

    # ~ define zones 
    # get an example 
    zone_ex = list(afn_model["AirflowNetwork:MultiZone:Zone"].items())[0][1]

    # modify example to use standard algorithm for single sided wind pressure 
    zone_ex["single_sided_wind_pressure_coefficient_algorithm"] = "Standard"
    zone_ex.pop("facade_width") 

    # add modified example to the model, and change zone names to match model 
    model["AirflowNetwork:MultiZone:Zone"] = {}
    for ix, name in enumerate(model["Zone"].keys()):
        model["AirflowNetwork:MultiZone:Zone"][f"AirflowNetwork:MultiZone:Zone {ix+1}"] = create_AFN_zone(name)
        # add a schedule to all zones 
        model["AirflowNetwork:MultiZone:Zone"][f"AirflowNetwork:MultiZone:Zone {ix+1}"]["venting_availability_schedule_name"] = closed_sched
    

    # ~ define opening details and opening surfaces 
    # add slider window definition to model without modification 
    model["AirflowNetwork:MultiZone:Component:DetailedOpening"] = afn_model["AirflowNetwork:MultiZone:Component:DetailedOpening"]

    # make AFN surfaces for the windows in the buildings 
    model["AirflowNetwork:MultiZone:Surface"] = {}
    fen_names = model["FenestrationSurface:Detailed"].keys()
    for ix, name in enumerate(fen_names):
        model["AirflowNetwork:MultiZone:Surface"][f"AirflowNetwork:MultiZone:Surface {ix+1}"] = create_AFN_surface(name)

    # for surface in model["AirflowNetwork:MultiZone:Surface"].values():
    #     if "WestZone_Window" in surface["surface_name"]:
    #         surface["venting_availability_schedule_name"] = "Window Operation"


 

    
    # TODO -> way to print summary of changes, and add to IDF?

    return model 


def adjust_run_control(model):
    model["RunPeriod"]["RunPeriod1"] = make_run_period(0)

    model["RunPeriod"]["RunPeriod2"]  = {}
    model["RunPeriod"]["RunPeriod2"] = make_run_period(1)

    model["RunPeriod"]["RunPeriod3"] = {}
    model["RunPeriod"]["RunPeriod3"] = make_run_period(2)

    model["SimulationControl"]["SimulationControl 1"]["run_simulation_for_weather_file_run_periods"] = "Yes"

    model["SimulationControl"]["SimulationControl 1"]["run_simulation_for_sizing_periods"] = "Yes"

    return model



# ============================================================================ #
# ! AFN to Rosse 

def afn_run_control_on_rosse(model):
    model["RunPeriod"]["RunPeriod1"]["begin_day_of_month"] = ""
    model["RunPeriod"]["RunPeriod1"]["begin_month"] = ""
    model["RunPeriod"]["RunPeriod1"]["end_day_of_month"] = ""
    model["RunPeriod"]["RunPeriod1"]["end_month"] = ""


    model["RunPeriod"]["RunPeriod2"] = {}

    # rosse_model["SimulationControl"] = afn_model["SimulationControl"]
    # rosse_model["SizingPeriod:DesignDay"] = afn_model["SizingPeriod:DesignDay"]

    # # in afn_model model, the simulation control turns the run period off 
    # rosse_model["RunPeriod"] = afn_model["RunPeriod"]


    return model