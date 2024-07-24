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
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "Times New Roman",
    "font.sans-serif": "helvetica"
})
import eazy
import eazy.hdf5

# Suppress warnings
import warnings
from astropy.utils.exceptions import AstropyWarning
np.seterr(all='ignore')
warnings.simplefilter('ignore', category=AstropyWarning)

f_path = '/Users/sam/Fresco/' # Path to the FRESCO directory

# Define the parameters for the EAZY fitting
params = {}
params['CATALOG_FILE'] = f_path + 'catalogs_v3/gds_filtered.cat'
params['CATALOG_FORMAT'] = 'ascii' # important to specify the format
params['OUTPUT_DIRECTORY'] = f_path + 'eazy outputs'
params['MAIN_OUTPUT_FILE'] = f_path + 'eazy outputs/gds_photoz.eazypy'
params['N_MIN_COLORS'] = 3 # Minimum number of colors
params['NOT_OBS_THRESHOLD'] = -90 # Threshold for non-detection

params['Z_MAX'] = 15 # Maximum redshift
params['Z_STEP'] = 0.005 # Redshift step
params['PRIOR_ABZP'] = 23.9 # AB zeropoint
params['PRIOR_FILTER'] = 375
params['MW_EBV'] = 0.1909 # Milky Way E(B-V) reddening
params['CAT_HAS_EXTCORR'] = False # Catalog has extinction correction

params['H0'] = 70.0
params['OMEGA_M'] = 0.3
params['OMEGA_L'] = 0.7

params['WAVELENGTH_FILE'] = 'templates/uvista_nmf/lambda.def'
params['PRIOR_FILE'] = 'templates/prior_F160W_TAO.dat'
params['TEMPLATES_FILE'] = 'templates/sfhz/corr_sfhz_13.param'
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

# Write to HDF5 file
eazy.hdf5.write_hdf5(self, h5file=self.param['MAIN_OUTPUT_FILE'] + '.h5')