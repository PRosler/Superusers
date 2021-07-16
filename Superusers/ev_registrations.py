# -*- coding: utf-8 -*-
"""
Created on Wed Jun 16 09:59:48 2021

@author: HP Envy
"""

import pandas as pd
import numpy as np

'''
EV registration data per state and year
'''
#scraping atlasevhub website for data
states = ['ca', 'co', 'ct', 'fl', 'mt', 'mi', 'mn', 'nj', 'ny', 'or', 'tn', 'tx', 'vt', 'va', 'wa', 'wi']
state_names = ['California', 'Colorado', 'Connecticut', 'Florida' ,'Montana', 'Michigan', 'Minnesota', 'New Jersey', 'New York', \
               'Oregon', 'Tennessee', 'Texas', 'Vermont', 'Virginia', 'Washington', 'Wisconsin']

df_groups = []
data = []
for i in states:
    df = pd.read_csv(r'https://www.atlasevhub.com/public/dmv/{}_ev_registrations_public.csv'.format(i))
    data.append(df)
    group = df.groupby(by ='Registration Valid Date').sum()
    df_groups.append(group)


def cleaner(group_list, name_list):
    outlist = []
    data_list = []
    for df, name in zip(group_list, name_list):
        df['LastDigit'] = df.index.str.strip().str[-4:]
        df['LastDigit'] = np.where((df['LastDigit'].str.contains('-')) | (df['LastDigit'].str.contains('/')), np.nan, df['LastDigit'])
        df = df.rename(columns = {'LastDigit': 'year', 'DMV ID': 'number_ev'})
        df['FirstDigit'] = df.index.str.strip().str[0:4]
        df['FirstDigit'] = np.where((df['FirstDigit'].str.contains('-')) | (df['FirstDigit'].str.contains('/')), np.nan, df['FirstDigit'])
        df = df.rename(columns = {'FirstDigit': 'year'})
        df = df.dropna(axis=1, how='all')
        df['state'] = name
        df['year'] = df['year'].astype(float)
        df = df[['number_ev', 'year', 'state']]
        data_list.append(df)
        group = df.groupby(by = 'year').sum()
        group['state'] = name
        outlist.append(group)
    return data_list, outlist

data_clean, df_groups_clean = cleaner(df_groups, state_names)
    
ev_per_year_state = pd.concat(df_groups_clean).reset_index()

