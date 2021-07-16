# -*- coding: utf-8 -*-
"""
Created on Sat May  1 08:27:53 2021

@author: HP Envy
"""
from io import BytesIO
from zipfile import ZipFile
import pandas as pd
from urllib.request import urlopen


# import data from nhts website - vehicle dataset
# variables codebook: https://nhts.ornl.gov/tables09/CodebookBrowser.aspx
z = urlopen('https://nhts.ornl.gov/assets/2016/download/csv.zip')
myzip = ZipFile(BytesIO(z.read())).extract('vehpub.csv')
vehicles = pd.read_csv(myzip)

#filter for variables of interest
vehicles = vehicles[['HOUSEID', 'VEHID', 'HH_CBSA', 'PERSONID', 'HBHUR', 'ANNMILES', 'BESTMILE', 'FUELTYPE', 'GSTOTCST', 'GSYRGAL',\
                     'HHFAMINC','HFUEL', 'FEGEMPG' ,'HHSTATE', 'HHSTFIPS', 'HHVEHCNT','MAKE', 'MODEL', 'OD_READ', \
                         'VEHTYPE', 'VEHYEAR', 'VEHAGE', 'MSACAT', 'HH_RACE', 'HH_HISP']]
    
test = vehicles[['HOUSEID', 'VEHID','PERSONID']]
# create individual vehicle ID
vehicles['HOUSEID'] = vehicles['HOUSEID'].astype(str)
vehicles['VEHID'] = vehicles['VEHID'].astype(str)

vehicles['ID'] = vehicles.loc[:,'HOUSEID'] + vehicles.loc[:,'VEHID']

#check if its unique
#print('number of IDs that are not unique:', vehicles.duplicated(subset='ID', keep='first').sum())


#exclude cars that do not report on gasoline usage (annual gallons)
vehicles = vehicles[(vehicles['GSYRGAL'] != -9)]
vehicles = vehicles[(vehicles['VEHTYPE'] != 7)]


'''
EV vehicles
'''
evs = vehicles[vehicles['HFUEL'] == 3]
#print('ev mileage average:',evs['BESTMILE'].mean())

# ev vehicles income groups
ev_income = pd.DataFrame(evs.groupby(['HHFAMINC']).size().reset_index())
ev_income.to_excel(r'C:\Users\HP Envy\Dropbox\Gas_Subsidy_Model\3_Output\ev_income.xlsx')

#ev mileage
ranges = [0, 5000, 10000, 15000, 20000, 40000]
ev_miles = evs.groupby(pd.cut(evs.BESTMILE, ranges)).count()
ev_miles = ev_miles[['VEHID']]
ev_miles['%'] = ev_miles['VEHID'] / ev_miles['VEHID'].sum()



'''
per HH
'''
cars_per_hh = pd.DataFrame(vehicles.groupby(['HOUSEID']).size().reset_index())
cars_per_hh = cars_per_hh[0].mean()


'''
Scale Usage to USA level
'''
total_usage_nhts = vehicles['GSYRGAL'].sum()
number_cars_nhts = len(vehicles['GSYRGAL'])
number_cars_usa = 267000000
scaling = number_cars_usa / number_cars_nhts
gas_scaled_usa = total_usage_nhts * scaling
#print('gasoline consumption in billion gallons:', gas_scaled_usa / 1000000000)

'''
PREP DATA FOR GRAPHING
'''

vehicles['fuel_decile'] = pd.qcut(vehicles['GSYRGAL'], 10, labels=False)

usage_list = list(range(0, 3000, 10))
usage_groups = vehicles.groupby(pd.cut(vehicles.GSYRGAL, usage_list)).count()
usage_groups = usage_groups[['GSYRGAL']]
usage_groups.to_excel(r'C:\Users\HP Envy\Dropbox\Gas_Subsidy_Model\3_Output\usage_groups.xlsx')

nhts_data = vehicles[['HOUSEID', 'VEHID','HHSTATE', 'HHSTFIPS', 'HH_CBSA', 'GSYRGAL', 'fuel_decile']]


vehicles_ca = vehicles[vehicles['HHSTATE'] == 'CA']


percentiles = list(range(0,100,1))
percentiles = [x / 100 for x in percentiles]

fuel_percentiles = []
for i in percentiles:
    value = vehicles['GSYRGAL'].quantile(i)
    fuel_percentiles.append(value)



