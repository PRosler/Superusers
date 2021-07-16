# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 14:43:42 2021

@author: HP Envy
"""

import pandas as pd
import numpy as np


#'https://www.fhwa.dot.gov/ohim/1996/mv1.xlw', 
fhwa_links = ['https://www.fhwa.dot.gov/ohim/hs97/xls/mv1_1997.xls','https://www.fhwa.dot.gov/policyinformation/statistics/1998/xls/mv1.xls','https://www.fhwa.dot.gov/ohim/hs99/excel/mv1.xls','https://www.fhwa.dot.gov/ohim/hs00/xls/mv1.xls','https://www.fhwa.dot.gov/ohim/hs01/xls/mv1.xls','https://www.fhwa.dot.gov/policy/ohim/hs02/xls/mv1.xls','https://www.fhwa.dot.gov/policy/ohim/hs03/xls/mv1.xls','https://www.fhwa.dot.gov/policy/ohim/hs04/xls/mv1.xls','https://www.fhwa.dot.gov/policy/ohim/hs05/xls/mv1.xls','https://www.fhwa.dot.gov/policy/ohim/hs06/xls/mv1.xls'] 

def data_extractor_1(inlist):
    histo_stat = []
    for i in inlist:
        data = pd.read_excel(i)
        histo_stat.append(data) 
    return histo_stat

highway_statistics_1 = data_extractor_1(fhwa_links)

years = list(range(2007,2020,1))

def data_extractor_2(inlist, url1, url2): 
    histo_stat = []
    for i in inlist:
        try:
            data = pd.read_excel(url1.format(i))
            histo_stat.append(data)
        except:
            data = pd.read_excel(url2.format(i))
            histo_stat.append(data)
    return histo_stat


highway_statistics_2 = data_extractor_2(years,r'https://www.fhwa.dot.gov/policyinformation/statistics/{}/xls/mv1.xls', r'https://www.fhwa.dot.gov/policyinformation/statistics/{}/xls/mv1.xlsx')


highway_statistics = highway_statistics_1 + highway_statistics_2


states_total = highway_statistics[0].iloc[13:66,0].dropna()


#states = ['Washington', 'California', 'Total']
def cleaner(inlist, region):
    clean_list = []
    for df in inlist:
        df = df.astype(str)
        df = df.replace('nan', np.nan, regex = True)
        df = df.dropna(how = 'all').fillna(method = 'bfill')
        new_header = df.iloc[0]
        df = df[1:] 
        df.columns = new_header 
        df = df.filter(regex = 'TOTAL|STATE')
        df = df.iloc[:,[0,1,3]]
        df.columns= ['state','automobile_total', 'truck_total']
        df = df.drop_duplicates(subset = 'state', keep ='last')
        df = df[df['state'].str.contains('|'.join(states_total), case=False, na=False)]
        #df = df.iloc[0:3,:]
        df['state'] =  df['state'].str.lstrip()
        df['state'] = df['state'].map(lambda x: x.rstrip('4/')).map(lambda x: x.rstrip('(2)')).str.rstrip()
        df['year'] = ''
        #df['state'] = df['state'].apply(lambda x: x.split(' ')[0])
        clean_list.append(df)
    return clean_list

highway_statistics_clean = cleaner(highway_statistics, states_total)

years_total = list(range(1997,2020,1))
def year_adder(inlist, time):
    with_year = []
    for i,j in zip(inlist, time):
        i['year'] = j
        with_year.append(i)
    return with_year

highway_statistics_year = year_adder(highway_statistics_clean, years_total)
            
            



column_names = ['year', 'state', 'automobile_total', 'truck_total']

def combine_dfs(inlist, columns):
    df_total = pd.DataFrame(columns = columns)
    for df in inlist:
        df_total = df_total.append(df)
    return df_total

total_dfs = combine_dfs(highway_statistics_year, column_names)


def create_panel(df, region, columns):
    df_total = pd.DataFrame(columns = columns)
    for state in region:
        df_filter = df[df['state'] == state]
        df_total = df_total.append(df_filter)
    df_total = df_total.reset_index(drop = True)
    return df_total
    
panel = create_panel(total_dfs, states_total, column_names)





num_list = ['automobile_total', 'truck_total']
panel[num_list] = panel[num_list].apply(lambda col: pd.to_numeric(col))
panel[['automobile_total', 'truck_total']] = panel[['automobile_total', 'truck_total']].round(0)
panel['Total'] = panel['automobile_total'] + panel['truck_total']
panel['state'] = np.where(panel['state'] == 'Total', 'USA', panel['state'])
panel = panel[['year', 'state', 'automobile_total', 'truck_total', 'Total']]

washington = panel[panel['state'] == 'Washington'].to_excel(r'C:\Users\HP Envy\Dropbox\EV_Model\1_Input\Data\2_WA\fhwa_wa_registration.xlsx', index = False)
california = panel[panel['state'] == 'California'].to_excel(r'C:\Users\HP Envy\Dropbox\EV_Model\1_Input\Data\3_CA\fhwa_ca_registration.xlsx', index = False)
usa = panel[panel['state'] == 'USA'].to_excel(r'C:\Users\HP Envy\Dropbox\EV_Model\1_Input\Data\1_USA\fhwa_usa_registration.xlsx', index = False)
       
panel.to_excel(r'C:\Users\HP Envy\Dropbox\EV_Model\1_Input\fhwa_registration_panel.xlsx', index = False)          
            






