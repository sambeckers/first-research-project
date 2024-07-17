from matplotlib.lines import Line2D
from astropy.io import fits
from astropy import units as u
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord, ICRS
from astropy.nddata import Cutout2D
from astropy.nddata.utils import NoOverlapError
from astropy.stats import SigmaClip
from photutils.psf import EPSFBuilder, EPSFStars, EPSFStar
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from astropy.visualization import simple_norm
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


def star_cutouts(cat_length, RA, DEC, ID, simbad=False, plot=True, HST_only=False, JWST_only=False):
    """Generate cutouts of stars from the a star catalog.

    Args:
        cat_length (int): Number of stars in the catalog
        RA (array): Right ascension of the stars in the catalog
        DEC (array): Declination of the stars in the catalog
        ID (array): ID of the stars in the catalog
        simbad (bool, optional): Whether the catalog is from SIMBAD. Defaults to False.
        plot (bool, optional): Whether to plot the cutouts. Defaults to True.

    Returns:
        EPSF_stars_per_filter (list): nested list of EPSF stars for each filter
        filter_names (list): List of filter names
    """
    filenames = open(f_path / f'names/{cat_name}_sci_filenames.txt', 'r').read().splitlines()
    
    # Filter filenames to only include HST filters and JWST F444W
    if HST_only:
        filtered_filenames = [f for f in filenames if '5.0' in f or '444w' in f]
    elif JWST_only:
        filtered_filenames = [f for f in filenames if '5.0' not in f]
    else:
        filtered_filenames = filenames
    
    filter_names = [f.split('-')[3].split('_')[0].upper() for f in filtered_filenames] # Extract filter names from filenames

    # Load the images
    imgs = [fits.open(f_path / images / f)[0] for f in filtered_filenames]  # save HDUList for each image

    # Subplot setup
    num_images = len(imgs) # Number of images
    num_cutouts = cat_length # Number of cutouts
    nrows, ncols = num_cutouts, num_images # Calculate the grid size for subplots (rows = num_cutouts, columns = num_images)
    if plot:
        fig, axs = plt.subplots(nrows, ncols, figsize=(2 * ncols, 2 * nrows), dpi=450)

    EPSF_stars_per_filter = [[] for _ in range(num_images)] # List to store EPSF stars
    print(f'Generating cutouts for {cat_length} stars...')
    # Generate cutouts and plot them
    for i, (ra, dec, obj_id) in tqdm(enumerate(zip(RA, DEC, ID)), total=cat_length):
        for j, img in enumerate(imgs):
            try:
                if simbad:
                    cutout = Cutout2D(img.data, SkyCoord(ra, dec, unit=(u.hourangle, u.degree)), u.Quantity((4, 4), u.arcsec), wcs=WCS(img.header)) # important! use hourangle for ra
                else:
                    cutout = Cutout2D(img.data, SkyCoord(ra, dec, unit=(u.deg, u.deg)), u.Quantity((4.04, 4.04), u.arcsec), wcs=WCS(img.header))
            except NoOverlapError:
                print(f'No overlap for {obj_id} in {filter_names[j]}')
                continue

            # Add EPSF star
            star = EPSFStar(cutout.data, 
                            cutout_center=cutout.center_cutout, origin = cutout.origin_original, 
                            wcs_large=WCS(img.header), id_label=obj_id)
            if star.flux >= 0.0 and np.all(np.isfinite(star._data_values)): # Only add stars with positive flux to EPSFStars list 
                EPSF_stars_per_filter[j].append(star)

            if plot:
                # Determine the axis to plot on
                ax = axs[i, j]

                # Plot the cutout
                # ax.imshow(cutout.data, origin='lower', cmap='plasma', vmin=-1*np.std(cutout.data), vmax=3*np.std(cutout.data))
                ax.imshow(cutout.data, origin='lower', cmap='plasma', vmin=0, vmax=1)
                ax.tick_params(left=False, right=False, top=False, bottom=False, labelleft=(j==0), labelbottom=False)
                
                # Set the side header with the catalog id
                if j == 0:
                    wrapped_id = "\n".join(textwrap.wrap(str(obj_id), width=10)) # Wrap the id to fit the plot # add str(i) + "|" + if you want to see the index
                    ax.set_ylabel(wrapped_id, fontsize=20, rotation=0, labelpad=70, va='center')
                    ax.set_yticks([]) # Remove y-ticks

                # Set the top header with the filter name
                if i == 0:
                    ax.set_title(filter_names[j], fontsize=30)
        
    if plot: 
        # Adjust layout to ensure space for labels
        plt.subplots_adjust(wspace=0.05, hspace=0.05)
        plt.savefig(fig_path / f'{cat_name}_psf_star_cutouts_selected_v7.jpg', bbox_inches='tight')
        plt.show()

    return EPSF_stars_per_filter, filter_names

