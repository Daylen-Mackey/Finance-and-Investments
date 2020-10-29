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

request1 = requests.get(url_1).text
request2 = requests.get(url_2).text

soup_1 = BeautifulSoup(request1,'lxml')
soup_2 = BeautifulSoup(request2,'lxml')


all_currencies_table = soup_1.find('table',{'class' : 'wikitable sortable' })
fx_table = soup_2.find('table',{'class' : 'wikitable sortable' })
#%% We've grabbed our tables, now let's convert them into DataFrames
 
df_all_curr = pd.read_html(str(all_currencies_table))[0]
df_fx = pd.read_html(str(fx_table))[0]


#%% General Cleaning & Merging

df_all_curr.columns = ['Country', 'Currency','Symbol','ISO', 'Unit','Number to Basic']

df_fx.rename({'Fixed Currency': 'Currency'},axis = 1, inplace = True)


df_merged = df_all_curr.merge(df_fx,how = 'left', on = 'Currency')

#%%

fx = df_merged.dropna().
