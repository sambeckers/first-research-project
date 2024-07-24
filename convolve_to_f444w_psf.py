"""
convolve_to_f444w_psf
Created on 12-06-2024

@author(s): Sam Beckers

Simulates the Point Spread Function (PSF) of the JWST filters using WebbPSF
"""
from paths_and_global_vars import *
import glob
import numpy as np
from astropy.convolution import convolve, convolve_fft
from astropy.io import fits
from tqdm import tqdm

def get_pixel_scale(sci_imgs):
    """Get the pixel scale of the science images.

    Args:
        sci_imgs (list): List of science images (HDUList objects) 
                         including CD2_2 (Coordinate transformation matrix element) header keyword.
    Returns:
        pixelscales (list): List of pixel scales in arcseconds per pixel for each science image.
    """
    pixelscales = []
    for i, f in zip(sci_imgs, f_names):
        pixscl = i.header['CD2_2']*3600 # Pixel scale in arcseconds / pixel
        pixelscales.append(pixscl)
        # print(f'{f} pixel scale: {pixscl} arcseconds/px')
    return pixelscales

def pypher_commands(pixel_scales) -> None:
    """Prints the commands to add pixel scales to the PSF files and to create the convolution kernels using pypher.

    Args:
        pixel_scales (list): List of pixel scales in arcseconds/pixel for each science image.
    """
    print(f'addpixscl F444W_PSF.fits {pixel_scales[-1]}')
    for f, p in zip(f_names, pixel_scales):
        if f == 'F444W':
            continue
        print(f'addpixscl {f}_PSF.fits {p}')
        print(f'pypher {f}_PSF.fits F444W_PSF.fits kernel_{f}_to_F444W.fits')

def convolution(sci_imgs, wht_imgs, sci_filenames, wht_filenames) -> None:
    # Store the kernel data along with their filenames
    kernel_data = [(fits.open(f_path / 'psf' / f'kernel_{f}_to_F444W.fits')[0], f'kernel_{f}_to_F444W.fits') for f in f_names if f != 'F444W']

    def convolve(image, kernel, filename) -> None:
        convolved_data = convolve_fft(image.data, kernel.data, allow_huge=True,
                                      nan_treatment='interpolate', preserve_nan=True)
        convolved_filename = f_path / 'convolved' / f'c_crop_{filename}'
        fits.writeto(convolved_filename, convolved_data, header=image.header, overwrite=True)
        print(f'Convolved image saved to {convolved_filename}')
    
    # skip_filters = ['f336wu', 'f435w', 'f606w', 'f606wu', 'f775w', 'f814w', 'f850lp', 'f277w', 'f335m', 'f356w', 'f410m', 'f460m', 'f480m', 'f105w', 'f444w']
    for sci, wht, (kernel, kernel_filename), sci_f, wht_f in zip(sci_imgs, wht_imgs, kernel_data, sci_filenames, wht_filenames):
        # if any(filter in sci_f for filter in skip_filters):
        #     continue
        print(f'Convolving {sci_f} and {wht_f} with {kernel_filename}')
        convolve(sci, kernel, sci_f)
        convolve(wht, kernel, wht_f)


def main():
    sci_filenames = open(f_path / f'names/{cat_name}_sci_filenames.txt', 'r').read().splitlines()
    wht_filenames = open(f_path / f'names/{cat_name}_wht_filenames.txt', 'r').read().splitlines()
    def open_imgs(filenames):
        return [fits.open(f_path / reprojected / f'reproj_crop_{f}')[0] for f in filenames]
    sci_imgs = open_imgs(sci_filenames)
    wht_imgs = open_imgs(wht_filenames)
    # pypher_commands(get_pixel_scale(sci_imgs))
    convolution(sci_imgs, wht_imgs, sci_filenames, wht_filenames)

if __name__ == '__main__':
    main()