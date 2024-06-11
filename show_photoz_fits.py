"""
show_photoz_fits
Created on 01-06-2024

@author(s): Sam Beckers

This script is used to show the fits for all objects in the catalog. The fits are shown in the Eazy photoz plot, with the cutouts of the images above the plot. 
The fits are saved as pdf files in the specified folder.
"""

import os
from pathlib import Path
import matplotlib.pyplot as plt
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "Times New Roman",
    "font.sans-serif": "helvetica"
})
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from astropy.io import fits
from astropy import units as u
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
from astropy.nddata import Cutout2D
from matplotlib.gridspec import GridSpec
from tqdm import tqdm
import eazy
import eazy.hdf5
from paths_and_global_vars import *
os.chdir('/Users/sam/eazy-photoz') 

def open_cats(cat_file):
    """Opens eazy photoz hdf5 file, catalog file and zout fits file.

    Returns:
        self (eazy.photoz.PhotoZ) : Eazy photoz object
        cat (np.array) : Catalog file
        id (np.array) : ID column from zout fits file
        nusefilt (np.array) : number of used filters whilst fitting, from zout fits file
        images (list) : List of fits images from all filters
    """
    self = eazy.hdf5.initialize_from_hdf5(f_path / eazy_folder / f'{cat_name}_photoz.eazypy.h5', verbose=False)

    cat = np.genfromtxt(f_path / cat_folder / cat_file, delimiter=' ', names=True, comments='#')

    zout = fits.open(f_path / eazy_folder / f'{cat_name}_photoz.eazypy.zout.fits')
    id = zout[1].data['id']
    nusefilt = zout[1].data['nusefilt']

    filenames = open(f_path / 'gds-sci-filenames_ordered_incl_f444w.txt', 'r').read().splitlines()
    images = [fits.open(f_path / f)[0] for f in filenames] # save hdul for each image
    
    return self, cat, id, nusefilt, images

def show_cat_fits(self, cat, id, nusefilt, images, f_names):
    """Show fits for all objects in the catalog.

    Args:
        self (eazy.photoz.PhotoZ) : Eazy photoz object
        cat (np.array) : Catalog file
        id (np.array) : ID column from zout fits file
        nusefilt (np.array) : number of used filters whilst fitting, from zout fits file
        images (list) : List of fits images from all filters
        f_names (list) : List of filter names
        cc (bool, optional) : If True, only show fits for objects with z > 6 (for colour-cut selection). Defaults to False.
    """
    id_z_6 = []
    for idx, (ID, RA, DEC) in tqdm(enumerate(zip(cat['ID'], cat['ra'], cat['dec'])), total=len(cat['ID'])):
        # Get the redshift from the zbest column
        ix = self.idx[self.OBJID == ID][0]
        z = self.zbest[ix]
        if cc:
            if z < 6.0:
                continue # Skip objects with z < 6
        with plt.ioff():
            # print(z)
            fig, dir = self.show_fit(float(ID), template_color='red', logpz=False, add_label=False) # show_fit method from eazy.photoz.PhotoZ

            # Calculate the reduced chi^2
            zout_idx = np.where(id == ID)[0][0]
            nusefilt_id = nusefilt[zout_idx]
            reduced_chi2 = dir['chi2'] / nusefilt_id

            # Manipulate the show_fit plot
            fig.set_dpi(450)
            fig.get_axes()[0].set_ylabel(r'$f_{\lambda}$ [$10^{-19}$ erg s$^{-1}$ cm$^{-2}$]', fontsize=12)
            fig.get_axes()[0].set_xlabel(r'$\lambda_{\mathrm{obs}}$', fontsize=12)
            fig.get_axes()[1].set_xlabel(r'$z$', fontsize=12)
            fig.get_axes()[1].set_ylabel(r'$p(z)$', fontsize=12)
            fig.get_axes()[0].legend(handles=[Line2D([0], [0], ls='-', color='red', label=fr'$z$={z:.2f}', markerfacecolor='red'),
                                                Line2D([0], [0], marker=None, color='w', label=fr'ID={ID}'),
                                                Line2D([0], [0], marker=None, color='w', label=fr"$\chi^2$={reduced_chi2:.2f}")], loc='upper left', fontsize=12)
            pos0 = fig.get_axes()[0].get_position()
            pos1 = fig.get_axes()[1].get_position()

            # Save non-empty cutouts of images to a list
            non_empty_images = []
            non_empty_names = []
            for image, name in zip(images, f_names):
                cutout = Cutout2D(image.data, SkyCoord(ra=RA*u.degree, dec=DEC*u.degree), u.Quantity((4, 4), u.arcsec), wcs=WCS(image.header))
                if not np.all(cutout.data == 0):
                    non_empty_images.append(cutout)
                    non_empty_names.append(name)
            
            # Dynamic grid sizing based on number of non-empty images
            n_images = len(non_empty_images)
            if max(nusefilt) > 18:
                n_cols = 7
            else:
                n_cols = 6
            n_rows = (n_images + n_cols - 1) // n_cols

            # Plot the cutouts above the show_fit plot
            gs = GridSpec(n_rows, n_cols, figure=fig, wspace=0)
            for i, (cutout, name) in enumerate(zip(non_empty_images, non_empty_names)):
                ax = fig.add_subplot(gs[i // n_cols, i % n_cols])
                ax.imshow(cutout.data, origin='lower', cmap='hot', vmin=0, vmax=3*np.std(cutout.data))
                ax.set_title(name, fontsize=12, y=0.95)
                ax.axis('off')

                # Add crosshairs to the cutouts
                center_x, center_y = cutout.shape[1] / 2, cutout.shape[0] / 2
                length = min(cutout.shape) / 6
                gap = length * 0.6
                ax.plot([center_x - length, center_x - gap], [center_y, center_y], color='white', lw=1)  # Left horizontal line
                ax.plot([center_x + gap, center_x + length], [center_y, center_y], color='white', lw=1)  # Right horizontal line
                ax.plot([center_x, center_x], [center_y - length, center_y - gap], color='white', lw=1)  # Bottom vertical line
                ax.plot([center_x, center_x], [center_y + gap, center_y + length], color='white', lw=1)  # Top vertical line
            
            fig.subplots_adjust(bottom=pos0.y1 + 0.05, top=pos0.y1 + 0.9, left=pos0.x0 - 0.1, right=pos1.x1)
            plt.savefig(fig_fits_path / f'gds_photoz_fit_{str(ID)}.pdf', dpi=450, bbox_inches='tight')
            id_z_6.append(ID)
    pd.DataFrame({'ID (z>6)':id_z_6}).to_csv(fig_fits_path / 'id_z_6.cat', index=False)

def main():
    global cc
    cc = True
    if cc:
        fig_fits_path = fig_path / 'colour_colour_fits/'
        show_cat_fits(*open_cats(f'{cat_name}_catalog_colourcut_sel_formatted.cat'), f_names)
    else:
        fig_fits_path = fig_path / 'eazy_fits/'
        show_cat_fits(*open_cats(f'{cat_name}_zphot_catalog_filtered.cat'), f_names)

if __name__ == '__main__':
    main()

                                          