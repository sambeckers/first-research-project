from matplotlib.lines import Line2D
from astropy.io import fits
from astropy import units as u
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord, ICRS
from astropy.nddata import Cutout2D
from astropy.stats import sigma_clip
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "Times New Roman",
    "font.sans-serif": "helvetica"
})
from paths_and_global_vars import *

cat = np.genfromtxt(f_path / cat_folder / 'FRESCO_simbad_stars.txt', delimiter='\t', names=True, dtype=None, encoding='utf-8')

# filenames = open(f_path / f'names/{cat_name}-sci-filenames_ordered_incl_f444w.txt', 'r').read().splitlines()
# images = [fits.open(f_path / images / f)[0] for f in filenames] # save hdul for each image

image  = fits.open(f_path / reprojected / 'gds-grizli-v5.1-f444w-clear_drc_sci.fits')[0]

for ra, dec in zip(cat['ra'], cat['dec']):
    cutout = Cutout2D(image.data, SkyCoord(ra, dec, unit=(u.hourangle, u.degree)), u.Quantity((4, 4), u.arcsec), wcs=WCS(image.header))
    plt.figure(dpi=450)
    plt.imshow(cutout.data, origin='lower', cmap='plasma', vmin=0, vmax=1)
    plt.show()
