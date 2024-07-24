"""
generate_jwst_psf
Created on 12-06-2024

@author(s): Sam Beckers

Simulates the Point Spread Function (PSF) of the JWST filters using WebbPSF
"""
import os
os.environ['WEBBPSF_PATH'] = '/Users/sam/FRESCO/webbpsf-data'
from webbpsf import NIRCam, measure_fwhm, display_psf, display_ee
from pathlib import Path
from tqdm import tqdm
import matplotlib.pyplot as plt
plt.rcParams.update({
    "text.usetex": False,
    "font.family": "Times New Roman",
    "font.sans-serif": "helvetica"
})
from paths_and_global_vars import *

def generate_jwst_psf(nircam_filter:str, plot=False, save=False) -> None:
    nc = NIRCam()
    nc.filter = nircam_filter
    if save:
        psf = nc.calc_psf(outfile=str(f_path / f'psf/{nircam_filter}_PSF.fits'), overwrite=True)
    else:
        psf = nc.calc_psf()
    if plot:
        display_psf(psf, ext=1, title=f'{nircam_filter} PSF (Simulated)')
        display_ee(psf)
        plt.savefig(fig_path / f'psf/{nircam_filter}_psf.pdf', dpi=450)

for f in tqdm(nircam_names, total=len(nircam_names)):
    if f != 'F444W':
        continue
    generate_jwst_psf(f, True)

