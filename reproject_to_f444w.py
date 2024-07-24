import os
from astropy.io import fits
from reproject import reproject_adaptive
from pathlib import Path
from paths_and_global_vars import *
from tqdm import tqdm

def reproject(image, sci=False, wht=False):
    if sci: 
        hdu_detect = fits.open(f_path / cropped / 'crop_gds-grizli-v7.2-f444w-clear_drc_sci.fits')[0]
    if wht:
        hdu_detect = fits.open(f_path / cropped / 'crop_gds-grizli-v7.2-f444w-clear_drc_wht.fits')[0]
    reproj, _ = reproject_adaptive(fits.open(f_path / cropped / image)[0], hdu_detect.header, conserve_flux=True)
    fits.writeto(f_path / reprojected / f'reproj_{image}', reproj, hdu_detect.header, overwrite=True)

def main():
    filenames_sci = open(f_path / f'names/{cat_name}_sci_filenames.txt', 'r').read().splitlines()
    filenames_wht = open(f_path / f'names/{cat_name}_wht_filenames.txt', 'r').read().splitlines()

    # print('Cropping science images at UDF...')
    for filename in tqdm(filenames_sci, total=len(filenames_sci)):
        if 'f444w' in filename:
            continue
        reproject(f'crop_{filename}', sci=True)

    # print('Cropping weight images at UDF...')
    for filename in tqdm(filenames_wht, total=len(filenames_wht)):
        if 'f444w' in filename:
            continue
        reproject(f'crop_{filename}', wht=True)

if __name__ == '__main__':
    main()