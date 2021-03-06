# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 20:41:14 2020

Wikipedia Data Scraping

1) https://en.wikipedia.org/wiki/List_of_circulating_currencies

2) https://en.wikipedia.org/wiki/List_of_circulating_fixed_exchange_rate_currencies


@author: Daylen Mackey
"""

import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup


#%% Setting the URLS

url_1 = 'https://en.wikipedia.org/wiki/List_of_circulating_currencies' # All currencies
url_2 = 'https://en.wikipedia.org/wiki/List_of_circulating_fixed_exchange_rate_currencies' #Fixed  currencies
url_3 = 'https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes'
url_4 = 'https://www.xe.com/symbols.php' # List of all currency symbols --> Not used 

request1 = requests.get(url_1).text
request2 = requests.get(url_2).text
request3 = requests.get(url_3).text


soup_1 = BeautifulSoup(request1,'lxml')
soup_2 = BeautifulSoup(request2,'lxml')
soup_3 = BeautifulSoup(request3,'lxml')


all_currencies_table = soup_1.find('table',{'class' : 'wikitable sortable' })
fx_table = soup_2.find('table',{'class' : 'wikitable sortable' })
country_iso_codes_table = soup_3.find('table',{'class' : 'wikitable sortable' })


#%% We've grabbed our tables, now let's convert them into DataFrames
 
df_all_curr = pd.read_html(str(all_currencies_table))[0]
df_fx = pd.read_html(str(fx_table))[0]
df_country_codes = pd.read_html(str(country_iso_codes_table))[0]


#%% General Cleaning & Merging

df_all_curr.columns = ['Country', 'Currency','Symbol','ISO', 'Unit','Number to Basic']

df_fx.rename({'Fixed Currency': 'Currency'},axis = 1, inplace = True)

df_merged = df_all_curr.merge(df_fx,how = 'left', on = 'Currency')

#Mapping all the symbols 

#making a mask of all the pegged_currencies

pegged_mask = df_merged['Reference Currency'].notna()

reference_currency_isos = df_merged['Reference Currency'].to_frame().merge(df_all_curr.drop_duplicates(subset = ['Currency']), how = 'left', left_on = 'Reference Currency', right_on = 'Currency').ISO
# Pound Sterling not Recognized in our previously scraped dataframe

df_merged.insert(0,'Ref_ISO',reference_currency_isos)


GBP_mask = (df_merged['Reference Currency'] == 'Pound sterling')
df_merged.loc[GBP_mask,'Ref_ISO'] = "GBP"


#%% Now that we have everything we need, we can start looking at APIs

from exchangeratesapi import Api
import datetime
api = Api()

supported = df_merged['ISO'].apply(api.is_currency_supported)

df_merged.insert(0,'Supported?',supported.values)

# Now we can do some additional filtering so we don't have to waste API calls 


#%% To use plotly maps, we need the country's ISO code (ISO 3166-1 alpha-3) --> Column 4 in our DataFrame

df_country_codes.columns = ['Country name','Official state name'	,'Sovereignty'	,'Alpha-2 code'	,'Alpha-3 code'	,'Numeric code', 'Subdivision code links','Internet ccTLD']

#%%


country_iso = df_merged.merge(df_country_codes[['Country name','Alpha-3 code']],how = 'left', left_on = 'Country',right_on = 'Country name')


#%% Let's look at how effective that merge was:


print(country_iso[country_iso['Reference Currency'].notna()])


# Not the most effective, but we can come back and make updates as we go along





#%%
country_iso_mask = (country_iso['Alpha-3 code'].notna() & 
                    country_iso['Reference Currency'].notna()
                    )


country_iso.loc[country_iso_mask,'Count'] = 1


# country_iso.to_csv('FinalFXSheet.csv',index = False)

#%% Chloropleth map
import plotly.express as px
import plotly.offline as pyo
import plotly.graph_objs as go
#%%
df = pd.read_csv('FinalFXSheet.csv')

df = df[df['Reference Currency'].notna()]
df.reset_index(inplace = True)

fig = go.Figure(data=go.Choropleth(
        # fig = go.Figure(data=go.Choroplethmapbox(
        locations=df['Alpha-3 code'],
        # z = df['Rate (Reference / Fixed)'],
        z=df.index.values,
        text=df['Country'] + ' is pegged to the ' + df['Reference Currency'] + \
        '<br> with a standard exchange rate of ' + \
        round(df['Rate (Reference / Fixed)'], 2).astype(str),
        # colorscale = 'Blues',
        colorscale = px.colors.sequential.Plasma,
        autocolorscale=False,
        reversescale=True,
        marker_line_color='black',
        marker_line_width=1.5,
        colorbar_tickprefix='',
        colorbar_title='',
        showscale = False,
    ))

fig.update_layout(
    title_text='Countries with Fixed Exchange Rates (Pegged Currencies)',
    coloraxis_showscale=False,
    # width = 1500,
    # height = 1000,
    
    geo=dict(
        showframe=True,
        # showcoastlines=True,
        # projection_type='equirectangular'
    ),


)
  
pyo.plot(fig)

#%% Capitalize every word
df = pd.read_csv('FinalFXSheet.csv')
df['Reference Currency'] = df['Reference Currency'].str.title()




#%% API experimentation

df = pd.read_csv('FinalFXSheet.csv')

from exchangeratesapi import Api
from datetime import date,timedelta
import requests
import json
api = Api()


#%%
today_obj = date.today()
today_str = today_obj.strftime("%Y-%m-%d")
year_ago = (today_obj - timedelta(days = 365)).strftime("%Y-%m-%d")
API_url = f"https://api.exchangeratesapi.io/history?start_at={year_ago}&end_at={today_str}"

response = requests.get(API_url)

hist_rates = json.loads(response.text)['rates']
#%% All historical rates received in json format 


df_rates = pd.DataFrame(hist_rates).transpose() # All these rates are grabbed with respect to the Euro 

parent_currencies = df[df['Reference Currency'].notna()].Ref_ISO.unique()

supported_children_currencies = df[df['Reference Currency'].notna() & df['Supported?']].ISO


#%% Rather than taking this approach, talk about the IMPACT floating a currency has 

"""
1) 1967 British pound? --> Too old 
2) Thai Baht 1997
3) Bank of England 1992

"""
# 2) Thai Baht 1997 -- July 2nd

df = pd.read_excel("Thai-US.xls")
df['Date'] = df['observation_date'].dt.date

trace = go.Scatter(
    x = df.Date,
    y = df.DEXTHUS,
    
    
    )

layout = dict(
    title='Thai Baht / USD Foreign Exchange Rate',
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
        ax=-50,
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

pyo.plot(fig)



#%%
#1) 1) 1967 British pound? 
API_url = f"https://api.exchangeratesapi.io/history?start_at=1997-01-01&end_at=1998-01-01"

response = requests.get(API_url)

hist_rates = json.loads(response.text)['rates']



#%%%
# Converting the EXCEl GDP data into something cleaner and easier to process
df = pd.read_excel("assets/US_GDP_QUARTLERY.xls")
df = df.iloc[10:]
df.columns = ['Date',"GDP (Millions)"]

df['Date'] = pd.to_datetime(df['Date']).dt.date

#%% Code to determine if in recession
# Recession means two consecutive down quarters, break recession with two periods of growth

difference = df['GDP (Millions)'].diff() 



















