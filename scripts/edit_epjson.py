import os, json
from model_edits import * 
from icecream import ic 
ic.configureOutput(includeContext=True)

ROOT= "/Users/julietnwagwuume-ezeoke/_UILCode/buildingEnergyModel/"
MODELS_DIR = "rosseRoomModel/230301_rr/"
OUTPUT_DIR = "rosseRoomModel/230303_rr/"

# ! import data 
filename = "AFN_SS2.epJSON"
with open(os.path.join(ROOT, MODELS_DIR, filename)) as f:
    base_afn_model = json.load(f)


filename = "os.epJSON" # os  => open studio model 
with open(os.path.join(ROOT, MODELS_DIR, filename)) as f:
    rosse_model = json.load(f)


# ! edits to rosse model 
# want to compare original model to what we get when put the geom into afn model 
# rosse02 = afn_run_control_on_rosse(afn_model, rosse_model)


# ! edits to afn-rosse model 
model01 =  rosse_on_afn(base_afn_model, rosse_model)
model = add_zone_vent(model01)

# model = add_afn_to_model(base_afn_model, model01)




# # ! output data 
# write 
model_name = "test04_schedZoneVent"

output_filename = f'{model_name}.epJSON'
# dont need to make dir, it should go in general models dir, e+ makes the dir for the output os.mkdir(os.path.join(ROOT, MODELS_DIR, f"{model_name}" ))
with open(os.path.join(ROOT, OUTPUT_DIR, output_filename),'w') as f:
    json.dump(model, f)

print(f"created epjson for {model_name}")