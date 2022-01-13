# Superusers & EV Adoption in the USA
This Project was created to provide quantitative insights for the white paper 'Gasoline Superusers' (M. Metz. J. London, P. Roesler) and contains three main parts which were largely created independently of each other:
1) Superusers analysis (Python)
2) EV Adoption Policy Model (Excel)
3) Emission Pathways Gasoline Consumption Groups Model (Excel)
4) CA Gasoline Map

The Models for 1-3) are based on historical, publicly available data and forecast, among others, number of Light-Duty-Vehicles, Gasoline Consumption and Emissions. They are constructed to provide insights into possible future scenarios and to evaluate general trends, not to provide an accurate forecast for individual variables. The CA Gasoline Map was created in order to be able presenting insights into gasoline consumption pattern and understand who the drivers with the highest impact on the environment are, a map can help making these patterns visible on geographical level. The data was provided by the DMV California and can be accessed on request. This repository is intended to give an overview of the work, but does not claim to be complete due to the vast amount of datasets and literature used. If there are any questions, please contact us at the address shown below. 

## Superusers
This analysis highlights the importance of Light-Duty-Vehicle gasoline superuser targeted policies for emission reduction in the transportation sector.

To analyze Superusers characteristics, data was taken from the National Household Survey from NHTS 2017 (https://nhts.ornl.gov/).

The nhts_vehpub_data_import_clean_prep_graphs.py file contain data import, cleaning and graph data prepping (graphing was done later on in excel) of the nhts datasets on the vehicles and person level.
Additionally, we provide code on scraped state level vehicle registration panel data from the fhwa highway statistics (highway_statistics.py) and EV registration panel data (ev_registrations.py). 
Some parts of the analysis and code were not used in the paper itself, however, are included in this project.
To model the impact of policies on profiteers, profiteer_models.py was created.


## EV Adoption Models
The folder EV Adoption contains the model for the analysis of different EV adoption policies. Consumption Groups contains files related to the model and the model itself.
In order to evaluate emissions related to different adoption paths of gasoline consumers organized in deciles a model was created and can be found in the folder Consumption Groups. 
For questions about data, methodology and literature please contact: contact@paul-roesler.com


## CA Gasoline Map
The folder CA Gasoline Map contains the python code with the main file dmv_data_import_clean_map.py and further census.py, afdc.py and cec_gasoline_sales.py. The latter three are importing and preparing datasets from Census, Alternative Fuel Data Center and the CEC, links to the sources are provided in the code. The main combines all datasets and runs the other .py files in order to merge, clean and prepare the data to create a folium map about gasoline usage in California. The data provided for DMV is not yet to be published, however here some insights into the structure and content:

The data contains information about transactions of vehicles with the following variables:
  Vehicle_ID: Unique identification number for each vehicle.
  ZIP_Code: Zip Code of the vehicle transaction.
  Make, Model and Model Year: are defining the car maker, model and year of building. 
  The MPG represents the combined EPA MPG for vehicle (Plug-in hybrids use average MPG of the fuel types)
  Ownership:	Personal, Commercial, Government, or Rental sector.
  Owner_Date:	Date the vehicle first appears with a registered owner. Most likely the vehicle purchase date. Not used in this analysis.
  Odometer_Date:	Date of the vehicle's odometer reading.
  Odometer:	Current odometer reading of the vehicle.
  Time_Delta:	Number of years between current and previous odometer readings. Blank for the first time a vehicle appears in the dataset.
  VMT_Delta:	Net VMT between current and previous odometer readings. Blank for the first time a vehicle appears in the dataset.
  Annual_VMT:	Average VMT driven per year. Calculated directly by dividing VMT_Delta by Time Delta.



Copyright © 2021 Coltura & Paul Roesler. All Rights Reserved.
