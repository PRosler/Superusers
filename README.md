# Superusers & Ev Adoption in the USA
This Project was created to provide quantitative insights for the white paper 'Gasoline Superusers' (M. Metz. J. London, P. Roesler) and contains three main parts:
1) Superusers analysis (Python)
2) EV Adoption Policy Model (Excel)
3) Emission Pathways Gasoline Consumption Groups Model (Excel)

This repository is intended to give an overview of the work, but does not claim to be complete due to the amount of datasets used and individual parts of the analysis. If there are any questions, please contact us at the address shown below.

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



Copyright © 2021 Coltura & Paul Roesler. All Rights Reserved.