def pad_to_even_shape(data):
    """Pad the data to have an even shape.

    Args:
        data (array): Data to pad

    Returns:
        array: Padded data
    """
    padded_data = data
    if data.shape[0] % 2 != 0:
        # Pad with one row of zeros at the bottom
        padded_data = np.pad(padded_data, ((0, 1), (0, 0)), mode='constant')
    if data.shape[1] % 2 != 0:
        # Pad with one column of zeros at the right
        padded_data = np.pad(padded_data, ((0, 0), (0, 1)), mode='constant')
    return padded_data

def custom_format(x, pos):
    """Custom format for colorbar tickers. 
    Scientific notation for values less than 1e-2 and greater than 1e4.

    Args:
        x (str): colorbar tickers

    Returns:
        str: formatted colorbar tickers
    """
    if x != 0 and (abs(x) < 1e-2 or abs(x) >= 1e4):
        return f'{x:.1e}'
    else:
        return f'{x:.1f}'

def build_psf(stars_per_filter, filter_names) -> None:
    """Build the Effective Point Spread Function (EPSF) for each filter.

    Args:
        stars_per_filter (list): nested list of EPSF stars for each filter
        filter_names (list): list of filter names
    """
    # Initialize the EPSFBuilder w/ custom settings
    epsf_builder = EPSFBuilder(oversampling=1, norm_radius=10, sigma_clip=SigmaClip(sigma=5.0, maxiters=10), smoothing_kernel='quadratic', maxiters=50, progress_bar=True)

    # Build the EPSF for each filter
    for s_list, f in zip(stars_per_filter, filter_names):
        stars = EPSFStars(s_list) # Create EPSFStars object
        epsf, fitted_stars = epsf_builder.build_epsf(stars) # Build the EPSF
        epsf_padded  = pad_to_even_shape(epsf.data) # Pad the EPSF to have an even shape (required by pypher)
        if s_list != stars_per_filter[-1]: # Save the EPSF to a fits file for all filters except F444W (already made it's PSF with webbpsf)
            hdu = fits.PrimaryHDU(data=epsf_padded.data)
            hdu.writeto(f_path / 'psf' / f'{f}_PSF.fits', overwrite=True)
            print(f'Saved {f} PSF to fits file')

        # Plot the EPSF (using photutils example code)
        norm = simple_norm(epsf.data, 'log', percent=99.0)
        plt.figure(dpi=450)
        plt.imshow(epsf.data, origin='lower', cmap='plasma', norm=norm)
        plt.colorbar(label='Fractional intensity per pixel', format=ticker.FuncFormatter(custom_format))
        plt.title(f'{f} EPSF')
        plt.savefig(fig_path / f'{f}_epsf.png', bbox_inches='tight')
        plt.show()

    # Example for one filter:
    # stars = EPSFStars(stars_per_filter[-2])
    # epsf, fitted_stars = epsf_builder.build_epsf(stars)

    # norm = simple_norm(epsf.data, 'log', percent=99.0)
    # plt.imshow(epsf.data, origin='lower', cmap='plasma', norm=norm)
    # plt.colorbar()
    # plt.show()

def main():
    excluded_sources = [3, 11, 13, 16, 17, 21, 24, 27, 28, 29, 31, 32, 33, 34, 35, 36, 39, 42, 43, 46, 47] # index of sources to exclude

    # # Load the SIMBAD catalog
    # cat = np.genfromtxt(f_path / cat_folder / 'FRESCO_simbad_stars.txt', delimiter='\t', names=True, dtype=None, encoding='utf-8')
    # cat_sim = np.delete(cat, excluded_sources) # Remove the excluded sources
    
    # spf, filters = star_cutouts(len(cat_sim), cat_sim['ra'], cat_sim['dec'], cat_sim['identifier'], simbad=True, plot=False, JWST_only=True)
    # build_psf(spf, filters)

    # Load the SE catalog
    # stars_from_f444w_SE()
    # star_cutouts(*stars_from_f444w_SE())

    # Andrea's v7 star catalog
    cat_v7 = np.genfromtxt(f_path / cat_folder / f'{cat_name}_imgv7.0_stars.cat', names=True, dtype=None, encoding='utf-8')
    spf, filters = star_cutouts(len(cat_v7), cat_v7['ra'], cat_v7['dec'], cat_v7['id'], simbad=False, plot=False, JWST_only=True)
    build_psf(spf, filters)

if __name__ == '__main__':
    main()
