'''
Author: Paul Roesler
'''

'''
Import DMV data
'''

import pandas as pd
import plotly.figure_factory as ff
import numpy as np
from functools import reduce
import plotly.express as px
import matplotlib.pyplot as plt
import os
import string
import folium 
import matplotlib.pyplot as plt


path = r'PUT_YOUR_DATAPATH_HERE'

# Import DMV Data
dmv_1 = pd.read_csv('\OUT 944 Coltura Part 1.csv')
dmv_2 = pd.read_csv(path + '\OUT 944 Coltura Part 2.csv')

dmv_raw_original = pd.concat([dmv_1,dmv_2])

# store original data
dmv_raw = dmv_raw_original.copy()
# print('average ownership in years (raw): ',dmv_raw['Time_Delta'].mean())

# see data structure
head = dmv_raw.head(10)

'''
Clean and prepare data for analysis
'''
# shift variables -1 to match with actual user at corresponding time
vars_to_shift = ['Time_Delta', 'VMT_Delta', 'Annual_VMT']
for i in vars_to_shift:
    dmv_raw[i] = dmv_raw[i].shift(-1)

#filter out rows that do not contain delta variables
dmv_raw = dmv_raw[(dmv_raw['Time_Delta'].notna()) & (dmv_raw['VMT_Delta'].notna()) & (dmv_raw['Annual_VMT'].notna())]

head = dmv_raw.head(10)


#split odom. date column
dmv_raw[['Year', 'Month', 'Day']] = dmv_raw['Odometer_Date'].str.split('-', 2, expand=True)

# destring new date columns
for i in ['Year', 'Month', 'Day']:
    dmv_raw[i] = pd.to_numeric(dmv_raw[i])

#filter out future reading date
dmv_raw = dmv_raw[dmv_raw['Year'] < 2022]

date_vars = ['Odometer_Date', 'Owner_Date']
for i in date_vars:
    dmv_raw[i] = pd.to_datetime(dmv_raw[i])

# difference between owner and odometer date
dmv_raw['ow_od_time_delta'] = (dmv_raw['Owner_Date'] - dmv_raw['Odometer_Date']).dt.days

# filter out if diff >  1 year
dmv_raw = dmv_raw[dmv_raw['ow_od_time_delta'] < 365]
dmv_raw = dmv_raw[dmv_raw['ow_od_time_delta'] > -365]

# filter out negative values for Time Delta
dmv_raw = dmv_raw[dmv_raw['Time_Delta'] > 0]


# #Top Models without MPG - one time usage
# no_mpg = dmv_raw[dmv_raw['MPG'].isna()] 
# print(len(dmv_raw['MPG']))
# no_mpg_group = no_mpg.groupby(['Make','Model','Model_Year'])['Model'].size()
# no_mpg_group = no_mpg_group.sort_values(ascending=False)
# no_mpg_group_head = no_mpg_group.head(500)
# no_mpg_group_head.to_excel(path + '\Output\models_without_mpg.xlsx')


# import MPG data (manually created dataset for model/make/year and MPG)
mpg_data = pd.read_excel(path + '\Data\211103 Models with MPG.xlsx')
mpg_data = mpg_data.fillna(method='ffill')
dmv_raw = pd.merge(dmv_raw, mpg_data, on = ['Make','Model','Model_Year'], how = 'left')
dmv_raw.MPG.fillna(dmv_raw.EPA_Rating, inplace=True)
del dmv_raw['EPA_Rating']


# exclude all observations that do not include MPG
dmv_raw = dmv_raw[dmv_raw['MPG'].notna()]

# convert Zip tp string
dmv_raw['ZIP_Code'] = dmv_raw['ZIP_Code'].astype(str)


# compute annual gasolinge consumption
dmv_raw['Annual_Gasoline_Consumption'] = dmv_raw['Annual_VMT'] / dmv_raw['MPG']

# exclude all observations that have negative gas consumption
dmv_raw = dmv_raw[dmv_raw['Annual_Gasoline_Consumption'] > 0]

#exclude everything over 70,000 Miles
dmv_raw = dmv_raw[dmv_raw['Annual_VMT'] < 70000]

#exclude everything over 5,000 gallons
dmv_raw = dmv_raw[dmv_raw['Annual_Gasoline_Consumption'] < 5000]

# continue with copy of df
consumption = dmv_raw.copy()

'''
analyse and clean out EVs   
  Clean out the missing EV Models and check comment from Matthew about whether or not to clean out PHEV!!!!!!!
'''

os.chdir("A:\\Upwork\DMV_Data\Code")

# read EV model datafile
exec(open('afdc.py').read())

head = consumption.head(10)

# merge with DMV data on model and make
consumption = pd.merge(consumption, ev_models, on = ['Make', 'Model'], how = 'left')

# check if merge worked and for how many models
type_filled = consumption[consumption['Type'].notna()]
del type_filled['Type']
type_filled_nodup = type_filled.drop_duplicates(['Model', 'Make'])
type_filled_nodup['Merged'] = 1

matched_models = pd.merge(ev_models, type_filled_nodup, on = ['Model', 'Make'], how = 'left')
not_matched = matched_models[matched_models['Merged'].isna()]

make_list = []
for i in not_matched['Make']:
    df = consumption[consumption['Make'] == i]
    df = df.drop_duplicates(['Model', 'Make'])
    df_group = pd.DataFrame(df.groupby(['Model', 'Make']))
    make_list.append(df_group)


# use string contains to fill in Type column
# print('nans in type column: ', len(consumption[consumption['Type'].notna()]))
consumption['Type'] = np.where(consumption['Model'].str.contains('PLUG-IN'), 'PHEV', consumption['Type'] )
# print('nans in type column after plug-in fill: ', len(consumption[consumption['Type'].notna()]))
consumption['Type'] = np.where(consumption['Model'].str.contains('HYBRID'), 'HYBRID', consumption['Type'])
# print('nans in type column after hybrid fill: ', len(consumption[consumption['Type'].notna()]))

# Include missing PHEV, EV, HYBRID vehicles after merge
 # - FORD FOCUS EV (not found)
 # - mercedes b-class (b250e) (not found)
 # - MITSUBISHI I EV
 # - HONDA FIT EV (no distinction between BEV and ICE in data - only FIT)
 # - BMW ACTIVE E (not found)

