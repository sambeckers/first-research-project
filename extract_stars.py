from matplotlib.lines import Line2D
from astropy.io import fits
from astropy import units as u
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord, ICRS
from astropy.nddata import Cutout2D
from astropy.stats import sigma_clip
import matplotlib.pyplot as plt
import numpy as np
import textwrap

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "Times New Roman",
    "font.sans-serif": "helvetica",
    "figure.facecolor": "black",
    "axes.facecolor": "black",
    "savefig.facecolor": "black",
    "text.color": "white",
    "axes.labelcolor": "white",
    "xtick.color": "white",
    "ytick.color": "white"
})
from paths_and_global_vars import *

# Load the catalog
cat = np.genfromtxt(f_path / cat_folder / 'FRESCO_simbad_stars.txt', delimiter='\t', names=True, dtype=None, encoding='utf-8')

# Load the filenames
filenames = open(f_path / f'names/{cat_name}_sci_filenames.txt', 'r').read().splitlines()

# Filter filenames
filtered_filenames = [f for f in filenames if '5.0' in f or '444w' in f]

# Extract filter names from filenames
filter_names = [f.split('-')[3].split('_')[0].upper() for f in filtered_filenames]

# Load the images
images = [fits.open(f_path / images / f)[0] for f in filtered_filenames]  # save HDUList for each image

# Number of images
num_images = len(images)

# Number of cutouts
num_cutouts = len(cat)

# Calculate the grid size for subplots (rows = num_cutouts, columns = num_images)
nrows = num_cutouts
ncols = num_images

# Prepare the plot
fig, axs = plt.subplots(nrows, ncols, figsize=(2 * ncols, 2 * nrows), dpi=450)

# Generate cutouts and plot them
for i, (ra, dec, obj_id) in enumerate(zip(cat['ra'], cat['dec'], cat['identifier'])):
    for j, img in enumerate(images):
        cutout = Cutout2D(img.data, SkyCoord(ra, dec, unit=(u.hourangle, u.degree)), u.Quantity((7, 7), u.arcsec), wcs=WCS(img.header))

        # Determine the axis to plot on
        ax = axs[i, j]

        # Plot the cutout
        ax.imshow(cutout.data, origin='lower', cmap='plasma', vmin=0, vmax=1)
        ax.tick_params(left=False, right=False, top=False, bottom=False, labelleft=(j==0), labelbottom=False)
        
        # Set the side header with the catalog id
        if j == 0:
            wrapped_id = "\n".join(textwrap.wrap(obj_id, width=10))
            ax.set_ylabel(wrapped_id, fontsize=20, rotation=0, labelpad=70, va='center')
            ax.set_yticks([])

        # Set the top header with the filter name
        if i == 0:
            ax.set_title(filter_names[j], fontsize=30)

# Adjust layout to ensure space for labels
plt.subplots_adjust(wspace=0.05, hspace=0.05)
plt.savefig(fig_path / f'{cat_name}_psf_star_cutouts_all.png', bbox_inches='tight')
plt.show()
