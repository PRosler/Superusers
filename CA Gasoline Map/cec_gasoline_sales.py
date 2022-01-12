# -*- coding: utf-8 -*-
"""
Created on Mon Jan  3 10:33:04 2022

@author: HP Envy
"""

import pandas as pd

path = r'A:\Upwork\DMV_Data'

'''
County level
'''

#direct access: https://www.energy.ca.gov/sites/default/files/2021-07/CEC-A15%20Gasoline%20Sales%20by%20Cities_ADA.xlsx
df_original = pd.read_excel(path + r'\Data\2010-2020 CEC-A15 Results and Analysis.xlsx', sheet_name= 'Retail Gasoline Sales by County')

# create list with variables to include
col_choice = list([col for col in df_original.columns if 'Estimated Totals' in col])
col_choice.insert(0,'County')

# exlclude variables that are not in list from df and rename columns
df = df_original[col_choice]
df.columns = df.columns.str.replace('[A Estimated Totals (Millions of Gallons)]', '')
df = df.rename(columns = {'Cuy': 'County'})


df['average_gasoline_sales_county'] = round(df.mean(axis=1),1)

df = df[['County', 'average_gasoline_sales_county']]

average_gasoline_sales_county = df.copy()


'''
ZIP level
'''

df_original = pd.read_excel(path + r'\Data\220103 CA gas sales by zip code to 2019.xlsx', sheet_name= 'Gasoilne Sales by Zip Code')

df_original = df_original.rename(columns = {'Unnamed: 0': 'Zip_Code'})
df = df_original[df_original.columns.drop(list(df_original.filter(regex='Unnamed')))]
df = df.reset_index(drop = True)
df.columns.str.replace(' ','')

# exclude column header and last rows including totals
df = df.iloc[1:904,:]

df['Zip_Code_num'] = df['Zip_Code'].astype(float)
df[2019] = df[2019].astype(float)

df_19 = df[['Zip_Code_num', 2019]]
df_19 = df_19.rename(columns = {2019: 'gasoline_sales_2019'})
gasoline_sales_2019 = df_19.copy()
