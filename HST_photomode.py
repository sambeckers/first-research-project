"""
HST_photmode
Created on 18-02-2024

@author(s): Sam Beckers

- This script reads the PHOTMODE keyword from the header of a FITS file and prints the value.
Used to verify which filters were assigned to which camera
- It also defines filter transmission curves for EAZY
"""
import os
from astropy.io import fits
import numpy as np

def read_photmode_from_fits(filename):
    # Open the FITS file
    with fits.open(filename) as hdulist:
        # Access the header of the primary HDU (usually index 0)
        header = hdulist[0].header
        
        # Check if 'PHOTMODE' keyword is present in the header
        if 'PHOTMODE' in header:
            photmode_value = header['PHOTMODE']
            return photmode_value
        else:
            print(f"PHOTMODE keyword not found in the header of {filename}.")
            return None

folder_path = '/Users/sam/FRESCO/original FITS files'

# List all FITS files in the folder
fits_files = [f for f in os.listdir('/Users/sam/FRESCO/original FITS files') if f.endswith('sci.fits')]

# Loop through each FITS file and read PHOTMODE
for fits_filename in fits_files:
    full_path = os.path.join(folder_path, fits_filename)
    photmode_value = read_photmode_from_fits(full_path)

    if photmode_value:
        print(f"{fits_filename}: PHOTMODE value - {photmode_value}")
        
from eazy import filters

def define_eazy_filter(filter_path):
    # Read in the filter transmission curves
    with open(filter_path, 'r') as filter_file:
        filter_data = filter_file.read().splitlines()
        wx = []
        wy = []
        for i in range(len(filter_data)):
            wx.append(float(filter_data[i].split()[0]))
            wy.append(float(filter_data[i].split()[1]))
    
    f1 = filters.FilterDefinition(wave=np.array(wx), throughput=np.array(wy), name='hst/wfc3/UVIS/F850LP')
    return f1.for_filter_file()

f850lpu = define_eazy_filter('/Users/sam/FRESCO/Filter throughputs/HST_WFC3_UVIS1.F850LP.dat')
# print(f850lpu)

