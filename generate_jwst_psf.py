"""
generate_jwst_psf
Created on 12-06-2024

@author(s): Sam Beckers

Simulates the Point Spread Function (PSF) of the JWST filters using WebbPSF
"""
import os
os.environ['WEBBPSF_PATH'] = '/Users/sam/FRESCO/webbpsf-data'
from webbpsf import NIRCam, measure_fwhm, display_psf
from pathlib import Path
from tqdm import tqdm
import matplotlib.pyplot as plt
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "Times New Roman",
    "font.sans-serif": "helvetica"
})
from paths_and_global_vars import *

def generate_jwst_psf(nircam_filter:str, plot=False) -> None:
    nc = NIRCam()
    nc.filter = nircam_filter
    psf = nc.calc_psf(outfile=str(f_path / f'psf/{nircam_filter}_PSF.fits'))
    if plot:
        display_psf(psf, ext=1, title=f'{nircam_filter} PSF (Simulated)')
        plt.savefig(fig_path / f'psf/{nircam_filter}_psf.pdf', dpi=450)

for f in tqdm(nircam_names, total=len(nircam_names)):
    generate_jwst_psf(f, True)
