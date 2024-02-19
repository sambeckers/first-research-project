"""
full_FRESCO_catalog
Created on 20-01-2024

@author(s): Sam Beckers

Reaads in the catalogs from all filters, and combines them into one catalog. The catalog has an ID number for each source, 
and has each SE parameter for each filter. If a source doesn't have a value for a parameter in a filter, it is set to 0 (expection: fluxes are set to -100 such
that they are below the observation threshold of eazy). The output catalog is compliant with eazy input requirements.
"""
import os
import numpy as np
os.chdir('/Users/sam/FRESCO')

# Read in the catalog names
cat_names = []
with open('catalog-names_incl_f444w.txt', 'r') as catalog_file:
    catalog_names = catalog_file.read().splitlines()
    for cat_name in catalog_names:
        cat_names.append(cat_name)

# Read in the catalogs
os.chdir("/Users/sam/FRESCO/Catalogs")
columns = [[[] for _ in range(len(cat_names))] for _ in range(20)] # 20 empty lists for each parameter, empty lists within for each filter
for idx, cat_name in enumerate(cat_names):
    with open(cat_name, 'r') as catalog:
        for row in catalog:
            # Skip comment lines that start with #
            if row.startswith('#'):
                continue
            row_val= row.split() # Split the row into a list of values
            for i in range(len(row_val)): # Loop over the values in the row
                columns[i][idx].append(row_val[i]) # Add the value to the corresponding parameter and filter

# Find the maximum number of sources in a catalog
number_arr = []  
for i in range(len(columns)):
    number_arr.append(len(columns[0][i]))
max_sources_idx = np.argmax(number_arr)
ID = columns[0][max_sources_idx]
print(number_arr)

del columns[0] # Remove the ID column

# Write the catalogs to a new file
filters = [cat_name.split('_')[0][3:] for cat_name in cat_names] # Get the filter names from the catalog names
parameters_to_save = [
    'f', 'e', 'MAG_APER', 'MAGERR_APER', 'XPEAK_IMAGE', 'YPEAK_IMAGE',
    'XPEAK_WORLD', 'YPEAK_WORLD', 'ALPHAPEAK_J2000', 'DELTAPEAK_J2000', 'X_IMAGE', 'Y_IMAGE',
    'ALPHA_J2000', 'DELTA_J2000', 'FLAGS', 'CLASS_STAR', 'FLUX_RADIUS', 'XMODEL_IMAGE', 'YMODEL_IMAGE'
] #from SE
header = ['# id'] # Start the header with the source ID
for param in parameters_to_save:
    for filter_name in filters:
        header.append(f'{param}_{filter_name}') # Add the parameter and filter to the header

with open('gds_catalog.cat', 'w') as catalog_file:
    catalog_file.write(' '.join(header) + '\n')
    for source_idx in range(len(ID)): # Loop over the sources
        output_row = [ID[source_idx]]  # Start each row with the source ID
        for param_idx, param in enumerate(parameters_to_save):
            for filter_name in filters:
                # Get the corresponding value for the current source, parameter, and filter
                value = columns[param_idx][filters.index(filter_name)][source_idx]
                output_row.append(value)

        # Append the row to the output file
        print('Saving full catalog...')
        catalog_file.write(' '.join(output_row) + '\n')