'''
CHECK FOR TESLA MODEL Y
'''
consumption['Type'] = np.where(consumption['Model'] == 'CLARITY ELECTRIC', 'EV', consumption['Type'])
consumption['Type'] = np.where(consumption['Model'] == 'E-TRON', 'EV', consumption['Type'])
consumption['Type'] = np.where(consumption['Model'] == 'FORTWO ELECTRIC DRIVE', 'EV', consumption['Type'])
consumption['Type'] = np.where(consumption['Model'] == 'IONIQ ELECTRIC', 'EV', consumption['Type'])
consumption['Type'] = np.where(consumption['Model'] == 'IONIQ HYBRID', 'HYBRID', consumption['Type'])
consumption['Type'] = np.where(consumption['Model'] == 'SONATA HYBRID', 'HYBRID', consumption['Type'])
consumption['Type'] = np.where(consumption['Model'] == 'IONIQ PLUG-IN HYBRID', 'PHEV', consumption['Type'])
consumption['Type'] = np.where(consumption['Model'] == 'SONATA PLUG-IN HYBRID', 'PHEV', consumption['Type'])
consumption['Type'] = np.where(consumption['Model'] == 'KONA EV', 'EV', consumption['Type'])
consumption['Type'] = np.where(consumption['Model'] == 'I-MIEV', 'EV', consumption['Type'])
consumption['Type'] = np.where(consumption['Model'] == 'ACTIVE E', 'EV', consumption['Type'])
consumption['Type'] = np.where(consumption['Model'] == 'ACTIVEHYBRID 3', 'HYBRID', consumption['Type'])
consumption['Type'] = np.where(consumption['Model'] == 'ACTIVEHYBRID 5', 'HYBRID', consumption['Type'])
consumption['Type'] = np.where(consumption['Model'] == 'ACTIVEHYBRID X6', 'HYBRID', consumption['Type'])
consumption['Type'] = np.where(consumption['Make'] == 'TESLA', 'EV', consumption['Type'])


# fill type column with gasoline
consumption['Type'] = consumption['Type'].fillna('ICE')
consumption['Type'] = np.where((consumption['MPG'] > 50) & (consumption['Type'].isna()), 'PHEV/EV', consumption['Type'])

type_group = consumption.groupby('Type').size()
type_year_group= pd.DataFrame(consumption.groupby(['Type', 'Year']).size()).reset_index().rename(columns = {0: 'transactions'})

# filter out EVs
ev_df = consumption[consumption['Type'] == 'EV']

ev_df_2018 = ev_df[ev_df['Year'] > 2017]

sum_annual_ev_mileage = round(ev_df_2018['Annual_VMT'].sum(),1)
mean_annual_ev_mileage = round(ev_df_2018['Annual_VMT'].mean(),1)

print('ev milage - ', 'sum: ', sum_annual_ev_mileage, 'mean: ', mean_annual_ev_mileage)

# mpg ICE
ice_df = consumption[consumption['Type'] == 'ICE']
ice_mean_mpg = ice_df['MPG'].mean()
print('mean ice mpg: ', ice_mean_mpg)


# gasoline saved from travel
#number
ev_gas_savings_sample = sum_annual_ev_mileage / ice_mean_mpg
#column, calc for each vehicle
ev_df_2018['gas_savings'] = round(ev_df_2018['Annual_VMT'] / ice_mean_mpg,1)

ev_saving_per_car = ev_df_2018['gas_savings'].sum() / len(ev_df_2018['gas_savings'])

# savings for top 20 EV models
ev_model_saving = pd.DataFrame(ev_df_2018.groupby(['Make','Model'])['gas_savings'].sum().reset_index())
ev_model_saving = ev_model_saving.sort_values(by = 'gas_savings', ascending = False).reset_index()
ev_model_saving.to_excel(path + '\Output\ev_model_saving.xlsx')

# mileage analysis and plottting
mile_categories = ['<5,000', '5,000-9,999', '10,000-14,999', '15,000-19,999', '>25,000']

mileage_18 = consumption[consumption['Year'] > 2017]


# groupby mileage category and type
type_group = mileage_18.groupby(['Type'])['Vehicle_ID'].count().reset_index().rename(columns = {'Vehicle_ID': 'Number_of_Vehicles'})
type_group.to_excel(path + '\Output\type_group.xlsx', index = False)

ev_model_group = mileage_18.groupby(['Model'])['Vehicle_ID'].count().reset_index().rename(columns = {'Vehicle_ID': 'Number_of_Vehicles'})

def group_plotter(df, catergory, name):
    df['mileage_category'] = np.nan
    df['mileage_category'] = np.where(df['Annual_VMT'] < 5000, 5000, df['mileage_category'])
    df['mileage_category'] = np.where((df['Annual_VMT'] >= 5000) & (df['Annual_VMT'] < 10000),\
                                               10000, df['mileage_category'])
    df['mileage_category'] = np.where((df['Annual_VMT'] >= 10000) & (df['Annual_VMT'] < 15000),\
                                               15000, df['mileage_category'])
    df['mileage_category'] = np.where((df['Annual_VMT'] >= 15000) & (df['Annual_VMT'] < 20000),\
                                               20000, df['mileage_category'])
    df['mileage_category'] = np.where(df['Annual_VMT'] > 25000, 25000, df['mileage_category'])

    mileage_group = df.groupby([catergory, 'mileage_category'])['Vehicle_ID'].count().reset_index().rename(columns = {'Vehicle_ID': 'Number_of_Vehicles'})
    mileage_group_pivot = mileage_group.pivot(index='mileage_category', columns= [catergory], values=['Number_of_Vehicles']).reset_index()
    mileage_group_pivot.columns = mileage_group_pivot.columns.droplevel()
    mileage_group_pivot = mileage_group_pivot.rename(columns = {'':'Mileage_Category'})
    
    mileage_group_pivot = mileage_group_pivot.set_index('Mileage_Category')
    mileage_group_pivot = mileage_group_pivot.sort_index()
    
    for i in mileage_group_pivot.columns:
        mileage_group_pivot['share_{}'.format(i)] = mileage_group_pivot[i] / mileage_group_pivot[i].sum()
    
    share_type_miles  = mileage_group_pivot.filter(regex='share')
    share_type_miles['categories'] = mile_categories
    share_type_miles = share_type_miles.set_index('categories')
    
    share_type_miles.columns = share_type_miles.columns.str.lstrip('share_') 
    cols = share_type_miles.columns
    share_type_miles = share_type_miles.reset_index()
    share_type_miles.to_excel(path + '\Output\{}.xlsx'.format(name), index = False)
    #line
    share_type_miles.plot('categories', cols, 'line', xlabel = 'Mileage', ylabel = '% of Vehicle Count in Category')
    plt.tight_layout()
    plt.show()

