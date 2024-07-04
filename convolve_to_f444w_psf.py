"""
convolve_to_f444w_psf
Created on 12-06-2024

@author(s): Sam Beckers

Simulates the Point Spread Function (PSF) of the JWST filters using WebbPSF
"""
from paths_and_global_vars import *
import numpy as np


def pypher_commands():
    for f in f_names:
        if f == 'F444W':
            continue
        print(f'pypher {f}_PSF.fits F444W_PSF.fits kernel_{f}_to_F444W.fits')
pypher_commands()

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

def pad_to_even_shape(data):
    padded_data = data
    if data.shape[0] % 2 != 0:
        # Pad with one row of zeros at the bottom
        padded_data = np.pad(padded_data, ((0, 1), (0, 0)), mode='constant')
    if data.shape[1] % 2 != 0:
        # Pad with one column of zeros at the right
        padded_data = np.pad(padded_data, ((0, 0), (0, 1)), mode='constant')
    return padded_data

# verify_and_fix_hdu(f_path / 'psf' / 'F814WU_PSF.fits')
# # fix_header(f_path / 'psf' / 'F200W_PSF.fits')
# # fix_header(f_path / 'psf' / 'F444W_PSF.fits')

# Load the FITS files
f105w_psf = fits.open(f_path / 'psf' / 'F105W_PSF.fits')
f444w_psf = fits.open(f_path / 'psf' / 'F444W_PSF.fits')
f606w_psf = fits.open(f_path / 'psf' / 'F606W_PSF.fits')

f105w_data = f105w_psf[0].data

# Pad the data with zeros to have even dimensions
f105w_data_padded = pad_to_even_shape(f105w_data)
fits.writeto(f_path / 'psf' / 'F105W_PSF_padded.fits', f105w_data_padded, header=f105w_psf[0].header, overwrite=True)

# Print the shape of the data
print("F105W PSF shape:", f105w_psf[0].data.shape)
print("F105w PSF padded shape:", f105w_data_padded.shape)
print("F444W PSF shape:", f444w_psf[0].data.shape)
print("F606W PSF shape:", f606w_psf[0].data.shape)

# Close the FITS files
f105w_psf.close()
f444w_psf.close()