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
from dash.dependencies import Input, Output, State

external_stylesheets = [dbc.themes.BOOTSTRAP,'assets/style.css']
 
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

collapse = dbc.Button(
            "About",
            id="collapse-button",
            className="ml-2",
            color="primary",
        ),
        

search_bar = dbc.Row(
    [
        dbc.Col(dbc.Input(type="search", placeholder="Search")),
        dbc.Col(
            # dbc.Button("Search", color="primary", className="ml-2"),
            collapse,
            width="auto",
        ),
    ],
    no_gutters=True,
    className="ml-auto flex-nowrap mt-3 mt-md-0",
    align="center",
)

navbar = dbc.Navbar(
    [
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    # dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
                    dbc.Col(dbc.NavbarBrand("The Financial Analyst Concept Dashboard", className="ml-2")),
                ],
                align="center",
                no_gutters=True,
            ),
            # href="https://plot.ly",
        ),
        # dbc.NavbarToggler(id="navbar-toggler",children = collapse),
        dbc.Collapse(search_bar, id="navbar-collapse", navbar=True),
    ],
    color="rgba(0,0,0,0)",
    dark=True,
)




@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open




app.layout = html.Div(id = 'master-div',
# style = {'width' : '100%'},
children = [
    html.Div(className = 'navbar',children = [navbar]),
    html.Div(className = 'row',children = [dbc.Collapse(
            dbc.Card(dbc.CardBody(([
                "The Financial Analyst Concept Dashboard was created to showcase and document the " +   
                "interesting concepts I learned while taking 'The Complete Financial Analyst Training & Investing Course' on Udemy. ",html.Br(), 
                "\nPlease note: This is still a work in progress, and loading times may vary as the site is using free hosting from Heroku.",html.Br(),
                "\nProject Start Date: 2020-11-01 ",html.Br(),
                "\nMost Recent Update: 2020-11-02 " ]
                )
            )),
            id="collapse",
        ),]),
    html.Div(className = 'row',children = [


        html.Div(className = 'col-lg-6 plot-box',children = [
            dcc.Graph(
        id='chloro-map',config={
        'displayModeBar': False
    },
        figure = FL.generate_FX_chloropleth()
    )



        ]),

        html.Div(className = 'col-lg-6 plot-box',children = [
            dcc.Graph(id = 'dual-fx-plot',config={
        'displayModeBar': False
    },
            figure = FL.generate_dual_FX_plot()



            )



        ])

    

    ]),

    html.Div(className = 'row',children = [
        html.Div(className = 'col-lg-12',
        children  =[

            # Some DCC GRAPH 
        ]),
        html.Div(className = 'col-lg-')







    ])

])

if __name__ == '__main__':
    app.run_server(
        debug = True

    )