group_plotter(mileage_18, 'Type', 'share_type_miles')
group_plotter(ev_df_2018, 'Model', 'ev_model_miles')


# filter out all EVs
consumption = consumption[consumption['Type'] == 'ICE']


dmv_clean = consumption.copy()
# print('average ownership in years (clean): ',dmv_clean['Time_Delta'].mean())

# #Most frequent models
freq_models = dmv_clean.groupby(['Make','Model'])['Model'].size()
freq_models_group = freq_models.sort_values(ascending=False).to_frame()
freq_models_group = freq_models_group.rename(columns = {'Model': 'Frequency'})
freq_models_group_head = freq_models_group.head(100)
freq_models_group_head.to_excel(path + '\Output\most_freq_models_dmv_data_cleaned.xlsx')


year_2015 = dmv_clean[dmv_clean['Year'] == 2015]
# print('average ownership in years cars sold 2015: ', year_2015['Time_Delta'].mean())

#create new and long historic timeframe filter for data after 2015
dmv_16 = dmv_clean[dmv_clean['Year'] > 2015]


# create fuel deciles and filter out all that do not have fuel decile (all that are in current use)
def fuel_decile(df):
    df['fuel_decile'] = pd.qcut(df['Annual_Gasoline_Consumption'], 10, labels=False)
    df = df[df['fuel_decile'].notna()]
    return df

dmv_clean = fuel_decile(dmv_clean)
dmv_16 = fuel_decile(dmv_16)

test = dmv_16.head(100)

def decile_ranges(df):
    decile = []
    mins = []
    maxs = []
    for i in range(0,10):
        decile.append(i)
        df_filter = df[df['fuel_decile'] == i]
        min_value = df_filter.min(axis=0)['Annual_Gasoline_Consumption']
        mins.append(min_value)
        max_value = df_filter.max(axis=0)['Annual_Gasoline_Consumption']
        maxs.append(max_value)
    df_out = pd.DataFrame(list(zip(decile,mins, maxs )))
    return df_out
        
fuel_deciles_frontiers = decile_ranges(dmv_16)
fuel_deciles_frontiers.to_excel(path + '\Output\fuel_deciles_frontiers.xlsx')

# analysis of buyer of su vehicles
def buyer_decile(df, name):
    #create shift columns for id and fuel decile to compare pre and current owner
    df['buyer_ID'] = df['Vehicle_ID'].shift(-1)
    df['buyer_fuel_decile'] = df['fuel_decile'].shift(-1)
    
    # find fuel decile for buyer of su cars
    df['su_buyer_fuel_decile'] = np.nan
    df['su_buyer_fuel_decile'] = np.where((df['buyer_ID'] == df['Vehicle_ID']) & (df['fuel_decile'] == 9), df['buyer_fuel_decile'], df['su_buyer_fuel_decile'] )
    
    # group for fuel decile of su car buyers
    su_buyer = pd.DataFrame(df.groupby('su_buyer_fuel_decile')['su_buyer_fuel_decile'].size())
    su_buyer['share'] = su_buyer['su_buyer_fuel_decile'] / su_buyer['su_buyer_fuel_decile'].sum()
    su_buyer.to_excel(path + '\Output\su_buyer_{}.xlsx'.format(name))

buyer_decile(dmv_clean, '96')
buyer_decile(dmv_16, '16')


# top su models
superusers = dmv_16[dmv_16['fuel_decile'] == 9]
superusers_sample = superusers.head(1000).to_excel(path + '\Output\superuser_sample.xlsx')
superusers_group = pd.DataFrame(superusers.groupby(['Make','Model','Model_Year'])['Model'].size()).rename(columns = {'Model': 'number_superusers'})
superusers_group = superusers_group.sort_values('number_superusers',ascending=False)
superusers_group.to_excel(path + '\Output\superuser_models.xlsx')

'''
Grouping for annual consumption total
'''
def annual_consumption(df, name):
    # average consumption per consumption group
    consumption_avg_groups = pd.DataFrame(df.groupby('fuel_decile')['Annual_Gasoline_Consumption'].mean())
    
    # sum of consumption per consumption group
    consumption_sum_groups = pd.DataFrame(df.groupby('fuel_decile')['Annual_Gasoline_Consumption'].sum())
    
    # total consumption & share of consumption of each group compared to total
    consumption_total = df['Annual_Gasoline_Consumption'].sum()
    consumption_sum_groups['Consumption_Share'] = consumption_sum_groups['Annual_Gasoline_Consumption'] / consumption_total
    consumption_sum_groups.to_excel(path + '\Output\consumption_sum_groups_{}.xlsx'.format(name))
    return consumption_sum_groups, consumption_avg_groups

consumption_sum_groups_96, consumption_avg_groups_96 = annual_consumption(dmv_clean, '96')
consumption_sum_groups_16, consumption_avg_groups_16 = annual_consumption(dmv_16, '16')


'''
Grouping for annual consumption by Ownership
'''
# average consumption per consumption group
consumption_avg_ownership = pd.DataFrame(dmv_16.groupby(['fuel_decile', 'Ownership'])['Annual_Gasoline_Consumption'].mean()).reset_index()
owner_type_list = ['Personal', 'Commercial', 'Rental', 'Government']

for i in owner_type_list:
    df_filter = dmv_16[dmv_16['Ownership'] == i]
    df_filter['fuel_percentile'] = pd.qcut(df_filter['Annual_Gasoline_Consumption'], 100, labels=False)
    df_filter_group = df_filter.groupby('fuel_percentile')['Annual_Gasoline_Consumption'].mean()
    df_filter_group.to_excel(path + '\Output\avg_consumption_percentile_{}.xlsx'.format(i))
    

