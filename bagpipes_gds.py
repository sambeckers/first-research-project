"""
bagpipes_gds
Created on 01-06-2024

@author(s): Sam Beckers


"""

import numpy as np 
import bagpipes as pipes
import matplotlib.pyplot as plt
import os
from pathlib import Path
from astropy.io import fits

f_path = Path('/Users/sam/FRESCO/') # Path to the FRESCO directory
fig_path = Path('/Users/sam/Documents/GitHub/FRP/Figures/')
fig_fits_path = fig_path / 'colour_colour_fits/'
cat_folder = 'Catalogs_v2'
eazy_folder = 'eazy outputs'
cat_filter_names = 'catalog-names_incl_f444w.txt'
cat_name = 'gds'


def load_goodss(ID):
    """ Load  photometry from catalogue. """

    # load up the relevant columns from the catalogue.
    cat = np.genfromtxt(f_path / cat_folder / f'{cat_name}_catalog_colourcut_sel_formatted_vi.cat', delimiter=' ', names=True, comments='#')
    
    f_header, e_header = [], []
    for n in cat.dtype.names:
        if n.startswith('f_'):
            f_header.append(n)
        if n.startswith('e_'):
            e_header.append(n)
    
    flux, flux_err = [], []
    for f, e in zip(f_header, e_header):
        flux.append(cat[float(ID)==(cat['ID'])][f][0])
        flux_err.append(cat[float(ID)==(cat['ID'])][e][0])
    
    photometry = np.c_[flux, flux_err]

    return photometry

# print(load_goodss("141.0"))

filters= np.loadtxt(f_path / f'{cat_name}_filter_paths.txt', dtype="str") # Load filter paths
# print(filters)

galaxy = pipes.galaxy("2472", load_goodss, spectrum_exists=False, filt_list=filters)
galaxy.plot()

exp = {}                                  # Tau-model star-formation history component
exp["age"] = (0., 15.)                   # Vary age between 100 Myr and 15 Gyr. In practice 
                                          # the code automatically limits this to the age of
                                          # the Universe at the observed redshift.

exp["tau"] = (0.3, 10.)                   # Vary tau between 300 Myr and 10 Gyr
exp["massformed"] = (1., 15.)             # vary log_10(M*/M_solar) between 1 and 15
exp["metallicity"] = (0., 2.5)            # vary Z between 0 and 2.5 Z_oldsolar

dust = {}                                 # Dust component
dust["type"] = "Calzetti"                 # Define the shape of the attenuation curve
dust["Av"] = (0., 2.)                     # Vary Av between 0 and 2 magnitudes

fit_instructions = {}                     # The fit instructions dictionary
fit_instructions["redshift"] = (0., 10.)  # Vary observed redshift from 0 to 10
fit_instructions["exponential"] = exp   
fit_instructions["dust"] = dust

fit = pipes.fit(galaxy, fit_instructions)

fit.fit(verbose=False)

fig = fit.plot_spectrum_posterior(save=False, show=True)
