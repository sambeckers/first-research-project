import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord, ICRS
from astropy import units as u
from astropy.nddata import Cutout2D
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from paths_and_global_vars import *
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

def crop_at_UDF(image):
    # Load the FITS file
    # fits_file = f_path / images / 'gds-grizli-v7.2-f444w-clear_drc_sci.fits'
    hdulist = fits.open(f_path / images / image)
    hdu = hdulist[0]
    data = hdu.data
    wcs = WCS(hdu.header)

    # Define the center and size of the region to be cropped
    center_position = (data.shape[1] // 2, data.shape[0] // 2)  # center of the image
    size = (2500, 2500)  # size of the cutout (width, height)

    # Create the cutout - at UDF Coordinates (https://webbtelescope.org/contents/media/images/2022/015/01FY71QV5K57XMV95C90MNX3QB)
    cutout = Cutout2D(data, SkyCoord("03h 32m 39.99s", "-27° 48' 0.0", unit=(u.hourangle, u.degree)), size=size, wcs=wcs)

    # Plot the original image
    if 'f444w' in image and 'sci' in image:
        fig, ax = plt.subplots(1, 1, subplot_kw={'projection': wcs}, dpi=300)
        ax.imshow(data, origin='lower', cmap='grey', vmin=0, vmax=0.01*np.std(data))
        ax.set_xlabel('RA', fontsize=14)
        ax.set_ylabel('DEC',fontsize=14)

        # Add a red rectangle to indicate the region to be cropped
        rect = Rectangle((center_position[0] - size[0] // 2, center_position[1] - size[1] // 2), size[0], size[1],
                        edgecolor='red', facecolor='none', lw=3, label='Cutout')
    
        ax.add_patch(rect)
        ax.legend(loc='upper right', fontsize=12, facecolor='black', edgecolor='white')
        ax.set_title('F444W')
        plt.tight_layout()
        plt.show()
        fig.savefig(fig_path / 'f444w_cutout.pdf')

    # Create new header with original and updated WCS
    new_header = hdu.header.copy()
    new_header.update(cutout.wcs.to_header())

    # Save the cropped image
    cutout_hdu = fits.PrimaryHDU(data=cutout.data, header=new_header)
    cutout_hdulist = fits.HDUList([cutout_hdu])
    cutout_hdulist.writeto(f_path / 'cropped' / f'crop_{image}', overwrite=True)

def main():
    filenames_sci = open(f_path / f'names/{cat_name}_sci_filenames.txt', 'r').read().splitlines()
    filenames_wht = open(f_path / f'names/{cat_name}_wht_filenames.txt', 'r').read().splitlines()

    print('Cropping science images at UDF...')
    for filename in tqdm(filenames_sci, total=len(filenames_sci)):
        crop_at_UDF(filename)

    print('Cropping weight images at UDF...')
    for filename in tqdm(filenames_wht, total=len(filenames_wht)):
        crop_at_UDF(filename)

if __name__ == '__main__':
    main()