# sum of consumption per consumption group
consumption_sum_ownership = pd.DataFrame(dmv_16.groupby(['fuel_decile', 'Ownership'])['Annual_Gasoline_Consumption'].sum())

# total consumption & and share of consumption of each ownership group compared to sub total
def ownership_share(df, inlist):
    df = df.reset_index()
    df_list = []
    for i in inlist:
        df_filter = df[df['Ownership'] == i]
        consumption_sum = df_filter['Annual_Gasoline_Consumption'].sum()
        df_filter['Consumption_Share'] = df_filter['Annual_Gasoline_Consumption'] / consumption_sum
        df_list.append(df_filter)
        df_filter.to_excel(path + '\Output\consumption_sum_{}.xlsx'.format(i))
    return df_list

ownership_df_list = ownership_share(consumption_sum_ownership, owner_type_list)


'''
Time Trends
'''
# count annual transaction (no consumption needed)
def transactions(df, inlist):
    df_list = []
    for i in inlist:
        df_filter = df[df['Ownership'] == i]
        year_group = df_filter.groupby('Year').size()
        df_list.append(year_group)
    return df_list

annual_transactions = transactions(dmv_clean, owner_type_list)

# annual consumption
def consumption_func(df, inlist):
    df_list = []
    for i in inlist:
        df_filter = df[df['Ownership'] == i]
        year_group_sum = pd.DataFrame(df_filter.groupby('Year')['Annual_Gasoline_Consumption'].sum()).reset_index().rename(columns = {'Annual_Gasoline_Consumption': 'Annual_Gasoline_Consumption_{}'.format(i)})
        year_group_size = pd.DataFrame(df_filter.groupby('Year')['Annual_Gasoline_Consumption'].size()).reset_index().rename(columns = {'Annual_Gasoline_Consumption': 'Number_vehicles_{}'.format(i)})
        df_merge = pd.merge(year_group_sum, year_group_size, on = 'Year')
        df_merge['Consumption_Per_Vehicle_{}'.format(i)] = df_merge['Annual_Gasoline_Consumption_{}'.format(i)] /df_merge['Number_vehicles_{}'.format(i)]
        df_list.append(df_merge)
        #print(i, df_merge['Year'])
    df_out = reduce(lambda df1,df2: pd.merge(df1,df2,on='Year', how = 'left'), df_list)
    df_out['Total_Vehicles'] = df_out['Number_vehicles_Personal'] + df_out['Number_vehicles_Commercial']+ df_out['Number_vehicles_Rental']+ df_out['Number_vehicles_Government']
    number_cols = [col for col in df_out.columns if 'Number' in col]
    for i in number_cols:
        df_out['Share_{}'.format(i)] = df_out[i] / df_out['Total_Vehicles']
    return df_out

annual_consumption = consumption_func(dmv_clean, owner_type_list)
annual_consumption.to_excel(path + '\Output\annual_consumption.xlsx', index = False)

def su_consumption_share(df):
    # calculate share of superusers per year over time
    df_personal = df[df['Ownership'] == 'Personal']
    years = df_personal['Year'].unique()

    for i in years:
        #total
        df_sum_consumption = pd.DataFrame(df_personal.groupby('Year')['Annual_Gasoline_Consumption'].sum()).reset_index().rename(columns = {'Annual_Gasoline_Consumption': 'sum_total'})
        #superusers
        df_su = df_personal[df_personal['fuel_decile'] == 9]
        df_su_consumption = pd.DataFrame(df_su.groupby('Year')['Annual_Gasoline_Consumption'].sum()).reset_index().rename(columns = {'Annual_Gasoline_Consumption': 'sum_su'})
    df_out = pd.merge(df_sum_consumption, df_su_consumption, on = 'Year')
    df_out['share_su_consumption'] = df_out['sum_su'] / df_out['sum_total']
    return df_out

personal_su_annual_consumption = su_consumption_share(dmv_clean).to_excel(path + '\Output\personal_su_annual_consumption.xlsx', index = False)
personal_su_annual_consumption = su_consumption_share(dmv_16).to_excel(path + '\Output\personal_su_annual_consumption_16.xlsx', index = False)


'''
Prep data for graphing
'''

#filter for private and superusers and zip codes with more than 10 vehicles since 2016
personal = dmv_16[dmv_16['Ownership'] == 'Personal']
# superuser df
su_personal = personal[personal['fuel_decile'] == 9]

# groupby zip code and count observations
personal_group = pd.DataFrame(personal.groupby('ZIP_Code').size()).reset_index().rename(columns = {0: 'number_of_transactions', 'ZIP_Code': 'Zip_Code'})
su_personal_group = pd.DataFrame(su_personal.groupby('ZIP_Code').size()).reset_index().rename(columns = {0: 'number_of_transactions', 'ZIP_Code': 'Zip_Code'})


# most frequent su models, only for zips with more than 50 su vehicles
su_zip_vehicles = su_personal_group[su_personal_group['number_of_transactions'] > 50]
su_zip_vehicles = su_zip_vehicles[['Zip_Code', 'number_of_transactions']]
model_freq = pd.DataFrame(su_personal.groupby(['ZIP_Code','Model']).size().reset_index()).rename(columns = {0: 'su_models', 'ZIP_Code': 'Zip_Code'})
model_freq_filter = pd.merge(model_freq, su_zip_vehicles, on = 'Zip_Code', how ='inner')
model_freq_filter['freq_perc'] = round(model_freq_filter['su_models'] / model_freq_filter['number_of_transactions'] *100,0)

top_veh_list = []
for i in model_freq_filter['Zip_Code'].unique():
    df_filter = model_freq_filter[model_freq_filter['Zip_Code'] == i]
    df_filter = df_filter.sort_values(by = 'su_models', ascending=False)
    df_filter = df_filter.head(5)
    top_veh_list.append(df_filter)

top_veh_df = pd.concat(top_veh_list).sort_index()

