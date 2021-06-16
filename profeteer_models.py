# -*- coding: utf-8 -*-
"""
Created on Fri Jun  4 15:56:53 2021

@author: HP Envy
"""

'''
Weighting and Sampling
'''
import pandas as pd
import numpy as np
import random

# Scenarios darueber wie viele nie annehmen


vehicles_model = pd.read_excel(r'C:\Users\HP Envy\Dropbox\Gas_Subsidy_Model\1_Input\input_data_financial_model.xlsx')


avg_value_used_vehicle = 22000 # https://www.statista.com/statistics/274928/used-vehicle-average-selling-price-in-the-united-states/
number_cars_usa = 267000000 # Federal Highway Administration. (2021). Federal Highway statistics 2019. https://www.fhwa.dot.gov/policyinformation/statistics/2019/mv1.cfm. Accessed: 02/16/2021 
national_vehicle_loan_value = 1380000000000
avg_ltv = national_vehicle_loan_value / (avg_value_used_vehicle * number_cars_usa)



# calculate ltv per age
vehicles_model['ltv'] = 0.2
vehicles_model['ltv'] = np.where(vehicles_model['VEHYEAR'] == 2017, 0.8, vehicles_model['ltv'])
vehicles_model['ltv'] = np.where(vehicles_model['VEHYEAR'] == 2016, 0.68, vehicles_model['ltv'])
vehicles_model['ltv'] = np.where(vehicles_model['VEHYEAR'] == 2015, 0.56, vehicles_model['ltv'])
vehicles_model['ltv'] = np.where(vehicles_model['VEHYEAR'] == 2014, 0.44, vehicles_model['ltv'])
vehicles_model['ltv'] = np.where(vehicles_model['VEHYEAR'] == 2013, 0.32, vehicles_model['ltv'])
vehicles_model['ltv'] = np.where(vehicles_model['VEHYEAR'] == 2012, 0.20, vehicles_model['ltv'])



# price for EV
vehicles_model['ev_price'] = 55000
vehicles_model['ev_price'] = np.where((vehicles_model['VEHTYPE'] == 1), 44000,vehicles_model['ev_price'] )

avg_value_vehicles = vehicles_model['AVG_USED_PRICE_4'].mean()


#subsidies
gas_subsidy =  0
ev_subsidy = 7500

max_payed = 20000

#loan
interest_rate = 0.0527
loan_term = 6

#maintenance
diff_maintenance_cost_per_mile = 0.03

#cost and usage of electricity and gasoline
price_khw = 0.1
ev_khw_usage = 0.29
gallon_cost = 3


# define subsidies
vehicles_model['gas_subsidy'] = vehicles_model['GSYRGAL'] * gas_subsidy
vehicles_model['gas_subsidy'] = np.where(vehicles_model['gas_subsidy'] > max_payed, max_payed, vehicles_model['gas_subsidy'])

vehicles_model['ev_subsidy'] = ev_subsidy

# define net vehicle price
vehicles_model['gas_subsidy_net_vehicle_price'] = vehicles_model['ev_price'] - (vehicles_model['AVG_USED_PRICE_4'] * (1-avg_ltv)) - vehicles_model['gas_subsidy']
# print('avg net price gas subsidy:', round(vehicles_model['gas_subsidy_net_vehicle_price'].mean()))
vehicles_model['ev_subsidy_net_vehicle_price'] = vehicles_model['ev_price'] - (vehicles_model['AVG_USED_PRICE_4'] * (1-avg_ltv)) - vehicles_model['ev_subsidy']
# print('avg net price ev subsidy:', round(vehicles_model['ev_subsidy_net_vehicle_price'].mean()))

# calculate fuel and electricy costs
vehicles_model['ev_khw_cost'] = price_khw * ev_khw_usage * vehicles_model['BESTMILE']
vehicles_model['fuel_savings'] = vehicles_model['GSTOTCST'] - vehicles_model['ev_khw_cost']
# print('avg annual savings:', round(vehicles_model['fuel_savings'].mean()))

#loan payments
vehicles_model['gas_subsidy_an_loan_payments'] = vehicles_model['gas_subsidy_net_vehicle_price'] * (interest_rate * ((1 + interest_rate)**loan_term)) / (((1 + interest_rate)**loan_term)-1)
vehicles_model['gas_subsidy_an_loan_payments'] = np.where(vehicles_model['gas_subsidy_an_loan_payments'] < 0, 0, vehicles_model['gas_subsidy_an_loan_payments'])
# print('avg annual loan payments gas subsidy:', round(vehicles_model['gas_subsidy_an_loan_payments'].mean()))

