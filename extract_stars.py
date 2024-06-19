from matplotlib.lines import Line2D
from astropy.io import fits
from astropy import units as u
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord, ICRS
from astropy.nddata import Cutout2D
from astropy.nddata.utils import NoOverlapError
from astropy.stats import sigma_clip
import matplotlib.pyplot as plt
import numpy as np
import textwrap
from tqdm import tqdm

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

def stars_from_f444w_SE():
    cat = np.genfromtxt(f_path / cat_folder / f'{cat_name}_444w.cat', skip_header = 20,
                        names= ['id', 'f', 'e', 'x', 'y', 'ra', 'dec', 'flags', 'class_star'],
                        comments='#', usecols=(0, 1, 2, 11, 12, 13, 14, 15, 16))
    
    star = 0.8
    sel = (cat['class_star'] >= star) & (cat['flags'] <= 7) & (cat['f']/cat['e'] >= 5)
    cat = cat[sel]
    print(f'Number of stars: {len(cat)} using class_star >= {star}')
    return len(cat), cat['ra'], cat['dec'], cat['id']

def star_cutouts(cat_length, RA, DEC, ID, simbad=False) -> None:
    filenames = open(f_path / f'names/{cat_name}_sci_filenames.txt', 'r').read().splitlines()
    
    # Filter filenames to only include HST filters and JWST F444W
    filtered_filenames = [f for f in filenames if '5.0' in f or '444w' in f]
    filter_names = [f.split('-')[3].split('_')[0].upper() for f in filtered_filenames] # Extract filter names from filenames
    # Load the images
    imgs = [fits.open(f_path / images / f)[0] for f in filtered_filenames]  # save HDUList for each image

    # Subplot setup
    num_images = len(imgs) # Number of images
    num_cutouts = cat_length # Number of cutouts
    nrows, ncols = num_cutouts, num_images # Calculate the grid size for subplots (rows = num_cutouts, columns = num_images)
    fig, axs = plt.subplots(nrows, ncols, figsize=(2 * ncols, 2 * nrows), dpi=450)

    # Generate cutouts and plot them
    for i, (ra, dec, obj_id) in tqdm(enumerate(zip(RA, DEC, ID)), total=cat_length):
        for j, img in enumerate(imgs):
            try:
                if simbad:
                    cutout = Cutout2D(img.data, SkyCoord(ra, dec, unit=(u.hourangle, u.degree)), u.Quantity((7, 7), u.arcsec), wcs=WCS(img.header))
                else:
                    cutout = Cutout2D(img.data, SkyCoord(ra, dec, unit=(u.deg, u.deg)), u.Quantity((7, 7), u.arcsec), wcs=WCS(img.header))
            except NoOverlapError:
                print(f'No overlap for {obj_id} in {filter_names[j]}')
                continue

            # Determine the axis to plot on
            ax = axs[i, j]

            # Plot the cutout
            ax.imshow(cutout.data, origin='lower', cmap='plasma', vmin=0, vmax=1)
            ax.tick_params(left=False, right=False, top=False, bottom=False, labelleft=(j==0), labelbottom=False)
            
            # Set the side header with the catalog id
            if j == 0:
                wrapped_id = "\n".join(textwrap.wrap(str(obj_id), width=10)) # Wrap the id to fit the plot
                ax.set_ylabel(wrapped_id, fontsize=20, rotation=0, labelpad=70, va='center')
                ax.set_yticks([]) # Remove y-ticks

            # Set the top header with the filter name
            if i == 0:
                ax.set_title(filter_names[j], fontsize=30)

    # Adjust layout to ensure space for labels
    plt.subplots_adjust(wspace=0.05, hspace=0.05)
    plt.savefig(fig_path / f'{cat_name}_psf_star_cutouts_from_444w_SE.png', bbox_inches='tight')
    plt.show()

def main():
    # Load the SIMBAD catalog
    cat_sim = np.genfromtxt(f_path / cat_folder / 'FRESCO_simbad_stars.txt', delimiter='\t', names=True, dtype=None, encoding='utf-8')
    # star_cutouts(len(cat_sim), cat_sim['ra'], cat_sim['dec'], cat_sim['identifier'], sibmad=True)
    stars_from_f444w_SE()
    # star_cutouts(*stars_from_f444w_SE())

if __name__ == '__main__':
    main()