top_veh_df['rank'] = top_veh_df.groupby('Zip_Code')['su_models'].rank(ascending=False, method='first')
top_veh_df['model_freq'] = top_veh_df['Model'] + ' ' + top_veh_df['freq_perc'].astype(str) + '%'

top_veh_df_pivot = top_veh_df.pivot(index='Zip_Code', columns= ['rank'], values=['model_freq']).fillna('').reset_index()
top_veh_df_pivot.columns = top_veh_df_pivot.columns.droplevel()
top_veh_df_pivot = top_veh_df_pivot.rename(columns = {'':'Zip_Code'})



top_veh_df_pivot['top_models'] = top_veh_df_pivot[1] + ', ' + top_veh_df_pivot[2] +', ' + top_veh_df_pivot[3] + ', ' + \
    top_veh_df_pivot[4] + ', ' + top_veh_df_pivot[5]

top_veh_df_pivot['Zip_Code_num'] = pd.to_numeric(top_veh_df_pivot['Zip_Code'])
top_veh_df_pivot = top_veh_df_pivot[['Zip_Code_num', 'top_models']]

top_veh_df_pivot['top_models'] = [x.title() for x in top_veh_df_pivot['top_models']]


# filter out low number of vehicle zip codes
def nr_vehicle_filter(df, number):
    df = df[df['number_of_transactions'] > number]
    return df

# run code to import and prep population and race data
exec(open('census.py').read())


# group by zip code - su number & merge with census data, add num Zip Code
su_personal_zip = pd.DataFrame(su_personal.groupby('ZIP_Code').size())
su_personal_zip = su_personal_zip.reset_index().rename(columns = {'ZIP_Code': 'Zip_Code', 0: 'nr_private_su'})
su_personal_zip = pd.merge(su_personal_zip, census_data, on = 'Zip_Code', how = 'left')
su_personal_zip['pc_private_su'] = su_personal_zip['nr_private_su'] / su_personal_zip['population_tsd_inhabitants']
su_personal_zip['Zip_Code_num'] = su_personal_zip['Zip_Code']
su_personal_zip['Zip_Code_num'] = pd.to_numeric(su_personal_zip['Zip_Code_num'])


# merge with number of vehicles per zip code
su_personal_zip = pd.merge(su_personal_zip, personal_group, on = 'Zip_Code', how = 'left')
su_personal_zip['su_per_vehicles'] = su_personal_zip['nr_private_su'] / su_personal_zip['number_of_transactions'] *100

# merge with top models
su_personal_zip = pd.merge(su_personal_zip, top_veh_df_pivot, on = 'Zip_Code_num', how = 'left')


# cut off max scale for superuser share
su_personal_zip['su_per_vehicles_cut'] = su_personal_zip['su_per_vehicles']
su_personal_zip['su_per_vehicles_cut'] = np.where(su_personal_zip['su_per_vehicles'] > 25, 25, su_personal_zip['su_per_vehicles_cut'])

# drop nans and exclude low number of vehicle zip codes, create oc df
su_personal_zip = nr_vehicle_filter(su_personal_zip, 10)
pc_private_su = su_personal_zip[['Zip_Code','pc_private_su']].dropna()
pc_private_su['pc_private_su'] = round(pc_private_su['pc_private_su'],0)


# create filter for low number of vehicles Zip Code, group by zip code for sum and average gas consumption
filter_df = nr_vehicle_filter(personal_group, 10)

consumption_sum = pd.DataFrame(personal.groupby('ZIP_Code')['Annual_Gasoline_Consumption'].sum())
consumption_sum = consumption_sum.reset_index().rename(columns = {'Annual_Gasoline_Consumption': 'Annual_Gasoline_Consumption_Sum', 'ZIP_Code': 'Zip_Code'})

consumption_avg = pd.DataFrame(personal.groupby('ZIP_Code')['Annual_Gasoline_Consumption'].mean())
consumption_avg = consumption_avg.reset_index().rename(columns = {'ZIP_Code': 'Zip_Code','Annual_Gasoline_Consumption': 'Annual_Gasoline_Consumption_Avg'})
consumption_avg = pd.merge(consumption_avg, filter_df, on = 'Zip_Code', how = 'left')
del consumption_avg['number_of_transactions']


su_personal_zip = pd.merge(su_personal_zip, consumption_avg, on = 'Zip_Code', how = 'left')
su_personal_zip = pd.merge(su_personal_zip, consumption_sum, on = 'Zip_Code', how = 'left')

# total number of DMV vehicles from >2019
new_cars = personal[personal['Model_Year']>2019]
new_cars_group = pd.DataFrame(new_cars.groupby(['ZIP_Code']).size())
# print('zip codes with more than 10 cars from >2019: ', len(new_cars_group[new_cars_group[0]>10]))

'''
Model 2020 analysis ICE to EV
'''

# registered vehicles per zip code, exclude all rows without zip and fill nans with 0 (not registered = no vehicles of this fuel type)
vehicle_registration_data = pd.read_excel(path + '\Data\Vehicle Population_Last updated 04-30-2021.xlsx', sheet_name= 'ZIP')
vehicle_registration_data = vehicle_registration_data[vehicle_registration_data['ZIP'].notna()]
vehicle_registration_data = vehicle_registration_data.fillna(0)
vehicle_registration_data['type'] = ''
vehicle_registration_data['type'] = np.where((vehicle_registration_data['Fuel Type'] == 'Electric') | \
                                             (vehicle_registration_data['Fuel Type'] == 'PHEV') | \
                                                 (vehicle_registration_data['Fuel Type'] == 'Hydrogen '), 'ev', \
                                                     vehicle_registration_data['type'])
vehicle_registration_data['type'] = np.where(vehicle_registration_data['type'] !=  'ev', 'ice', vehicle_registration_data['type'])

# types, year group
vehicle_registration_type_year = vehicle_registration_data.groupby(['Fuel Type', 'Data Year'])['Number of Vehicles'].sum().reset_index()
vehicle_registration_type_year = vehicle_registration_type_year[['Fuel Type', 'Data Year', 'Number of Vehicles']]
vehicle_registration_type_year['Fuel Type'] = np.where(vehicle_registration_type_year['Fuel Type'] == 'Gasoline Hybrid', 'HYBRID',\
                                                       vehicle_registration_type_year['Fuel Type'])
