"""
photoz_gds
Created on 18-02-2024

@author(s): Sam Beckers

Eazy photo-z fitting for the GDS catalog
"""
import os
os.chdir('/Users/sam/eazy-photoz') # Change to the eazy-photoz directory
print(os.getcwd())
import numpy as np
import matplotlib.pyplot as plt
import eazy

# Suppress warnings
import warnings
from astropy.utils.exceptions import AstropyWarning
np.seterr(all='ignore')
warnings.simplefilter('ignore', category=AstropyWarning)

f_path = '/Users/sam/Fresco/' # Path to the FRESCO directory

# Define the parameters for the EAZY fitting
params = {}
params['CATALOG_FILE'] = f_path + 'Catalogs/gds_catalog.cat'
params['CATALOG_FORMAT'] = 'ascii' # important to specify the format
params['OUTPUT_DIRECTORY'] = f_path + 'eazy outputs'
params['MAIN_OUTPUT_FILE'] = f_path + 'eazy outputs/gds_photoz.eazypy'

params['Z_MAX'] = 20 # Maximum redshift
params['Z_STEP'] = 0.005 # Redshift step
params['PRIOR_ABZP'] = 23.9 # AB zeropoint
params['PRIOR_FILTER'] = 375
params['MW_EBV'] = 0.1909 # Milky Way E(B-V) reddening
params['CAT_HAS_EXTCORR'] = False # Catalog has extinction correction

# Planck flat lambda CDM cosmology (Plank Colloboration et al. 2020)
params['H0'] = 67.36
params['OMEGA_M'] = 0.3153
params['OMEGA_L'] = 0.6847 

params['WAVELENGTH_FILE'] = 'templates/uvista_nmf/lambda.def'
params['PRIOR_FILE'] = 'templates/prior_F160W_TAO.dat'
params['TEMPLATES_FILE'] = 'templates/spline_templates_v3/c2020_spline.param'
params['TEMP_ERR_FILE'] = 'templates/template_error_cosmos2020.txt'
params['TEMP_ERR_A2'] = 1. # Template error amplitude
params['SYS_ERR'] = 0.05 # Systematic error

params['FILTERS_RES'] = 'filters/FILTER.RES.latest'
translate_file = 'inputs/zphot.translate'

# Initialize the photo-z object
self = eazy.photoz.PhotoZ(param_file=None, translate_file=translate_file, zeropoint_file=None, 
                          params=params, load_prior=True, load_products=False)

# Fit the catalog to the templates
self.fit_catalog()

# Save the results
self.standard_output()

