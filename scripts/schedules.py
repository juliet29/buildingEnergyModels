import os, json

def create_schedule_object(key):
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
        "exp_A_sched": { # applies to 422b (west zone)
            "data": [
                { "field": "Through: 12/31" },
                { "field": "For: AllDays" },
                { "field": "Until: 24:00" },
                { "field": 0.0 },
            ],
            "schedule_type_limits_name": "Fraction"
        },

    }
    return schedules[key]


# windows/.../htimes.json -> dictionary 
filename = "/Users/julietnwagwuume-ezeoke/_UILCode/windows/analysis/constants/htimes.json" # os  => open studio model 
with open(filename) as f:
    rosse_model = json.load(f)
