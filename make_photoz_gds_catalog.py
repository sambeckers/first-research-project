"""
photoz_FRESCO
Created on 18-02-2024

@author(s): Sam Beckers

- Read in z_phot from eazy zout FITS file, 
- Read ID, ra, dec, fluxes and flux errors from the gds_catalog.cat file, 
- Combine these into a new catalog
"""

from astropy.io import fits
import numpy as np
import pandas as pd
import os
os.chdir('/Users/sam/FRESCO/')

# Read in filter names
cat_names = []
with open('catalog-names_incl_f444w.txt', 'r') as catalog_file:
    catalog_names = catalog_file.read().splitlines()
    for cat_name in catalog_names:
        cat_names.append(cat_name)
filters = [cat_name.split('_')[0][3:] for cat_name in cat_names]

# Read in the catalog including headers
cat = np.genfromtxt('catalogs/gds_catalog.cat', delimiter=' ', names=True, comments='#')
print(cat.dtype.names)

# Read in the eazy zout catalog FITS
zout = fits.open('eazy outputs/gds_photoz.eazypy.zout.fits')
z_phot = zout[1].data['z_phot']
z_phot_6 = z_phot[z_phot > 6] # Select sources with z_phot > 6

ID = cat['id'][z_phot>6].astype('int') # convert values to int

ra = cat['ALPHA_J2000_444w'][z_phot>6]
dec = cat['DELTA_J2000_444w'][z_phot>6]

flux = [[] for _ in range(len(filters))]
flux_err = [[] for _ in range(len(filters))]
for idx, filter in enumerate(filters):
    flux[idx] = cat[f'f_{filter}'][z_phot>6]
    flux_err[idx] = cat[f'e_{filter}'][z_phot>6]

# Create a DataFrame with the params for the selected sources
df = pd.DataFrame({
    'ID': ID,
    'z_phot': z_phot_6,
    'ra': ra,
    'dec': dec,
    **{f'f_{filter}': flux[idx] for idx, filter in enumerate(filters)},
    **{f'e_{filter}': flux_err[idx] for idx, filter in enumerate(filters)}
})

# Save DataFrame to a new .cat file
df.to_csv('gds_zphot_catalog.cat', sep=' ', index=False)
print('Catalog saved')
zout.close()