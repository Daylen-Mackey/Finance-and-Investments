# FinanceLib.py

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.offline as pyo
import plotly.graph_objs as go
# from exchangeratesapi import Api
import datetime
from plotly.subplots import make_subplots


def get_FX_sheet():
    df = pd.read_csv('FinalFXSheet.csv')
    df['Reference Currency'] = df['Reference Currency'].str.title()
    return df


def get_Thai_sheet():

    return pd.read_excel("assets/Thai-US.xls")

def generate_Thai_USD_plot():
    df = get_Thai_sheet()
    df['Date'] = df['observation_date'].dt.date

    trace = go.Scatter(
        x = df.Date,
        y = df.DEXTHUS,
        mode='lines',
        line_color='#92174a',
        # marker_color='#92174a',
        
        
        )

    layout = dict(
        title='Thai Baht / USD Foreign Exchange Rate',
        title_x = .5,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color = 'white',
        font_size = 12,
        
        xaxis=dict(
            
            rangeslider=dict(
                visible = True
            ),
            type='date'
        )
    )
    fig = go.Figure(data = trace, layout = layout)

    event_date = '1997-07-02'
    fig.add_annotation(x = event_date, y=30.18,
                text="Thai Baht detaches from US Dollar",
            showarrow=True,
            font=dict(
                family="Courier New, monospace",
                size=16,
                color="#ffffff"
                ),
            align="center",
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            clicktoshow = 'onoff',
            arrowcolor="#636363",
            ax=-100,
            ay=-30,
            bordercolor="#c7c7c7",
            borderwidth=2,
            borderpad=4,
            bgcolor="#ff7f0e",
            opacity=0.8
                )
    fig.update_layout()
    initial_range = [
        '1996-01-01', '2001-01-01']

    fig['layout']['xaxis'].update(range=initial_range)

    return fig



def generate_dual_FX_plot():
    df = get_FX_sheet()
    grouped_reference_currency_count = df.groupby('Reference Currency').count()
    grouped_reference_currency_median = df.groupby('Reference Currency').median()

    grouped_reference_currency_count.sort_values(
        'Count', inplace=True, ascending=False)
    grouped_reference_currency_median = grouped_reference_currency_median.reindex_like(
        grouped_reference_currency_count)

    x = grouped_reference_currency_count.index
    y_count = grouped_reference_currency_count.Count
    y_median = grouped_reference_currency_median['Rate (Reference / Fixed)']

    # Creating two subplots
    fig = make_subplots(rows=1, cols=2, specs=[[{}, {}]], shared_xaxes=True,
                        shared_yaxes=False, vertical_spacing=0.001)

    fig.append_trace(go.Bar(
        x=y_count,
        y=x,
        marker=dict(
            color='#92174a',
            opacity = .7,
            line=dict(
                color='rgba(50, 171, 96, 1.0)',
                width=1),
        ),
        text=y_count,
        textposition='outside',
        name='# of<br>Currencies',
        orientation='h',
    ), 1, 1)

    fig.append_trace(go.Scatter(
        x=y_median, y=x,
        mode='lines+markers+text',
        line_color='rgb(128, 0, 128)',
        textposition='middle right',
        text=y_median,
        
        name='Median<br>FX<br>Rate',
    ), 1, 2)

    fig.update_layout(
        title='Reference Currencies used in Fixed Exchange Rates',
        title_x = .5,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color = 'white',
        font_size = 12,
        # hovermode="x unified",
        yaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=True,
            title = "Reference Currencies"
        ),
        yaxis2=dict(
            showgrid=False,
            showline=True,
            showticklabels=False,
            linecolor='rgba(102, 102, 102, 0.8)',
            linewidth=2,
        ),
        xaxis=dict(
            zeroline=False,
            showline=True,
            showticklabels=True,
            showgrid=True,
            title = '# of Countries Fixed to Currency'
        ),
        xaxis2=dict(
            zeroline=False,
            showline=True,
            showticklabels=True,
            showgrid=True,
            title = 'Median Fixed Exchange Rate'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.0,
            xanchor="left",
            x=0
        ),
        showlegend = False,
         
        # margin=dict(l=100, r=20, t=70, b=70),
        hoverlabel=dict(
            bgcolor="white",
            font_size=16,
            font_family="Rockwell"
        )
    )
    fig.update_xaxes(
    range=[0, grouped_reference_currency_count.Count.max()*1.5],
    row = 1, col = 1,
    )  # sets the range of xaxis)
    fig.update_xaxes(
    range=[0, grouped_reference_currency_median['Rate (Reference / Fixed)'].max()*1.5],
    row = 1, col = 2,
    )  # sets the range of xaxis)

    return fig


def generate_FX_chloropleth():
    df = get_FX_sheet()
    df = df[df['Reference Currency'].notna()]

    fig = go.Figure(data=go.Choropleth(
        # fig = go.Figure(data=go.Choroplethmapbox(
        locations=df['Alpha-3 code'],
        
        # z = df['Rate (Reference / Fixed)'],
        z=df.index.values,
        text=df['Country'] + ' is pegged to the ' + df['Reference Currency'] + \
        '<br>with a standard exchange rate of ' + \
        round(df['Rate (Reference / Fixed)'], 2).astype(str),
        # colorscale = 'Blues',
        colorscale=px.colors.sequential.Plasma,
        autocolorscale=False,
        reversescale=True,
        marker_line_color='black',
        marker_line_width=1.5,
        colorbar_tickprefix='',
        colorbar_title='',
        showscale=False,
    ))

    fig.update_layout(
        title_text='Countries with Fixed Exchange Rates (Pegged Currencies)',
        title_x = .5,
        title_y = .9,
        coloraxis_showscale=False,
        autosize=True,
        
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color = 'white',
        # margin=dict(t=25, b=0, l=25, r=25),
        margin=dict(t=5, b=5, l=5, r=5),
        # width = 1500,
        # height = 1000,

        geo=dict(
            showframe=True,
            bgcolor='#15386a',
            showcoastlines=True,
            projection_type='equirectangular'
        ),


    )

    return fig
