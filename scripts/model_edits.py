"""Edits to bring original rosse geometry into AFN Single Sided Ventilation Example """

from helpers import diff
from icecream import ic 
ic.configureOutput(includeContext=True)

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
    for z in model["Zone"].keys():
        model["AirflowNetwork:MultiZone:Zone"] = zone_ex
        model["AirflowNetwork:MultiZone:Zone"]["zone_name"] = z

    # ~ define opening surfaces and opening details 
    # add slider window definition to model without modification 
    model["AirflowNetwork:MultiZone:Component:DetailedOpening"] = afn_model["AirflowNetwork:MultiZone:Component:DetailedOpening"]

    # get example of afn surface 
    surface_ex = afn_model["AirflowNetwork:MultiZone:Surface"]["AirflowNetwork:MultiZone:Surface 1"]

    # add afn surface to model 
    for f in model["FenestrationSurface:Detailed"].keys():
        model["AirflowNetwork:MultiZone:Surface"] = surface_ex
        model["AirflowNetwork:MultiZone:Surface"]["surface_name"] = f


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