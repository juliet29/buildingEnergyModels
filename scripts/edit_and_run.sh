#!/bin/bash

model=test01
model_dir=230307

python3 scripts/edit_epjson.py 

echo $model
echo $model_dir

energyplus -w weather/USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw -d rosseRoomModel/$model_dir/$model -c rosseRoomModel/$model_dir/$model.epJSON


# to run: ./scripts/edit_and_run.sh