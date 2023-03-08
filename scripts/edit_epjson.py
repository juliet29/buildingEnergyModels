import os, json
from model_edits import * 
from icecream import ic 
ic.configureOutput(includeContext=True)

ROOT= "/Users/julietnwagwuume-ezeoke/_UILCode/buildingEnergyModel/"
AFN_DIR = "rosseRoomModel/230301/"
BASE_DIR = "rosseRoomModel/230306/"


# ! import data 
filename = "AFN_SS2.epJSON"
with open(os.path.join(ROOT, AFN_DIR, filename)) as f:
    base_afn_model = json.load(f)


filename = "rosse02.epJSON" # os  => open studio model 
with open(os.path.join(ROOT, BASE_DIR, filename)) as f:
    rosse_model = json.load(f)


# ! edits to rosse model 
# want to compare original model to what we get when put the geom into afn model 
# rosse02 = afn_run_control_on_rosse(afn_model, rosse_model)


# ! edits to afn-rosse model 
# no afn 
# model =  rosse_on_afn(base_afn_model, rosse_model)

# add afn 
model01 =  rosse_on_afn(base_afn_model, rosse_model)
model = add_afn_to_model(base_afn_model, model01)




# # ! output data 
# write 
OUTPUT_DIR = "rosseRoomModel/230307/"
model_name = "test00"

output_filename = f'{model_name}.epJSON'
# dont need to make dir, it should go in general models dir, e+ makes the dir for the output os.mkdir(os.path.join(ROOT, MODELS_DIR, f"{model_name}" ))
with open(os.path.join(ROOT, OUTPUT_DIR, output_filename),'w') as f:
    json.dump(model, f)

print(f"created epjson for {model_name}")