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
# import scipy
# fft_mp = lambda a: scipy.fft.fftn(a, workers=-1)  # use all available cores
# ifft_mp = lambda a: scipy.fft.ifftn(a, workers=-1)

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
    for f, p in zip(f_names, pixel_scales):
        if f == 'F444W':
            continue
        print(f'addpixscl {f}_PSF.fits {p}')
        print(f'pypher {f}_PSF.fits F444W_PSF.fits kernel_{f}_to_F444W.fits')

def convolution(sci_imgs, wht_imgs, sci_filenames, wht_filenames) -> None:
    # try:
    kernel_files = glob.glob(str(f_path / 'psf' / 'kernel_*_to_F444W.fits'))
    kernels = [fits.open(k)[0] for k in kernel_files]
    # kernels_double = kernels + kernels
    # sci_wht_imgs = np.concatenate([sci_imgs, wht_imgs])
    def convolve(image, kernel, filename) -> None:
        convolved_data = convolve_fft(image.data, kernel.data, allow_huge=True,
                                      nan_treatment='interpolate', preserve_nan=True)
        convolved_filename = f_path / 'convolved' / f'c_{filename}'
        fits.writeto(convolved_filename, convolved_data, header=image.header, overwrite=True)
        print(f'Convolved image saved to {convolved_filename}')
    skip_filters = ['f336wu', 'f435w', 'f606w', 'f606wu', 'f775w', 'f814w', 'f850lp', 'f277w', 'f335m', 'f356w', 'f410m', 'f460m', 'f480m', 'f105w' 'f444w']
    # for sci, wht, kernel, sci_f, wht_f in tqdm(zip(sci_imgs, wht_imgs, kernels, sci_filenames, wht_filenames), total=len(sci_imgs)):
    #     if any(filter in sci_f for filter in skip_filters):
    #         continue
    #     print(f'Convolving {sci_f} and {wht_f} with {kernel}')
    #     convolve(sci, kernel, sci_f)
    #     convolve(wht, kernel, wht_f)
    for sci, kernel, sci_f in tqdm(zip(sci_imgs, kernels, sci_filenames), total=len(sci_imgs)):
        if any(filter in sci_f for filter in skip_filters):
            continue
        print(f'Convolving {sci_f} with {kernel}')
        convolve(sci, kernel, sci_f)
    for wht, kernel, wht_f in tqdm(zip(wht_imgs, kernels, wht_filenames), total=len(wht_imgs)):
        if any(filter in wht_f for filter in skip_filters):
            continue
        print(f'Convolving {wht_f} with {kernel}')
        convolve(wht, kernel, wht_f)

    # except FileNotFoundError:
    #     print('No kernel files found. Run pypher_commands() to generate them.')


# Load the science image
# sci_image_filename = f_path / images / 'gds-grizli-v5.0-f105w_drz_sci.fits'
# sci_image_hdul = fits.open(sci_image_filename)
# sci_image_data = sci_image_hdul[0].data

# # Load the convolution kernel
# kernel_filename = f_path / 'psf' / 'kernel_F105W_to_F444W.fits'
# kernel_hdul = fits.open(kernel_filename)
# kernel_data = kernel_hdul[0].data

# convolved_data = convolve_fft(sci_image_data, kernel_data, allow_huge=True, nan_treatment='interpolate', preserve_nan=True)

# # # Save the convolved image to a new FITS file
# convolved_image_filename = 'convolved_gds-grizli-v5.0-f105w_drz_sci.fits'
# fits.writeto(f_path / convolved_image_filename, convolved_data, header=sci_image_hdul[0].header, overwrite=True)

# # Close the FITS files
# sci_image_hdul.close()
# kernel_hdul.close()

# print(f"Convolved image saved to {convolved_image_filename}")

def main():
    sci_filenames = open(f_path / f'names/{cat_name}_sci_filenames.txt', 'r').read().splitlines()
    wht_filenames = open(f_path / f'names/{cat_name}_wht_filenames.txt', 'r').read().splitlines()
    def open_imgs(filenames):
        return [fits.open(f_path / images / f)[0] for f in filenames]
    sci_imgs = open_imgs(sci_filenames)
    wht_imgs = open_imgs(wht_filenames)
    # pypher_commands(get_pixel_scale(sci_imgs))
    convolution(sci_imgs, wht_imgs, sci_filenames, wht_filenames)

if __name__ == '__main__':
    main()