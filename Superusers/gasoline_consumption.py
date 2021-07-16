# -*- coding: utf-8 -*-
"""
Created on Fri Jul  2 16:13:14 2021

@author: HP Envy
"""

import pandas as pd

df = pd.read_csv(r'C:\Users\HP Envy\Dropbox\Gas_Subsidy_Model\1_Input\gasoline_consumption.csv')
df['YYYYMM'] = df['YYYYMM'].astype(str)
df['year']=df['YYYYMM'].str.slice(stop=4)
df['month']=df['YYYYMM'].str.slice(start=4)

df_group = pd.DataFrame(df.groupby('year')['Value'].mean())
df_group['an_gal'] = df_group['Value'] * 42 * 365

df_group.to_excel(r'C:\Users\HP Envy\Dropbox\Gas_Subsidy_Model\1_Input\gasoline_consumption_gallons_per_year.xlsx')