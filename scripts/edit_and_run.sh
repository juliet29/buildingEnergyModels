#!/bin/bash

model=test04_schedZoneVent
model_dir=230303_rr

python3 scripts/edit_epjson.py 

echo $model
echo $model_dir

energyplus -w weather/USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw -d rosseRoomModel/$model_dir/$model -c rosseRoomModel/$model_dir/$model.epJSON