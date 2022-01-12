'''
Author: Paul Roesler
'''

import pandas as pd
import numpy as np

path = r'PUT_YOUR_DATAPATH_HERE'

'''
import census data: ACS DEMOGRAPHIC AND HOUSING ESTIMATES
https://data.census.gov/cedsci/table?g=0400000US06%248600000&tid=ACSDP5Y2019.DP05

'''
#import as csv
census = pd.read_csv(path + r'\Data\census\DP05\ACSDP5Y2019.DP05_data_with_overlays_2021-11-04T152824.csv')

df = census.copy()
# rename poulation and race variables to extract (nl = not latino)
df = df.rename(columns = {'DP05_0001E': 'total_population','DP05_0037PE':'white_perc' , 'DP05_0038PE': 'black_perc',\
                          'DP05_0044PE': 'asian_perc', 'DP05_0035PE': 'two_more_races_perc', 'DP05_0036PE': 'one_race_perc',\
                              'DP05_0071PE': 'nl_latino_perc', 'DP05_0077PE': 'nl_white_perc', 'DP05_0078PE': 'nl_black_perc',\
                                  'DP05_0079PE': 'nl_indian_alaska_native', 'DP05_0080PE': 'nl_asian_perc',
                                  'DP05_0083PE':'nl_2+_races_perc'})

# filter df for vars of interest
df = df[['NAME', 'total_population', 'nl_white_perc', 'nl_black_perc', 'nl_asian_perc',\
          'nl_latino_perc', 'nl_2+_races_perc']]

# set new column header
df = df[1:] #take the data less the header row

# create two new columns containing name and zip code
df[['name', 'Zip_Code']] = df['NAME'].str.split(' ', 1, expand=True)
del df['NAME']

# filter out zip codes with population >= 0
df = df[df['total_population'] != '0']

to_num = ['total_population', 'nl_white_perc', 'nl_black_perc', 'nl_asian_perc',\
          'nl_latino_perc', 'nl_2+_races_perc']

for i in to_num:
    df[i] = pd.to_numeric(df[i])
    # print(i, ' average:', df[i].mean())

df['population_tsd_inhabitants']  = df['total_population'] /1000



zip_population = df.copy()


'''
income data
'''


census_income = pd.read_csv(r'A:\Upwork\DMV_Data\Data\census\ST05\ACSST5Y2019.S0501_data_with_overlays_2021-11-25T095626.csv')

df1 =census_income.copy()
df1 = df1.rename(columns = {'S0501_C01_089E': 'total_income','S0501_C01_001E': 'total_population_1', 'S0501_C01_101E': 'median_household_income',\
                            'S0501_C01_015E': 'white', 'S0501_C01_016E': 'black',\
                              'S0501_C01_018E': 'asian', 'S0501_C01_022E':'latino'})


check_nan = ['total_income', 'median_household_income']
for i in check_nan:
    num_obs = df1[df1[i].notna()]
    # print(len(df1[i]))

df1 = df1[['NAME', 'total_population_1', 'total_income', 'median_household_income', 'white', 'black', 'asian', 'latino']]

df1 = df1[1:] #take the data less the header row

df1['median_household_income'] = np.where(df1['median_household_income'] == '250,000+', '250000', df1['median_household_income'])

to_num = ['total_population_1', 'median_household_income', 'white', 'black', 'asian', 'latino']

for i in to_num:
    df1[i] = pd.to_numeric(df1[i])

races = ['white', 'black', 'asian', 'latino']
for i in races:
    df1[i] = df1[i] / df1['total_population_1']
    # print(i, df1[i].mean())
    


# create two new columns containing name and zip code
df1[['name', 'Zip_Code']] = df1['NAME'].str.split(' ', 1, expand=True)
del df1['NAME']
del df1['name']

test = df1[df1['median_household_income'].notna()]

zip_income = df1.copy()


census_data = pd.merge(zip_population, zip_income, on = 'Zip_Code', how = 'left')

