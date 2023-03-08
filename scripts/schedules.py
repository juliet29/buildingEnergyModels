import os, json
from helpers import flatten
import pandas as pd



filename = "/Users/julietnwagwuume-ezeoke/_UILCode/windows/analysis/constants/htimes.json" # os  => open studio model 
with open(filename) as f:
    htimes = json.load(f)

for v in htimes.values():
    for group in v:
        group["open"] = pd.to_datetime(group["open"], format= '%Y, %m, %d, %H, %M' )
        group["close"] = pd.to_datetime(group["close"], format= '%Y, %m, %d, %H, %M' )

t = [[i["open"]] + [i["close"]] for i in htimes['072522']]
ts = flatten(t)



def check_last_time(time, ts):
    times_on_day = []
    for t in ts:
        # check that we are on the same day 
        if t.date() == time.date():
            # check if this time is later than the others
            if time.time() >= t.time():
                times_on_day.append(True)
            else:
                times_on_day.append(False)
    
    # check the last item of the dictionary 
    if times_on_day[-1] == False:
        return False
    else:
        return True
    
def add_times(t, window_status):
    """t:time stamp
    window_status: 0 if closed, 1 if open. if dictionary says 'open', then until this point it has been closed, so input 0, and vice versa"""
    data = []
    data.append({"field": f"Through: {t.strftime(format='%m/%d')}"})
    data.append({"field": f"For: AllDays"})
    data.append({"field": f"Until: {t.strftime(format='%H:%M')}"})
    data.append({"field": window_status})
    if check_last_time(t, ts): 
        data.append({"field": f"Through: {t.strftime(format='%m/%d')}"})
        data.append({"field": f"For: AllDays"})
        data.append({"field": f"Until: 24:00"})
        data.append({"field": window_status})
    return data

def create_variable_schedule(key):
    print(key)
    if key==None:
        return
    
    exp_date = {letter:key for letter, key in zip(["A", "B", "C"], htimes.keys())}
    item = exp_date[key]
    data = []
    for i, time in enumerate(htimes[item]):
        d = add_times(time["open"], 0)
        data.extend(d)
        d = add_times(time["close"], 1)
        data.extend(d)

    return data

def create_schedule_object(key, dynamic_key=None): 
    schedules = {
        "always_closed_sched": {
            "data": [
                { "field": "Through: 12/31" },
                { "field": "For: AllDays" },
                { "field": "Until: 24:00" },
                { "field": 0.0 },
            ],
            "schedule_type_limits_name": "Fraction"
        },
        "always_open_sched": {
            "data": [
                { "field": "Through: 12/31" },
                { "field": "For: AllDays" },
                { "field": "Until: 24:00" },
                { "field": 1.0 },
            ],
            "schedule_type_limits_name": "Fraction"
        },
        "dynamic_sched" :{ 
            "data": create_variable_schedule(dynamic_key),
            "schedule_type_limits_name": "Fraction"
        }
    }
    if dynamic_key:  
        return schedules["dynamic_sched"]
    else:
        return schedules[key]





