# ConceptDashboard.py

import pandas as pd
import numpy as np
import FinanceLib as FL
 

import plotly.express as px
import plotly.offline as pyo
import plotly.graph_objs as go

from plotly import tools


import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    'assets/style.css'
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server


app.layout = html.Div(style = {'width' : '100%'},children = [
    html.Div(className = 'row',children = [


        html.Div(className = 'col-lg-6',children = [
            dcc.Graph(
        id='chloro-map',
        figure = FL.generate_FX_chloropleth()
    )



        ]),

        html.Div(className = 'col-lg-6',children = [
            dcc.Graph(id = 'dual-fx-plot',
            figure = FL.generate_dual_FX_plot()



            )



        ])

    

    ]),

    html.Div(className = 'row',children = [
        html.Div(className = 'col-lg-12',
        children  =[

            # Some DCC GRAPH 
        ])







    ])

])

if __name__ == '__main__':
    app.run_server()