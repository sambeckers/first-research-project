"""
SE_commands_FRESCO_catalogs
Created on 16-11-23

@author(s): Sam Beckers

Generates strings of sextractor commands to run on the command line to generate catalogs for FRESCO
"""
import os
from paths_and_global_vars import *

# Open files with image names, weight names and catalog names:
measurement_file = f_path / 'names' / f'{cat_name}_sci_filenames_excl_f444w.txt'
weight_file = f_path / 'names' / f'{cat_name}_wht_filenames_excl_f444w.txt'
catalog_file = f_path / 'names' / 'cat_names.txt'

# Read files and split into lists:
with open(measurement_file, 'r') as measurement_file:
    measurement_images = measurement_file.read().splitlines()

with open(weight_file, 'r') as weight_file:
    weight_images = weight_file.read().splitlines()

with open(catalog_file, 'r') as catalog_file:
    catalog_names = catalog_file.read().splitlines()

# Generate sextractor commands:
for measurement, weight, catalog in zip(measurement_images, weight_images, catalog_names):
    print(f'sex crop_gds-grizli-v7.2-f444w-clear_drc_sci.fits, c_crop_{measurement} -WEIGHT_IMAGE crop_gds-grizli-v7.2-f444w-clear_drc_wht.fits,c_crop_{weight} -CATALOG_NAME {catalog}')