fuel_percentiles = pd.DataFrame(fuel_percentiles)
fuel_percentiles = fuel_percentiles.rename(columns = {0:'Annual fuel consumption in US gallons'})



'''
States Map, SUperusers
'''

df = pd.read_excel(r'C:\Users\HP Envy\Dropbox\Gas_Subsidy_Model\3_Output\table_states.xlsx', sheet_name = 'data')
pd.options.display.float_format = '{:.2%}'.format

df = df.dropna()
values = df['share_superusers_usage'].tolist()
scope = df['state'].tolist()
fips = df['FIPS'].tolist()

import plotly.express as px

fig = px.choropleth(locations=scope, locationmode="USA-states", color=values, scope="usa")
fig.show()
fig.write_image(file = r'C:\Users\HP Envy\Dropbox\Gas_Subsidy_Model\superusers_density.png', format='png')


import plotly.graph_objects as go


fig = go.Figure(data=go.Choropleth(
    locations=df['state'], # Spatial coordinates
    z = df['share_superusers_usage'], # Data to be color-coded
    locationmode = 'USA-states', # set of locations match entries in `locations`
    colorscale = 'Blues',
    colorbar_title = "Share of Gasoline used by Superusers",
))

fig.update_layout(
    title_text = 'Superusers in the USA',
    geo_scope='usa', # limite map scope to USA
)
fig = fig.update_yaxes(tickformat="%")
fig.show()



'''
EV
'''

import plotly.graph_objects as go


fig = go.Figure(data=go.Choropleth(
    locations=df['state'], # Spatial coordinates
    z = df['EV Share'], # Data to be color-coded
    locationmode = 'USA-states', # set of locations match entries in `locations`
    colorscale = 'Greens',
    colorbar_title = "Share EV Registrations",
))

fig.update_layout(
    title_text = 'Share of EVs registered per State',
    geo_scope='usa', # limite map scope to USA
)
fig = fig.update_yaxes(tickformat="%")
fig.show()







'''
Vehicle Models 
'''

models = vehicles.groupby(['VEHYEAR', 'MODEL', 'MAKE']).size().reset_index(name='Freq')
models = models[models['VEHYEAR'] > 0]


models = models[models['MODEL'] != 'XXXXX']
models = models[models['MAKE'] != 'XX']

models['MAKE'] = models['MAKE'].astype(float)
models['MODEL'] = models['MODEL'].astype(float)
models = models[models['MODEL'] < 70000]




models = models.sort_values('Freq', ascending = False)
models_sample = models.head(200)


sell_prices = pd.read_excel('FILE VEHICLE_VALUES').iloc[:, :5]
model_vehicles_data = pd.read_excel('FILE organize_sample_model.xlsx', sheet_name = 'data')

sell_price_data = pd.merge(sell_prices, model_vehicles_data, on = ['VEHYEAR', 'MAKE_NAME', 'MODEL_NAME'], how = 'inner').rename(columns = {'VEH YEAR + 4 PRICE': 'AVG_USED_PRICE_4'})
sell_price_data['MODEL'] = sell_price_data['MODEL'].astype('str')
vehicles = pd.merge(vehicles, sell_price_data, on = ['VEHYEAR', 'MODEL'], how = 'left')


'''
Create dataset for the model
'''

# filter out vehicles without sell price info
vehicles_model = vehicles[vehicles.AVG_USED_PRICE_4.notnull() ]
vehicles_model = vehicles_model[vehicles_model['AVG_USED_PRICE_4'] != 'No Data Available']

total_car_value = vehicles_model['AVG_USED_PRICE_4'].sum()
number_cars_model = len(vehicles_model['GSYRGAL'])
number_cars_usa = 267000000
scaling = number_cars_usa / number_cars_model
gas_scaled_usa = total_usage_nhts * scaling





'''
Graph Data Output
'''
income_usage = vehicles[(vehicles['VEHTYPE'] > 0)]
gas_usage_income_deciles = pd.DataFrame(income_usage.groupby(pd.qcut(income_usage.GSYRGAL, 10))['HHFAMINC'].mean())

