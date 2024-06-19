"""
convolve_to_f444w_psf
Created on 12-06-2024

@author(s): Sam Beckers

Simulates the Point Spread Function (PSF) of the JWST filters using WebbPSF
"""
from paths_and_global_vars import *

def pypher_commands():
    for f in f_names:
        if f == 'F444W':
            continue
        print(f'pypher {f}_PSF.fits F444W_PSF.fits kernel_{f}_to_F444W.fits')
# pypher_commands()

from astropy.io import fits

def fix_header(file_name):
    try:
        with fits.open(file_name, mode='update', ignore_missing_end=True) as hdul:
            hdul.verify('fix')
            hdul.flush()
    except Exception as e:
        print(f"Failed to fix {file_name}: {e}")

def verify_and_fix_hdu(file_name):
    try:
        with fits.open(file_name, mode='update', ignore_missing_end=True) as hdul:
            # for hdu in hdul:
            #     try:
            #         hdu.verify('fix')
            #     except Exception as e:
            #         print(f"Error verifying HDU {hdu.name} in {file_name}: {e}")
            hdr = hdul[0].header
            hdr.apppend(('END', 'End of header'), end=True, verify=False)
            hdul.flush()
    except Exception as e:
        print(f"Failed to verify and fix {file_name}: {e}")
        
def rewrite_fits(file_name):
    try:
        with fits.open(file_name, ignore_missing_end=True) as hdul:
            hdul.writeto(file_name, overwrite=True)
    except Exception as e:
        print(f"Failed to rewrite1 {file_name}: {e}")


verify_and_fix_hdu(f_path / 'psf' / 'F814WU_PSF.fits')
# fix_header(f_path / 'psf' / 'F200W_PSF.fits')
# fix_header(f_path / 'psf' / 'F444W_PSF.fits')