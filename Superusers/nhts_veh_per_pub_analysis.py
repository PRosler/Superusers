# -*- coding: utf-8 -*-
"""
Created on Sun Jun 13 13:52:14 2021

@author: HP Envy
"""
from io import BytesIO
from zipfile import ZipFile
import pandas as pd
from urllib.request import urlopen
import numpy as np
def data_import_id(name):
    z = urlopen('https://nhts.ornl.gov/assets/2016/download/csv.zip')
    myzip = ZipFile(BytesIO(z.read())).extract('{}.csv'.format(name))
    df =  pd.read_csv(myzip)
    
    #filter for variables of interest
    df['HOUSEID'] = df['HOUSEID'].astype(str)
    df['PERSONID'] = df['PERSONID'].astype(str)
    
    df['PID'] = df.loc[:,'HOUSEID'] + df.loc[:,'PERSONID']
    #print('number of IDs that are not unique:', persons.duplicated(subset='PID', keep='first').sum())
    return df

vehicles = data_import_id('vehpub')
vehicles['fuel_decile'] = pd.qcut(vehicles['GSYRGAL'], 10, labels=False)

persons = data_import_id('perpub')


merge = pd.merge(vehicles, persons, how = 'inner', on = 'PID')

merge = merge[['PID', 'OCCAT', 'fuel_decile', 'GSYRGAL', 'GSTOTCST', 'GCDWORK', 'DISTTOWK17',\
              'DISTTOSC17', 'R_AGE', 'R_SEX', 'WKFTPT', 'HHFAMINC_x', 'WALK_DEF', 'WALK_GKQ', 'WKRMHM', 'VPACT',\
                  'TIMETOWK', 'HEALTH', 'GT1JBLWK', 'EDUC']]

# prep and export 
def graph_data_prepper(df, var1, var2, name, filter_group):
    # clean (exclude 'I dont know', no answer etc)
    df_clean = df[(df[var1] > 0)]
    # group by input variables
    group = pd.DataFrame(df_clean.groupby([var1, var2]).size().reset_index())
    #filter for the group of interest
    filtered_df = group[group[var2] == filter_group]
    #export to excel
    filtered_df.to_excel(r'C:\Users\HP Envy\Dropbox\Gas_Subsidy_Model\3_Output\{}.xlsx'.format(name))
    total = pd.DataFrame(df_clean.groupby([var1]).size().reset_index())
    total.to_excel(r'C:\Users\HP Envy\Dropbox\Gas_Subsidy_Model\3_Output\{}_total.xlsx'.format(name))

    
graph_data_prepper(merge, 'OCCAT', 'fuel_decile', 'usage_person_job', 9)
graph_data_prepper(merge, 'WALK_DEF', 'fuel_decile', 'person_work_nowalk_inf', 9)
graph_data_prepper(merge, 'WALK_GKQ', 'fuel_decile', 'person_work_nowalk_saf', 9)
graph_data_prepper(merge, 'WKRMHM', 'fuel_decile', 'person_work_opt_work_home', 9)
graph_data_prepper(merge, 'HEALTH', 'fuel_decile', 'person_health', 9)
graph_data_prepper(merge, 'GT1JBLWK', 'fuel_decile', 'person_more_jobs', 9)
graph_data_prepper(merge, 'EDUC', 'fuel_decile', 'person_educ', 9)



#distance to work mileage
def grouper(var, df, ranges, name):
    df_clean = merge[merge[var] >= 0]
    df_clean = df_clean[[var, 'fuel_decile']]
    df_grouped = df_clean.groupby(pd.cut(df_clean[var], ranges)).count()
    df_grouped.to_excel(r'C:\Users\HP Envy\Dropbox\Gas_Subsidy_Model\3_Output\{}_total.xlsx'.format(name))
    
    df_filtered = df_clean[df_clean['fuel_decile'] == 9]
    df_grouped_filtered = df_filtered.groupby(pd.cut(df_filtered[var], ranges)).count()
    df_grouped_filtered.to_excel(r'C:\Users\HP Envy\Dropbox\Gas_Subsidy_Model\3_Output\{}.xlsx'.format(name))


ranges_miles_distance = [0, 5, 10, 15, 20, 50, 100, 5000]
workout = [0, 10, 20, 30, 40, 50]
work_way = list(range(0, 700,100))

grouper('DISTTOWK17', merge, ranges_miles_distance, 'person_work_distance')
grouper('DISTTOSC17', merge, ranges_miles_distance, 'person_school_distance')
grouper('VPACT', merge, workout, 'person_time_phy_act')
grouper('TIMETOWK', merge, work_way, 'person_time_work_way')



# asign avg income per group
merge['avg_income'] = np.nan
merge['avg_income'] = np.where(merge['HHFAMINC_x'] == 1, 5000, merge['avg_income'])
merge['avg_income'] = np.where(merge['HHFAMINC_x'] == 2, 12500, merge['avg_income'])
merge['avg_income'] = np.where(merge['HHFAMINC_x'] == 3, 20000, merge['avg_income'])
merge['avg_income'] = np.where(merge['HHFAMINC_x'] == 4, 30000, merge['avg_income'])
merge['avg_income'] = np.where(merge['HHFAMINC_x'] == 5, 42500, merge['avg_income'])
merge['avg_income'] = np.where(merge['HHFAMINC_x'] == 6, 57500, merge['avg_income'])
merge['avg_income'] = np.where(merge['HHFAMINC_x'] == 7, 87500, merge['avg_income'])
merge['avg_income'] = np.where(merge['HHFAMINC_x'] == 8, 112500, merge['avg_income'])
merge['avg_income'] = np.where(merge['HHFAMINC_x'] == 9, 137500, merge['avg_income'])
merge['avg_income'] = np.where(merge['HHFAMINC_x'] == 10, 175000, merge['avg_income'])
merge['avg_income'] = np.where(merge['HHFAMINC_x'] == 11, 200000, merge['avg_income'])

# gasoline spendings
merge.loc[:,'share_gasoline_exp'] = merge.loc[:,'GSTOTCST'] / merge.loc[:,'avg_income']
gas_spending = merge[merge['GSTOTCST'] >= 0]
gas_spending = gas_spending[gas_spending['HHFAMINC_x'] >= 0]
gas_spending = gas_spending.groupby(['fuel_decile']).mean()
gas_spending = gas_spending[['share_gasoline_exp']]
