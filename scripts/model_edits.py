"""Edits to bring original rosse geometry into AFN Single Sided Ventilation Example """

from helpers import diff
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

def create_AFN_zone(name="Default"):
    return {
            "single_sided_wind_pressure_coefficient_algorithm": "Standard",
            "ventilation_control_mode": "Constant",
            "zone_name": name
            }

def create_zoneventilation_object(name="Default"):
        return {
            "zone_or_space_name": name,
            "opening_area": 0.5, #m2
            # "opening_area_fraction_schedule_name": "Constant",
            "opening_effectiveness": "Autocalculate",
            "effective_angle": 0,
            # "discharge_coefficient_for_opening": "Autocalculate",

            }


def create_schedule_object():
    return {
        "schedule_type_limits_name": "Fraction",
        "Through": "12/31",
        "For": "AllDays",
        "Until": "12:00, 1.0",
        "Until": "24:00, 0.0",   
    }

# ============================================================================ # ! General 

def add_object(obj, model, fx, multiple=False):
    model[obj] = {}
    model[obj] = fx(name)
    if multiple:
        for ix, name in enumerate(model["Zone"].keys()):
            model[obj][f"{obj} {ix+1}"] = fx(name)
    return model 


def add_zone_vent(model):
        model = add_object("ZoneVentilation:WindandStackOpenArea", model, create_zoneventilation_object, multiple=True)

        model = add_object("Schedule:Compact", model, create_schedule_object)



        # obj = "ZoneVentilation:WindandStackOpenArea"
        # model[obj] = {}
        # for ix, name in enumerate(model["Zone"].keys()):
        #     model[obj][f"{obj} {ix+1}"] = create_zoneventilation_object(name)

        return model


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

    # ~ define opening details and opening surfaces 
    # add slider window definition to model without modification 
    model["AirflowNetwork:MultiZone:Component:DetailedOpening"] = afn_model["AirflowNetwork:MultiZone:Component:DetailedOpening"]

    # make AFN surfaces for the windows in the buildings 
    model["AirflowNetwork:MultiZone:Surface"] = {}
    fen_names = model["FenestrationSurface:Detailed"].keys()
    for ix, name in enumerate(fen_names):
        model["AirflowNetwork:MultiZone:Surface"][f"AirflowNetwork:MultiZone:Surface {ix+1}"] = create_AFN_surface(name)


    # ~ define vent schedules

    # TODO -> way to print summary of changes, and add to IDF?

    return model 



# ============================================================================ #
# ! AFN to Rosse 

def afn_run_control_on_rosse(afn_model, rosse_model):
    rosse_model["SimulationControl"] = afn_model["SimulationControl"]
    rosse_model["SizingPeriod:DesignDay"] = afn_model["SizingPeriod:DesignDay"]

    # in afn_model model, the simulation control turns the run period off 
    rosse_model["RunPeriod"] = afn_model["RunPeriod"]


    return rosse_model