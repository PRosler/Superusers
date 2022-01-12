# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 11:03:25 2021

@author: HP Envy
"""

import pandas as pd
import numpy as np

path = r'A:\Upwork\DMV_Data'

df_in = pd.read_excel(path +r'\Data\afcd_10567_pev_sales_2-28-20.xlsx')

df = df_in.copy()
df.columns = df.iloc[1]
df = df.iloc[3:58]

df['Vehicle'] = df['Vehicle'].str.upper()
df[['Make', 'Model']] = df['Vehicle'].str.split(' ', 1, expand=True)

df['Make'] = np.where(df['Make'] == 'CHEVY', 'CHEVROLET', df['Make'])
df['Make'] = np.where(df['Make'] == 'VW', 'VOLKSWAGEN', df['Make'])
df['Model'] = np.where(df['Model'] == 'BOLT', 'BOLT EV', df['Model'])

df.sort_values(by=['Total'])

df_filter_ev = df[df['Type'] == 'EV']

ev_models = df[['Type', 'Model', 'Make']]
