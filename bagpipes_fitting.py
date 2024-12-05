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
from paths_and_global_vars import *


def load_phot(ID):
    """ Load  photometry from catalogue."""

    # load up the relevant columns from the catalogue.
    cat = np.genfromtxt(f_path / cat_folder / f'{cat_name}_colour_sel_formatted.cat', delimiter=' ', names=True, comments='#')
    
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

# Load filters
filters= np.loadtxt(f_path / f'names/{cat_name}_filter_paths_bagpipes.txt', dtype="str") # Load filter paths

def model_galaxy_spectrum(obj_id, SFH_model, run_var, gaussian_z_prior=False, z_prior=6.0):
    """Fit a model to the galaxy spectrum.

    Args:
        obj_id (str): ID of the galaxy. E.g. "1061"
        SFH_model (str): Type of star formation history model. Options: "delayed", "dblplaw", "constant"
        run_var (str): Name of the run. E.g. "delayed_final"
        gaussian_z_prior (bool, optional): Whether to include a gaussian redshift prior, Defaults to False.
        z_prior (float, optional): Mean of the redshift prior. Defaults to 6.0.
    """
    # Initalize galaxy object
    galaxy = pipes.galaxy(obj_id, load_phot, spectrum_exists=False, filt_list=filters)
    # galaxy.plot()

    # Delayed SFH model
    delayed = {}
    delayed["age"] = (0.1, 15.)                   # Vary age between 100 Myr and 15 Gyr.
    delayed["tau"] = (0.01, 10.)                   # Vary tau between 10 Myr and 10 Gyr
    delayed["massformed"] = (1., 15.)             # vary log_10(M*/M_solar) between 1 and 15
    delayed["metallicity"] = (0.005, 5)            # vary Z between 0.005 and 5 Z_solar
    delayed["metallicity_prior"] = "log_10"       # Impose a prior which is uniform in log_10

    # Double-power law SFH model
    dblplaw = {}                        
    dblplaw["tau"] = (0.1, 15.)                # Vary the time of peak star-formation between the Big Bang at 0.1 Gyr and 15 Gyr later. 
    dblplaw["alpha"] = (0.01, 1000.)          # Vary the falling power law slope from 0.01 to 1000.
    dblplaw["beta"] = (0.01, 1000.)           # Vary the rising power law slope from 0.01 to 1000.
    dblplaw["alpha_prior"] = "log_10"         # Impose a prior which is uniform in log_10 of the 
    dblplaw["beta_prior"] = "log_10"          # parameter between the limits which have been set above as in Carnall et al. (2017).
    dblplaw["massformed"] = (1., 15.)
    dblplaw["metallicity"] = (0., 2.5)

    # Constant SFH model
    constant = {}                        # tophat function
    constant["age_max"] = 1      # Time since SF switched on: Gyr
    constant["age_min"] = 0.001      # Time since SF switched off: Gyr
    constant["massformed"] = (1., 15.)
    constant["metallicity"] = (0., 2.5)

    # Dust model
    dust = {}                           
    dust["type"] = "Calzetti"
    dust["Av"] = (0., 5.)

    # Nebular emission
    nebular = {}
    nebular["logU"] = -3.

    fit_info = {}                            # The fit instructions dictionary
    fit_info["t_bc"] = 0.01                   # Max age of birth clouds [Gyr]
    fit_info["redshift"] = (0., 15.)         # Vary observed redshift from 0 to 15

    # Redshift prior
    if gaussian_z_prior:
        fit_info["redshift_prior"] = "Gaussian"  
        fit_info["redshift_prior_mu"] = z_prior
        fit_info["redshift_prior_sigma"] = 0.25  

    # SFH model selection
    if SFH_model == "delayed":
        fit_info["delayed"] = delayed
    elif SFH_model == "dblplaw":
        fit_info["dblplaw"] = dblplaw
    elif SFH_model == "constant":
        fit_info["constant"] = constant

    fit_info["dust"] = dust
    fit_info["nebular"] = nebular

    # Fit the model
    print(f'Running {run_var} model...')
    fit = pipes.fit(galaxy, fit_info, run=run_var) # Create a fit object
    fit.fit(verbose=False)

    # Plot the results
    fit.plot_spectrum_posterior(save=True, show=True) # Shows the posterior probability distribution of the spectrum
    fit.plot_1d_posterior(show=True, save=True)        # Shows 1d posterior probability distributions of the parameters

def main():
    for i in ["1061", "1475", "1574"]:
        model_galaxy_spectrum(i, "delayed", "delayed_final")
    model_galaxy_spectrum("829", "delayed", "delayed_gauss", gaussian_z_prior=True, z_prior = 8.0)
    model_galaxy_spectrum("1660", "dplplaw", "dblplaw_gauss", gaussian_z_prior=True, z_prior = 8.0)

if __name__ == "__main__":
    main()