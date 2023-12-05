"""
reproject_FRESCO_to_f444w.py
Created on 16-11-23

@author(s): Sam Beckers

Reprojects all the images in the FRESCO catalogue to the detection image (F444W)
using adaptive reprojection with flux conservation.
"""
import os
os.chdir("/Users/sam/Library/Mobile Documents/com~apple~CloudDocs/Astronomy Data Science MSc 2324 Yr 1/FRP/FRESCO")

from astropy.io import fits
from reproject import reproject_adaptive

hdu_detect = fits.open("gds-grizli-v5.1-f444w-clear_drc_sci.fits")[0]

#test: reproject 182m onto 444w
# hdu_182m = fits.open("gds-grizli-v5.1-f182m-clear_drc_sci.fits")[0]
# reproj_182m, _ = reproject_adaptive(hdu_182m, hdu_detect.header, conserve_flux=True)
# fits.writeto('gds-grizli-v5.1-f182m-clear_drc_sci_reproj.fits', reproj_182m, hdu_detect.header, overwrite=True)

# Filter names (without the 'f' prefix)):
filter_NIRCam = ['182m', '210m', '430m', '460m', '480m'] #JWST, F444W is the detection image
filter_WFC3IR = ['105w', '110w', '125w', '140w', '160w'] #HST
filter_optical = ['336wu', '435w', '475w', '606w', '606wu', '775w', '814w', '814wu', '850lp', '850lpu'] #HST

# Reproject all the images onto the detection image:
for f in filter_NIRCam:
    hdu = fits.open("gds-grizli-v5.1-f{}-clear_drc_sci.fits".format(f))[0]
    reproj, _ = reproject_adaptive(hdu, hdu_detect.header, conserve_flux=True)
    fits.writeto('gds-grizli-v5.1-f{}-clear_drc_sci_reproj.fits'.format(f), reproj, hdu_detect.header, overwrite=True)
    print("Done with {}".format(f))

for f in filter_WFC3IR:
    hdu = fits.open("gds-grizli-v5.0-f{}_drz_sci.fits".format(f))[0]
    reproj, _ = reproject_adaptive(hdu, hdu_detect.header, conserve_flux=True)
    fits.writeto('gds-grizli-v5.0-f{}_drz_sci_reproj.fits'.format(f), reproj, hdu_detect.header, overwrite=True)
    print("Done with {}".format(f))

for f in filter_optical:
    hdu = fits.open("gds-grizli-v5.0-f{}_drc_sci.fits".format(f))[0]
    reproj, _ = reproject_adaptive(hdu, hdu_detect.header, conserve_flux=True)
    fits.writeto('gds-grizli-v5.0-f{}_drc_sci_reproj.fits'.format(f), reproj, hdu_detect.header, overwrite=True)
    print("Done with {}".format(f))