vehicles_model['ev_subsidy_an_loan_payments'] = vehicles_model['ev_subsidy_net_vehicle_price'] * (interest_rate * ((1 + interest_rate)**loan_term)) / (((1 + interest_rate)**loan_term)-1)
vehicles_model['ev_subsidy_an_loan_payments'] = np.where(vehicles_model['ev_subsidy_an_loan_payments'] < 0, 0, vehicles_model['ev_subsidy_an_loan_payments'])
# print('avg annual loan payments ev subsidy:', round(vehicles_model['ev_subsidy_an_loan_payments'].mean()))

# maintenance costs
vehicles_model['an_maintenance_savings'] = diff_maintenance_cost_per_mile * vehicles_model['BESTMILE']
# print('avg annual maintenance savings:', round(vehicles_model['an_maintenance_savings'].mean()))

# efficient annual final cost per vehicle
vehicles_model['gas_subsidy_effective_savings'] =  vehicles_model['fuel_savings'] - vehicles_model['gas_subsidy_an_loan_payments'] + vehicles_model['an_maintenance_savings']
# print('avg annual effective savings gas subsidy:', round(vehicles_model['gas_subsidy_effective_savings'].mean()))
vehicles_model['ev_subsidy_effective_savings'] =  vehicles_model['fuel_savings'] - vehicles_model['ev_subsidy_an_loan_payments'] + vehicles_model['an_maintenance_savings']
# print('avg annual effective savings ev subsidy:', round(vehicles_model['ev_subsidy_effective_savings'].mean()))


#groups profiteers, which groups are making wins anyway and who can be switched

# profiteers
gas_subsidy_profiteurs = vehicles_model[vehicles_model['gas_subsidy_effective_savings'] > 0]
print('avg annual gas_subsidy:', gas_subsidy_profiteurs['gas_subsidy_effective_savings'].mean())
ev_subsidy_profiteurs = vehicles_model[vehicles_model['ev_subsidy_effective_savings'] > 0]
print('avg annual ev_subsidy:', round(ev_subsidy_profiteurs['ev_subsidy_effective_savings'].mean()))


# count vehicles_model and superusers for which a trade in would be benefitial financially and compute share
gas_subsidy_profiteurs_number= gas_subsidy_profiteurs['VEHID'].count()
gas_subsidy_profiteurs_superusers = gas_subsidy_profiteurs[gas_subsidy_profiteurs['fuel_decile'] == 9 ]['VEHID'].count()
print('gas_subsidy_profiteurs_superusers:', round(gas_subsidy_profiteurs_superusers,2))
print('share gas_subsidy_profiteurs_superusers:', round(gas_subsidy_profiteurs_superusers/ gas_subsidy_profiteurs_number,2))


ev_subsidy_profiteurs_number= ev_subsidy_profiteurs['VEHID'].count()
ev_subsidy_profiteurs_superusers = ev_subsidy_profiteurs[ev_subsidy_profiteurs['fuel_decile'] == 9 ]['VEHID'].count()
print('ev_subsidy_profiteurs_superusers:', round(ev_subsidy_profiteurs_superusers))
print('share ev_subsidy_profiteurs_superusers:', round(ev_subsidy_profiteurs_superusers/ ev_subsidy_profiteurs_number,2))


#share of profiteers and superusers
total_count = vehicles_model['VEHID'].count() 
gas_subsidy_profiteurs_share = gas_subsidy_profiteurs_number / total_count
# print('gas_subsidy_profiteurs_share:', round(gas_subsidy_profiteurs_share,2))
ev_subsidy_profiteurs_share = ev_subsidy_profiteurs_number / total_count
# print('ev_subsidy_profiteurs_share:', round(ev_subsidy_profiteurs_share,2))


# compute amount of gasoline saved due to the policy
gas_subsidy_profiteurs_usage= gas_subsidy_profiteurs['GSYRGAL'].sum()
print('gas_subsidy_profiteurs_usage:', round(gas_subsidy_profiteurs_usage,2))

ev_subsidy_profiteurs_usage = ev_subsidy_profiteurs['GSYRGAL'].sum()
print('ev_subsidy_profiteurs_usage:', round(ev_subsidy_profiteurs_usage,2))