vehicle_registration_type_year['Fuel Type'] = np.where(vehicle_registration_type_year['Fuel Type'] == 'Electric', 'EV',\
                                                       vehicle_registration_type_year['Fuel Type'])
vehicle_registration_type_year = vehicle_registration_type_year.rename(columns = {'Data Year': 'Year', 'Fuel Type': 'Type', 'Number of Vehicles':'registrations'})

# gasoline saved by EV cars registered in ca
evs_reg_2020 = vehicle_registration_type_year[(vehicle_registration_type_year['Type'] == 'EV') &\
                                                       (vehicle_registration_type_year['Year'] == 2020)] 
ev_gas_savings_ca = evs_reg_2020.iloc[0]['registrations'] * ev_saving_per_car



# compare registration and transactions
veh_trans_reg = pd.merge(vehicle_registration_type_year, type_year_group, on = ['Year', 'Type'], how = 'inner')

# growth rate of EV vehicles
ev_df = vehicle_registration_data[vehicle_registration_data['type'] == 'ev']
ev_group = pd.DataFrame(ev_df.groupby(['ZIP', 'Data Year'])['Number of Vehicles'].sum()).reset_index()
ev_group_pivot = ev_group.pivot(index='ZIP', columns='Data Year', values='Number of Vehicles')
ev_group_pivot['Zip_Code_num'] = ev_group_pivot.index.astype(float)
ev_growth_18 = ev_group_pivot[['Zip_Code_num',2018,2019,2020]]

ev_growth_18['ev_growth_19'] = round((ev_growth_18[2019]-ev_growth_18[2018])/ev_growth_18[2018],2)
ev_growth_18['ev_growth_20'] = round((ev_growth_18[2020]-ev_growth_18[2019])/ev_growth_18[2019],2)
ev_growth_18['avg_ev_growth'] = (ev_growth_18['ev_growth_19'] + ev_growth_18['ev_growth_20']) /2 *100
ev_growth_avg = ev_growth_18[['Zip_Code_num', 'avg_ev_growth']]
su_personal_zip = pd.merge(su_personal_zip, ev_growth_avg, on = 'Zip_Code_num', how = 'left')

# total number of vehicles in 2020
registration_data_2020 = vehicle_registration_data[vehicle_registration_data['Data Year'] == 2020]
number_vehicles = pd.DataFrame(registration_data_2020.groupby(['ZIP'])['Number of Vehicles'].sum()).reset_index().rename(columns = {'Number of Vehicles': 'number_vehicles', 'ZIP':'Zip_Code_num'})
su_personal_zip = pd.merge(su_personal_zip, number_vehicles, on = 'Zip_Code_num', how = 'left')

# new registrations
vehilce_year_group = pd.DataFrame(vehicle_registration_data.groupby(['ZIP', 'Data Year', 'type'])['Number of Vehicles'].sum()).reset_index()

def reg_counter(df, veh_type):
    inlist = []
    df = df[df['type'] == veh_type]
    for i in df['ZIP'].unique():
        df_filter = df[df['ZIP'] == i]
        df_filter = df_filter.sort_values(by = 'Data Year', ascending=True)
        df_filter['new_registrations_{}'.format(veh_type)] = df_filter['Number of Vehicles'].shift(-1) -df_filter['Number of Vehicles']
        df_filter['new_registrations_{}'.format(veh_type)] = df_filter['new_registrations_{}'.format(veh_type)].shift(1)
        inlist.append(df_filter) 
    new_reg_df = pd.concat(inlist).rename(columns = {'Number of Vehicles': '{}_registrations'.format(veh_type)})
    del new_reg_df['type']
    return new_reg_df

ev_reg = reg_counter(vehilce_year_group, 'ev')
ice_reg = reg_counter(vehilce_year_group, 'ice')

reg_def = pd.merge(ev_reg, ice_reg, on = ['ZIP', 'Data Year'], how = 'inner')



# evs in 2020
evs_2020 = ev_group_pivot[['Zip_Code_num',2020]]
evs_2020 = evs_2020.rename(columns = {2020: 'ev_number'})
su_personal_zip = pd.merge(su_personal_zip, evs_2020, on = 'Zip_Code_num', how = 'left')

# ice cars in 2020
ice_cars_2020 = registration_data_2020[registration_data_2020['type'] == 'ice']
ice_cars_2020 = ice_cars_2020.rename(columns = {'Number of Vehicles': 'ice_number', 'ZIP':'Zip_Code_num'})
ice_cars_2020 = ice_cars_2020[['Zip_Code_num','Fuel Type','ice_number']]
ice_cars_2020_group = ice_cars_2020.groupby('Zip_Code_num')['ice_number'].sum()
su_personal_zip = pd.merge(su_personal_zip, ice_cars_2020_group, on = 'Zip_Code_num', how = 'left')


# create share of evs column and ice to ev ratio
su_personal_zip['share_evs'] = su_personal_zip['ev_number'] / su_personal_zip['number_vehicles'] * 100
su_personal_zip['ice_to_ev'] = su_personal_zip['ice_number'] / su_personal_zip['ev_number']

#calculate total consumption by average time total number of cars
su_personal_zip['sum_consumption_avg_calc'] = su_personal_zip['Annual_Gasoline_Consumption_Avg'] * su_personal_zip['number_vehicles']


# round all numerical columns
num_cols = su_personal_zip.columns.to_list()
num_cols.remove('Zip_Code') 

for i in num_cols:
    su_personal_zip[i] = su_personal_zip[i].astype(float, errors='ignore')
    su_personal_zip[i] =  su_personal_zip[i].apply(lambda x: x if isinstance(x, str) else round(x,0))


# integrate name dataset and create zip code name, county variable
zip_names = pd.read_excel(path + '\Data\zip_code_name.xlsx', sheet_name = 'data')
zip_names['zip_name'] = zip_names['Zip Code Name'] + ', ' + zip_names['County']
# print('no zips in name data: ', len(zip_names['zip_name'].notna()))

zip_names = zip_names[['Zip Code', 'zip_name', 'County', 'Zip Code Name']]
zip_names = zip_names.rename(columns = {'Zip Code': 'Zip_Code_num'})
zip_names['Zip_Code_num'] = pd.to_numeric(zip_names['Zip_Code_num'], errors='coerce')
su_personal_zip = pd.merge(su_personal_zip, zip_names, on ='Zip_Code_num', how ='left')