# prep and export 
def graph_data_prepper(df, var1, var2, name, filter_group):
    # clean (exclude 'I dont know', no answer etc)
    df_clean = df[(df[var1] > 0)]
    # group by input variables
    group = pd.DataFrame(df_clean.groupby([var1, var2]).size().reset_index())
    #filter for the group of interest
    filtered_df = group[group[var2] == 9]
    #export to excel
    filtered_df.to_excel(r'C:\Users\HP Envy\Dropbox\Gas_Subsidy_Model\3_Output\{}.xlsx'.format(name))
    total = df_clean[df_clean[var2] != 9]
    total = pd.DataFrame(total.groupby([var1]).size().reset_index())

    return filtered_df




'''
USA
'''
# use graph_data_prepper  to export information about variables of interest
income_usage = graph_data_prepper(vehicles, 'HHFAMINC', 'fuel_decile', 'usage_income', 9)
metrolpolitan = graph_data_prepper(vehicles, 'MSACAT', 'fuel_decile', 'metrolpolitan', 9)
age_usage = graph_data_prepper(vehicles, 'VEHAGE', 'fuel_decile', 'age_usage', 9)
# additional cleaning step for vehicle type & fuel type
vehicle_type = vehicles[(vehicles['VEHTYPE'] != 97)]
vehicle_type = graph_data_prepper(vehicle_type, 'VEHTYPE', 'fuel_decile', 'vehicle_type', 9)

fuel_type = vehicles[(vehicles['FUELTYPE'] != 97)]
fuel_type = graph_data_prepper(fuel_type, 'FUELTYPE', 'fuel_decile', 'fuel_type', 9)

race = graph_data_prepper(vehicles, 'HH_RACE', 'fuel_decile', 'race', 9)
hispanic = graph_data_prepper(vehicles, 'HH_HISP', 'fuel_decile', 'hispanic', 9)




# mpg
mpg = vehicles[(vehicles['FEGEMPG'] > 0)]
mpg = pd.DataFrame(mpg.groupby(['fuel_decile'])['FEGEMPG'].mean().reset_index())

#bestmile
bestmile = vehicles[(vehicles['BESTMILE'] >= 0)]
bestmile_group = pd.DataFrame(bestmile.groupby(['fuel_decile'])['BESTMILE'].mean().reset_index())
bestmile_mean = bestmile['BESTMILE'].mean()
bestmile_no_superusers = bestmile[bestmile['fuel_decile'] != 9]
bestmile_no_superusers = bestmile['BESTMILE'].mean()

# fuel usage
fuel_usage = pd.DataFrame(vehicles.groupby(['fuel_decile'])['GSYRGAL'].mean().reset_index())
fuel_usage.to_excel(r'C:\Users\HP Envy\Dropbox\Gas_Subsidy_Model\3_Output\fuel_usage.xlsx')





# location usage extra as cleaning cannot include >0 (str)
location_usage = vehicles[(vehicles['HBHUR'] != -9)]
location_usage_total = location_usage[location_usage['fuel_decile'] != 9]
location_usage_total = pd.DataFrame(location_usage_total.groupby(['HBHUR']).size().reset_index())

# location superusers
location_usage = pd.DataFrame(location_usage.groupby(['HBHUR', 'fuel_decile']).size().reset_index())
location_usage = location_usage[location_usage['fuel_decile'] == 9]

# location usage fur EVs
location_evs = evs[(evs['HBHUR'] != -9)]
location_evs = pd.DataFrame(location_evs.groupby(['HBHUR']).size().reset_index())



# CA location usage extra as cleaning cannot include >0 (str)
location_usage_ca = vehicles[(vehicles['HBHUR'] != -9)]
location_usage_ca = pd.DataFrame(location_usage_ca.groupby(['HBHUR', 'fuel_decile']).size().reset_index())
location_usage_ca = location_usage_ca[location_usage_ca['fuel_decile'] == 9]





# gas usage deciles
gas_usage_deciles = pd.DataFrame(vehicles.groupby(pd.qcut(vehicles.GSYRGAL, 10))['GSYRGAL'].sum())
gas_usage_deciles['fuel_consumption_deciles_%'] = gas_usage_deciles['GSYRGAL'] / gas_usage_deciles['GSYRGAL'].sum()
gas_usage_deciles = gas_usage_deciles.rename(columns = {'GSYRGAL': 'sum_ann_fuel_consumption'})

# average age
age = vehicles[(vehicles['VEHAGE'] > 0)]
age = pd.DataFrame(age.groupby(pd.qcut(age.GSYRGAL, 10))['VEHAGE'].mean())
age.to_excel(r'C:\Users\HP Envy\Dropbox\Gas_Subsidy_Model\3_Output\age.xlsx')

