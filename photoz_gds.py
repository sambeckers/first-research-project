"""
photoz_FRESCO
Created on 18-02-2024

@author(s): Sam Beckers


"""
import os
print(os.getcwd())
os.chdir('/Users/sam/eazy-photoz')
print(os.getcwd())
import numpy as np
import matplotlib.pyplot as plt
import eazy

import warnings
from astropy.utils.exceptions import AstropyWarning

np.seterr(all='ignore')
warnings.simplefilter('ignore', category=AstropyWarning)

# Set multiprocessing start method
# import multiprocessing as mp
# mp.set_start_method('fork')

f_path = '/Users/sam/Fresco/'

params = {}
params['CATALOG_FILE'] = f_path + 'Catalogs/gds_catalog_v2.cat'
params['CATALOG_FORMAT'] = 'ascii'
params['OUTPUT_DIRECTORY'] = f_path + 'eazy outputs'
params['MAIN_OUTPUT_FILE'] = f_path + 'eazy outputs/gds_photoz.eazypy'

params['Z_MAX'] = 20
params['Z_STEP'] = 0.005
params['PRIOR_ABZP'] = 23.9
params['PRIOR_FILTER'] = 375
params['MW_EBV'] = 0.1909
params['CAT_HAS_EXTCORR'] = False

# Planck flat lambda CDM cosmology (Plank Colloboration et al. 2020)
params['H0'] = 67.36
params['OMEGA_M'] = 0.3153
params['OMEGA_L'] = 0.6847

params['WAVELENGTH_FILE'] = 'templates/uvista_nmf/lambda.def'

params['PRIOR_FILE'] = 'templates/prior_F160W_TAO.dat'
params['TEMPLATES_FILE'] = 'templates/spline_templates_v3/c2020_spline.param'
params['TEMP_ERR_FILE'] = 'templates/template_error_cosmos2020.txt'
params['TEMP_ERR_A2'] = 1.
params['SYS_ERR'] = 0.05

params['FILTERS_RES'] = 'filters/FILTER.RES.latest'

translate_file = 'inputs/zphot.translate'

# from eazy import filters, utils
# res = filters.FilterFile('/Users/sam/eazy-photoz/filters/FILTER.RES.latest')
# print(res.NFILT)

# for i in range(res.NFILT):
#     print(f'{i+1} {res.filters[i].name}')

self = eazy.photoz.PhotoZ(param_file=None, translate_file=translate_file, zeropoint_file=None, 
                          params=params, load_prior=True, load_products=False)

# def rest_frame_fluxes_no_multiprocessing(self, f_numbers):
#     return self.rest_frame_fluxes(f_numbers=[153, 154, 155, 161], pad_width=0.5, 
#                                   max_err=0.5, ndraws=1000, percentiles=[2.5, 16, 50, 84, 97.5], 
#                                   simple=False, verbose=1, fitter='nnls', n_proc=0, par_skip=10000)

# Override the rest_frame_fluxes method with the wrapper function
# self.rest_frame_fluxes(f_numbers=[153, 154, 155, 161], pad_width=0.5, 
#                                   max_err=0.5, ndraws=1000, percentiles=[2.5, 16, 50, 84, 97.5], 
#                                   simple=False, verbose=1, fitter='nnls', n_proc=0, par_skip=10000)
# self.abs_mag(f_numbers=[271, 272, 274], cosmology=None, rest_kwargs={'percentiles':[2.5,16,50,84,97.5], 'pad_width':0.5, 'max_err':0.5, 'verbose':False, 'simple':False, 'n_proc':0})

self.fit_catalog()



# self.set_template_error(TEF=None)

# Derived parameters (z params, RF colors, masses, SFR, etc.)
# warnings.simplefilter('ignore', category=RuntimeWarning)
self.standard_output()

