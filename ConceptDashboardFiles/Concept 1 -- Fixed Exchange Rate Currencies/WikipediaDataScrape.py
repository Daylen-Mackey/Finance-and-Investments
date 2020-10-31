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


#%% Horizontal Bar Plot

df = pd.read_csv('FinalFXSheet.csv')
# First get counts for each reference currency

grouped_reference_currency_count = df.groupby('Reference Currency').count()
grouped_reference_currency_median = df.groupby('Reference Currency').median()


#%%
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import numpy as np
grouped_reference_currency_count.sort_values('Count',inplace = True,ascending = False)
grouped_reference_currency_median = grouped_reference_currency_median.reindex_like(grouped_reference_currency_count)

#%%
y_saving = grouped_reference_currency_count.Count
y_net_worth = grouped_reference_currency_median['Rate (Reference / Fixed)']