# average age
age_ca = vehicles_ca[(vehicles_ca['VEHAGE'] > 0)]
age_ca = pd.DataFrame(age_ca.groupby(pd.qcut(age_ca.GSYRGAL, 10))['VEHAGE'].mean())
age_ca.to_excel(r'C:\Users\HP Envy\Dropbox\Gas_Subsidy_Model\3_Output\age_ca.xlsx')


# sort by metro area 
def sort_df(df, var1, var2, name):
    df1 = pd.DataFrame(df.groupby([var1, var2]).size().reset_index())
    df1 = df1[df1[var2] == 9]
    df1.columns = [var1, var2, 'count_decile']
    df1_groups = pd.DataFrame(vehicles.groupby([var1]).size().reset_index())
    df1_groups.columns = [var1, 'count_total']
    df1 = pd.merge(df1, df1_groups, how = 'inner', on = var1)
    df2 = pd.DataFrame(df.groupby([var1])['GSYRGAL'].sum().reset_index())
    df2_decile = pd.DataFrame(df.groupby([var1, var2])['GSYRGAL'].sum().reset_index())
    df2_decile = df2_decile[df2_decile[var2] == 9]
    df2 = pd.merge(df2, df2_decile, how = 'inner', on = var1)
    df1 = pd.merge(df1, df2, how = 'inner', on = var1)
    return df1
    
    
    
    

superusers_cities = sort_df(vehicles, 'HH_CBSA', 'fuel_decile', 'metro_cities')
superusers_cities = superusers_cities[superusers_cities['HH_CBSA'] != 'XXXXX']
superusers_cities['HH_CBSA'] = superusers_cities['HH_CBSA'].astype(float)


superusers_states = sort_df(vehicles, 'HHSTATE', 'fuel_decile', 'superusers_states')



#Superusers count per houshold
superusers = vehicles[vehicles['fuel_decile'] == 9]
non_superusers = vehicles[vehicles['fuel_decile'] != 9]
print(non_superusers['BESTMILE'].mean())

superusers_hid = pd.DataFrame(superusers.groupby(['HOUSEID']).size().reset_index(name='count'))
superusers_hid = superusers_hid[superusers_hid['count'] > 1]

# Superusers and population favorite Models

def favorite(df, head):
    df = df.rename(columns = {'MAKE_x': 'MAKE'})
    df = df.groupby(['MODEL', 'MAKE']).size().reset_index(name='Freq')
    df = df[df['MODEL'] != 'XXXXX']
    df = df[df['MAKE'] != 'XX']
    df['MAKE'] = df['MAKE'].astype(float)
    df['MODEL'] = df['MODEL'].astype(float)
    df = df[df['MODEL'] < 70000]
    df = df.sort_values('Freq', ascending = False)
    df = df.head(head)
    return df

pop_fav = favorite(vehicles, 15)

su_fav = favorite(superusers, 15)

total_freq = favorite(vehicles, 300)
total_freq = total_freq.rename(columns = {'Freq': 'Freq_total'})


su_fav = pd.merge(su_fav, total_freq, how = 'left', on = ['MODEL', 'MAKE'])
su_fav['superusers_share_total'] = su_fav['Freq'] / su_fav['Freq_total']
su_fav['superusers_share_internal'] = su_fav['Freq'] / len(superusers['ID'])



vehicles = vehicles.rename(columns = {'MAKE_x': 'MAKE'})
model_consumption = vehicles.groupby(['MODEL', 'MAKE'])['GSYRGAL'].sum().reset_index(name='consumption_sum').sort_values('consumption_sum', ascending = False).head(10)
model_freq = favorite(vehicles,600)
model_consumption['MODEL'] = model_consumption['MODEL'].astype(float)
model_consumption['MAKE'] = model_consumption['MAKE'].astype(float)

model_consumption_freq = pd.merge(model_consumption, model_freq, on = ['MODEL', 'MAKE'], how = 'left')
model_consumption_freq['freq_%'] = model_consumption_freq['Freq'] / len(vehicles['MODEL'])

total_gasoline_consumption_2019 = 142000000000

model_consumption_freq['consumption_model_usa'] = model_consumption_freq['freq_%'] * total_gasoline_consumption_2019
