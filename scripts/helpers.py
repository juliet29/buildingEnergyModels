from ladybug.sql import SQLiteResult
from ladybug.analysisperiod import AnalysisPeriod as ap
import numpy as np
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots




def diff(list1, list2):
    # TODO would be good to know which model the dif originates from 
    c = set(list1).union(set(list2))  # or c = set(list1) | set(list2)
    d = set(list1).intersection(set(list2))  # or d = set(list1) & set(list2)
    return list(c - d), c, d

def flatten(l):
    return [item for sublist in l for item in sublist]


class LoadSQL():
    """
    Class for quickly analyzing outputs of SQL files 

    Example usage:

    # load sql 
    dir0 = "../examples/AFN_SS/eplusout.sql"
    a = LoadSQL(dir0)

    # check available outputs
    a.ao

    # check headers for interesting outputs 
    a.enumerate_data_headers("Site Outdoor Air Drybulb Temperature")

    # make a list of tuples with desired data 
    desired_data = [(i, j, k) for i, j, k in zip(["Zone Mean Air Temperature"]*4 + ["Site Outdoor Air Drybulb Temperature"], [4,5,6,7,1], ["West", "South", "North", "East", "Sep Out"] )]

    ad = a.get_valid_data(desired_data)

    
    """


    def __init__(self, relative_sql_path, exp_name="Run A"):
        SQL_PATH = relative_sql_path
        self.sqld = SQLiteResult(SQL_PATH)
        self.ao = self.sqld.available_outputs # some how make these ENUMS??
        self.exp_name = exp_name
        self.data = {}
        

    # def available_outputs(self):
    #     return self.sqld.available_outputs
    
    def enumerate_data_headers(self, output_name):
        output = self.sqld.data_collections_by_output_name(output_name)
        for ix, o in enumerate(output):
            print(ix, "\n", o.header, "\n")
    
    def get_valid_data(self, arr_output_name_and_ix):
        """
        arr_output_name_and_ix: [(output_name, ix, abbr), (output_name, ix, abbr)]
        # TODO maybe make this a class of its own so can add and remove as needed... 
        """

        for ix, item in enumerate(arr_output_name_and_ix):
            # check if output_name in available outputs 
            if item[0] in self.ao:
                try:
                    data_group = self.sqld.data_collections_by_output_name(item[0])
                    self.data[item[2]] = data_group[item[1]]
                except Exception as err:
                    print(f"Error in item {ix}")
                    print(f"Unexpected {err=}, {type(err)=}")

        return self.data
    
    def plot_temps(self):
        if not self.data:
            return "No data yet!"
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # first check all are temps...
        for k, v in self.data.items():
            try:
                assert v.header.to_dict()["data_type"]["name"] == "Temperature"
            except AssertionError:
                print("This doesn't have temperature units")
                continue
                
            fig.add_trace(go.Scatter(
                    x=v.datetimes,
                    y=v.values, 
                    mode='lines',
                    name=k
                )),

            print(f"i continued, {k}")

        fig.update_layout(title=f"{self.exp_name}",
                   xaxis_title='Dates',
                   yaxis_title='Temperature (ºC)')

        self.temp_fig = fig

        return self.temp_fig
        

        






