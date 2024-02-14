"""
SE_commands_FRESCO_catalogs
Created on 16-11-23

@author(s): Sam Beckers

Generates strings of sextractor commands to run on the command line to generate catalogs for FRESCO
"""
import os
os.chdir('/Users/sam/FRESCO')

# Open files with image names, weight names and catalog names:
measurement_file = 'gds-sci-filenames.txt'
weight_file = 'gds-wht-filenames.txt'
catalog_file = 'catalog-names.txt'

# Read files and split into lists:
with open(measurement_file, 'r') as measurement_file:
    measurement_images = measurement_file.read().splitlines()

with open(weight_file, 'r') as weight_file:
    weight_images = weight_file.read().splitlines()

with open(catalog_file, 'r') as catalog_file:
    catalog_names = catalog_file.read().splitlines()

# Generate sextractor commands:
for measurement, weight, catalog in zip(measurement_images, weight_images, catalog_names):
    print(f'sex gds-grizli-v5.1-f444w-clear_drc_sci.fits,{measurement} -WEIGHT_IMAGE gds-grizli-v5.1-f444w-clear_drc_wht.fits,{weight} -CATALOG_NAME {catalog}')

