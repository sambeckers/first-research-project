from paths_and_global_vars import *
from convolve_to_f444w_psf import get_pixel_scale
import glob
import numpy as np
from poppy import display_ee
import poppy
import matplotlib.pyplot as plt
plt.rcParams.update({
    "text.usetex": False, # display_ee doesn't work with LaTeX
    "font.family": "Times New Roman",
    "font.sans-serif": "helvetica"
})
plt.rc('font', size=14)
from astropy.io import fits
from tqdm import tqdm

# psf = glob.glob(str(f_path / 'psf' / '*_PSF.fits'))
psf = [f_path / 'psf' / f'{i}_PSF.fits' for i in f_names]

sci_filenames = open(f_path / f'names/{cat_name}_sci_filenames.txt', 'r').read().splitlines()
sci_imgs  = [fits.open(f_path / reprojected / f'reproj_crop_{f}')[0] for f in sci_filenames]
pixelscl = get_pixel_scale(sci_imgs)

for p, ps, f in tqdm(zip(psf, pixelscl, f_names), total=len(psf)):
    hdul = fits.open(p, mode='update')
    try:
        fig, ax = plt.subplots(1, 1, dpi=450)
        display_ee(hdul, ax=ax, overplot=False)
        ax.axvline(ps, color='black', linestyle='--', label='Pixel scale', lw=1, alpha=0.8)
        plt.gca().get_lines()[0].set_color("red")
        ax.set_ylim(np.min(ax.lines[0].get_ydata())) # Set the y-axis limits to the minimum value of the encircled energy
        ax.set_xlabel('Radius [arcsec]', fontsize=14)
        ax.set_ylabel('Encircled Energy',fontsize=14)
        ax.legend(loc='lower right')
        ax.set_title(f)
        plt.savefig(fig_path / 'psf' / 'encircled_energy' / f'{f}_EE.pdf')
    except KeyError:
        print('aaaa')
        header = hdul[0].header
        header['PIXELSCL'] =  ps
        hdul.close()


    # plt.close('all')