# usage of profiteers
total_usage = vehicles_model['GSYRGAL'].sum() 
gas_subsidy_profiteurs_savings = gas_subsidy_profiteurs_usage / total_usage
ev_subsidy_profiteurs_savings = ev_subsidy_profiteurs_usage / total_usage
print('gas_subsidy_profiteurs_savings:', round(gas_subsidy_profiteurs_savings,4))
print('ev_subsidy_profiteurs_savings:', round(ev_subsidy_profiteurs_savings,4))

# total subsidyn of profiteers
gas_subsidy_total = gas_subsidy_profiteurs['gas_subsidy'].sum()
#print('gas_subsidy_total:', round(gas_subsidy_total))
ev_subsidy_total = ev_subsidy_profiteurs['ev_subsidy'].sum()
#print('ev_subsidy_total:', round(ev_subsidy_total))

# scale to national level
number_cars_nhts = len(vehicles_model['VEHID'])
number_cars_usa = 267000000
scaling = number_cars_usa / number_cars_nhts
gas_subsidy_scaled_usa = gas_subsidy_total * scaling
print('gas subsidy in billion dollars:', round(gas_subsidy_scaled_usa / 1000000000))
ev_subsidy_scaled_usa = ev_subsidy_total * scaling
print('ev subsidy in billion dollars:', round(ev_subsidy_scaled_usa / 1000000000))

# budget of 100 billion

# print('per dollar gas subsidy:', gas_subsidy_total/gas_subsidy_profiteurs_usage)
# print('per dollar ev subsidy:', ev_subsidy_total/ev_subsidy_profiteurs_usage)


print('---------------------------------------------')

'''
Random and weighted random sampling
'''

sample_size = 10000

def profiteur_calculator(df, column):
    # create profiteurs deciles
    df['profiteurs_decile'] = pd.qcut(df['{}_subsidy_effective_savings'.format(column)], 10, labels=False)
    
    # compute decile and weight
    df['profiteurs_decile'] = np.where(df['profiteurs_decile'] == 0, 0.5, df['profiteurs_decile'])
    df['profiteurs_decile'] = df['profiteurs_decile'] / 10
    
    sampleList = df['ID']
      
    weighted_random_choice = pd.DataFrame(random.choices(sampleList, weights=df['profiteurs_decile'], k=sample_size)).rename(columns = {0: 'ID'})
    random_choice = pd.DataFrame(df['ID'].sample(n=sample_size, random_state=1))
    
    buyers_weighted = pd.merge(weighted_random_choice, df, on = 'ID', how = 'inner')
    #print('buyers_weighted avg subsidy {} :'.format(column), round(buyers_weighted['{}_subsidy'.format(column)].mean()))
    buyers_equal = pd.merge(random_choice, df, on = 'ID', how = 'inner')
    print('subsidy payed to {} buyers (100,000):'.format(column), round(buyers_weighted['{}_subsidy'.format(column)].sum()/100000,1), round(buyers_equal['{}_subsidy'.format(column)].sum()/100000,1))
    print('gallons replaced {}:'.format(column), round(buyers_weighted['GSYRGAL'].sum()/100000), round(buyers_equal['GSYRGAL'].sum()/100000))
    print('share of gasoline replaced {}'.format(column), round(buyers_weighted['GSYRGAL'].sum()/total_usage,3), round(buyers_equal['GSYRGAL'].sum()/total_usage,3))
    print('dollars spent per gallon {}'.format(column), round(buyers_weighted['{}_subsidy'.format(column)].sum()/buyers_weighted['GSYRGAL'].sum(),1), round(buyers_equal['{}_subsidy'.format(column)].sum()/buyers_equal['GSYRGAL'].sum(),1))
    print('gallons replaced per vehicle {}'.format(column), round(buyers_weighted['GSYRGAL'].mean()), round(buyers_equal['GSYRGAL'].mean()))
    
    return buyers_weighted, buyers_equal


gas_subsidy_weighted, gas_subsidy_equal = profiteur_calculator(vehicles_model, 'gas')
ev_subsidy_weighted, ev_subsidy_equal = profiteur_calculator(vehicles_model, 'ev')


# count vehicles per group
def counter(df):
    count_list = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    vehicles_per_group = []
    for i in count_list:
        gas_item = df[df.profiteurs_decile == i]['ID'].count()
        vehicles_per_group.append(gas_item)
    return vehicles_per_group
   
print('vehicles in gas subsidy groups:', counter(gas_subsidy_weighted))
print('vehicles in ev subsidy groups:', counter(ev_subsidy_weighted))