# run code to import and prep population and race data
exec(open('cec_gasoline_sales.py').read())
su_personal_zip = pd.merge(su_personal_zip, gasoline_sales_2019, on ='Zip_Code_num', how ='left')

# calculate share of ev savings to sales
ca_gas_sales = gasoline_sales_2019['gasoline_sales_2019'].sum()
share_gas_savings_sales = ev_gas_savings_ca / ca_gas_sales


#check for merge fails (Modoc & Sierra not in gasoline sales data (probably in row other counties))
zip_nans = su_personal_zip[su_personal_zip['gasoline_sales_2019'].isna()]

'''
County Level
'''
# Total number of vehicles on county level
county_vehicles = pd.read_excel(path + '\Data\Vehicle Population_Last updated 04-30-2021.xlsx', sheet_name= 'County')
county_vehicles = county_vehicles[county_vehicles['Data Year'] == 2020]
county_vehicles_group = pd.DataFrame(county_vehicles.groupby('County')['Number of Vehicles'].sum()).reset_index()
county_vehicles_group = county_vehicles_group.rename(columns = {'Number of Vehicles': 'vehicles_total_county'})

#merge with main dataset
su_personal_zip = pd.merge(su_personal_zip, county_vehicles_group, on ='County', how ='left')


'''
Graph on ZIP Level
'''
# map on ZIP level https://towardsdatascience.com/visualizing-data-at-the-zip-code-level-with-folium-d07ac983db20

###################### load geojsons ###########################

# California
#https://github.com/OpenDataDE/State-zip-code-GeoJSON
import urllib.request, json 
with urllib.request.urlopen("https://raw.githubusercontent.com/OpenDataDE/State-zip-code-GeoJSON/master/ca_california_zip_codes_geo.min.json") as url:
    ca_zip = json.loads(url.read().decode())

# Los Angeles
#https://data.lacounty.gov/GIS-Data/ZIP-Codes-and-Postal-Cities/wft9-k7e3
import geojson
with open(path + '\Data\LA_ZIP_Codes.geojson') as f:
    la_zip = geojson.load(f)



###################### create geojson for region ###########################


#remove ZIP codes not in our dataset
def zip_json(file, region, zip_name):
    geozips = []
    for i in range(len(file['features'])):
        if file['features'][i]['properties'][zip_name] in list(su_personal_zip['Zip_Code'].unique()):
            geozips.append(file['features'][i])
    
    #creating new JSON object
    new_json = dict.fromkeys(['type','features'])
    new_json['type'] = 'FeatureCollection'
    new_json['features'] = geozips
    # save JSON object as updated-file
    open("{}updated-file.json".format(region), "w").write(
        json.dumps(new_json, sort_keys=True, indent=4, separators=(',', ': '))
    )

zip_json(ca_zip, 'ca_', 'ZCTA5CE10')
zip_json(la_zip, 'la_', 'zipcode')



'''
Create Hover Map with folium and geojson
https://towardsdatascience.com/using-folium-to-generate-choropleth-map-with-customised-tooltips-12e4cec42af2
'''

# create list of zip codes from data to plot
zips = su_personal_zip['Zip_Code'].to_list()
print('no zips in DMV data: ', len(zips))


# create list of zip codes that are in geojson and data to plot and list with all zips in geojson
zips_geojson = []
zips_filter = []
for i in range(len(ca_zip['features'])):
    zips_geojson.append(i)
    if ca_zip['features'][i]['properties']['ZCTA5CE10'] in zips:
        zips_filter.append(ca_zip['features'][i]['properties']['ZCTA5CE10'])
# print('no zips in geojson: ', len(zips_geojson))


# filter data to plot for zip codes that are in both datasets
su_personal_zip = su_personal_zip[su_personal_zip['Zip_Code'].isin(zips_filter)]


# create a list with all geodata features that are in both datasets
geozips = []
for i in range(len(ca_zip['features'])):
    if ca_zip['features'][i]['properties']['ZCTA5CE10'] in zips_filter:
        geozips.append(ca_zip['features'][i])

# sore the dictionaries in the list accoring to the zip code
geozips = sorted(geozips, key=lambda d: d['properties']['ZCTA5CE10']) 

#check if Zip Codes in list and column are the same
test_list = []
for i in geozips:
    test_list.append(i['properties']['ZCTA5CE10'])

su_personal_zip['column_check'] = test_list
# print('columns are the same: ',su_personal_zip['column_check'].equals(su_personal_zip['Zip_Code']))


# creating new JSON object
new_json = dict.fromkeys(['type','features'])
new_json['type'] = 'FeatureCollection'
new_json['features'] = geozips

# create df for variables that are presented together
# Race
mult_var_list = ['White', 'Black', 'Latino', 'Asian', 'Native', '2+ Races', 'EV Share', 'EV Number']
for i in mult_var_list:
    su_personal_zip[i] = i

race_list = ['nl_white_perc','nl_black_perc','nl_latino_perc','nl_asian_perc','nl_2+_races_perc','share_evs', 'ev_number']
for i in race_list:
    su_personal_zip[i] = su_personal_zip[i].astype(str)

su_personal_zip['race_info'] = su_personal_zip['White'] + ': ' + su_personal_zip['nl_white_perc'] + '%, '\
    + su_personal_zip['Black'] + ': ' + su_personal_zip['nl_black_perc'] + '%, '\
        + su_personal_zip['Latino'] + ': ' + su_personal_zip['nl_latino_perc'] + '%, '\
            + su_personal_zip['Asian'] + ': ' + su_personal_zip['nl_asian_perc'] + '%, '\
                + su_personal_zip['2+ Races'] + ': ' + su_personal_zip['nl_2+_races_perc'] +'%'

# EV
su_personal_zip['ev_info'] = su_personal_zip['EV Share'] + ': ' + su_personal_zip['share_evs'] + '%, '\
    + 'EVs' + ': ' + su_personal_zip['ev_number'] 

