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


def load_phot(ID):
    """ Load  photometry from catalogue."""

    # load up the relevant columns from the catalogue.
    cat = np.genfromtxt(f_path / cat_folder / f'{cat_name}_catalog_colourcut_sel_formatted_vi.cat', delimiter=' ', names=True, comments='#')
    
    # get the names of the flux and error columns.
    f_header, e_header = [], []
    for n in cat.dtype.names:
        if n.startswith('f_'):
            f_header.append(n)
        if n.startswith('e_'):
            e_header.append(n)
    
    # get the fluxes and errors for the object with the given ID.
    flux, flux_err = [], []
    for f, e in zip(f_header, e_header):
        flux.append(cat[float(ID)==(cat['ID'])][f][0])
        flux_err.append(cat[float(ID)==(cat['ID'])][e][0])
    
    # turn the fluxes and errors into a 2D array (required by BAGPIPES)
    photometry = np.c_[flux, flux_err]

    # blow up the errors associated with any missing fluxes.
    for i in range(len(photometry)):
        if (photometry[i, 0] == 0.) or (photometry[i, 1] <= 0):
            photometry[i,:] = [0., 9.9*10**99.]

    return photometry

# print(load_goodss("141.0"))

filters= np.loadtxt(f_path / f'{cat_name}_filter_paths.txt', dtype="str") # Load filter paths
# print(filters)

galaxy = pipes.galaxy("402", load_phot, spectrum_exists=False, filt_list=filters)
galaxy.plot()

dblplaw = {}                        
dblplaw["tau"] = (0., 15.)                # Vary the time of peak star-formation between
                                          # the Big Bang at 0 Gyr and 15 Gyr later. In 
                                          # practice the code automatically stops this
                                          # exceeding the age of the universe at the 
                                          # observed redshift.
            
dblplaw["alpha"] = (0.01, 1000.)          # Vary the falling power law slope from 0.01 to 1000.
dblplaw["beta"] = (0.01, 1000.)           # Vary the rising power law slope from 0.01 to 1000.
dblplaw["alpha_prior"] = "log_10"         # Impose a prior which is uniform in log_10 of the 
dblplaw["beta_prior"] = "log_10"          # parameter between the limits which have been set 
                                          # above as in Carnall et al. (2017).
dblplaw["massformed"] = (1., 15.)
dblplaw["metallicity"] = (0., 2.5)

dust = {}                           
dust["type"] = "Calzetti"
dust["Av"] = (0., 2.)

nebular = {}
nebular["logU"] = -3.

fit_info = {}                            # The fit instructions dictionary
fit_info["redshift"] = (0., 10.)         # Vary observed redshift from 0 to 10

fit_info["redshift_prior"] = "Gaussian"  # From looking at the spectrum in Example 2 it's
fit_info["redshift_prior_mu"] = 1.0      # clear that this  object is at around z = 1. We'll 
fit_info["redshift_prior_sigma"] = 0.25  # include that information with a broad Gaussian
                                         # prior centred on redshift 1. Parameters of priors
                                         # are passed starting with "parameter_prior_".
fit_info["dblplaw"] = dblplaw 
fit_info["dust"] = dust
fit_info["nebular"] = nebular

fit = pipes.fit(galaxy, fit_info, run="dblplaw_sfh")

fit.fit(verbose=False)

fig = fit.plot_spectrum_posterior(save=True, show=True)