su_personal_zip['avg_ev_growth'] = su_personal_zip['avg_ev_growth'].astype(str)
su_personal_zip['avg_ev_growth'] = su_personal_zip['avg_ev_growth'] + '%'

# City, Zip, Population
su_personal_zip['total_population'] = su_personal_zip['total_population'].astype(str)
su_personal_zip['zip_info'] = su_personal_zip['Zip Code Name'] + ', Zip: ' + su_personal_zip['Zip_Code'] +\
    ', Population: ' + su_personal_zip['total_population']


# format columns
su_personal_zip['share_evs'] = su_personal_zip['share_evs'].astype(float)
su_personal_zip['su_per_vehicles_num']= su_personal_zip['su_per_vehicles'].copy()
su_personal_zip['su_per_vehicles'] = su_personal_zip['su_per_vehicles'].astype(str)
su_personal_zip['su_per_vehicles'] = su_personal_zip['su_per_vehicles'] + '%'


# inlcude df columns as toolip into json
def toolip_creator(df, json,column, text):
    # create list with values that are going to be added to the geodataset
    tooltip_text = df[column].to_list()
    tooltip_text = [str(i) for i in tooltip_text]
    tooltip_text = [i.replace('.0','') for i in tooltip_text]
    tooltip_text = [i.replace('nan','N/A') for i in tooltip_text]
    tooltip_text = [text + ' ' +  s for s in tooltip_text]
    
    # Append a tooltip column with customised text
    for i in range(len(tooltip_text)):
        json['features'][i]['properties']['{}'.format(column)] = tooltip_text[i]
    return json

new_json = toolip_creator(su_personal_zip, new_json,'zip_info','City: ') 
new_json = toolip_creator(su_personal_zip, new_json,'zip_name','Zip Code Name:') 
new_json = toolip_creator(su_personal_zip, new_json,'Zip Code Name','City:') 
new_json = toolip_creator(su_personal_zip, new_json,'Zip_Code_num','Zip:')
new_json = toolip_creator(su_personal_zip, new_json,'total_population','Population:')
new_json = toolip_creator(su_personal_zip, new_json,'race_info','')
new_json = toolip_creator(su_personal_zip, new_json,'ev_info','')
new_json = toolip_creator(su_personal_zip, new_json,'avg_ev_growth','Annual avg growth of EVs since 2018: ')
new_json = toolip_creator(su_personal_zip, new_json,'ice_to_ev','ICE to EV ratio:')
new_json = toolip_creator(su_personal_zip, new_json,'number_of_transactions','Transactions since 2016:')
new_json = toolip_creator(su_personal_zip, new_json,'number_vehicles','Total vehicles:')
new_json = toolip_creator(su_personal_zip, new_json,'Annual_Gasoline_Consumption_Avg','Annual avg gasoline use per vehicle (Gallons):')
new_json = toolip_creator(su_personal_zip, new_json,'gasoline_sales_2019','Gasoline sales (Gallons) in 2019: ')
new_json = toolip_creator(su_personal_zip, new_json,'ev_number','EVs:')
new_json = toolip_creator(su_personal_zip, new_json,'median_household_income','Median Household Income:')
new_json = toolip_creator(su_personal_zip, new_json,'sum_consumption_avg_calc','Average consumption times number of vehicles: ')
new_json = toolip_creator(su_personal_zip, new_json,'Annual_Gasoline_Consumption_Sum','Avg annual total gasoline used in zip code:')
new_json = toolip_creator(su_personal_zip, new_json,'su_per_vehicles','Percentage of Superusers:')
new_json = toolip_creator(su_personal_zip, new_json,'share_evs','Share of Electric Vehicles:')
new_json = toolip_creator(su_personal_zip, new_json,'top_models','Most traded superuser models since 2016: ')


graph_data = su_personal_zip[['Zip_Code', 'share_evs', 'su_per_vehicles_cut']]

scale = [0,5,10,15,5000]
map1 = folium.Map([36.778259, -119.417931], zoom_start=7) # for black/white map: tiles='Stamen Toner'
choropleth = folium.Choropleth(
    geo_data=new_json,
    name='Electric Vehicles',
    data= graph_data,
    columns=['Zip_Code','share_evs'],
    key_on='feature.properties.ZCTA5CE10',
    fill_color= 'PuBuGn', # ‘BuGn’, ‘BuPu’, ‘GnBu’, ‘OrRd’, ‘PuBu’, ‘PuBuGn’, ‘PuRd’, ‘RdPu’, ‘YlGn’, ‘YlGnBu’, ‘YlOrBr’, and ‘YlOrRd’.
    fill_opacity=0.7,
    line_opacity=0.2,
    nan_fill_color = 'white', #greys for black/white map
    #threshold_scale = scale,
    legend_name='Share of Electric Vehicles per Zip Code (%)',
    highlight=True
).add_to(map1)
choropleth.geojson.add_child(
    folium.features.GeoJsonTooltip(['zip_info','ev_info','median_household_income'], labels=False)
)
choropleth = folium.Choropleth(
    geo_data=new_json,
    name='California Driver and Superuser Insights',
    data= graph_data,
    columns=['Zip_Code','su_per_vehicles_cut'],
    key_on='feature.properties.ZCTA5CE10',
    fill_color= 'YlOrBr', # ‘BuGn’, ‘BuPu’, ‘GnBu’, ‘OrRd’, ‘PuBu’, ‘PuBuGn’, ‘PuRd’, ‘RdPu’, ‘YlGn’, ‘YlGnBu’, ‘YlOrBr’, and ‘YlOrRd’.
    fill_opacity=0.7,
    line_opacity=0.2,
    nan_fill_color = 'white',
    legend_name='Share of Superuser (transactions) per Zipcode since 2016 (cut off at 25%)',
    highlight=True
).add_to(map1)
folium.LayerControl(collapsed=False).add_to(map1)
choropleth.geojson.add_child(
    folium.features.GeoJsonTooltip(['zip_info','su_per_vehicles','Annual_Gasoline_Consumption_Avg','gasoline_sales_2019',\
                                    'sum_consumption_avg_calc', 'number_vehicles','ev_info','ice_to_ev', 'avg_ev_growth', 'race_info',\
                                    'median_household_income', 'top_models'], labels=False)
)
map1.save('california_superuser_insights.html')



