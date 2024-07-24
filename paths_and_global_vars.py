"""
paths_and_global_vars
Created on 11-06-2024

@author(s): Sam Beckers
"""
import os
from pathlib import Path

# File handling
f_path = Path('/Users/sam/FRESCO/') # Path to the FRESCO directory
fig_path = Path('/Users/sam/Documents/GitHub/FRP/Figures/')
images = 'gds_FRESCO'
cropped = 'cropped'
reprojected = 'reprojected'
eazy_path = Path('/Users/sam/eazy-photoz/')
cat_folder = 'catalogs_v3'
eazy_folder = 'eazy outputs'
cat_filter_names = 'names/cat_names_incl_f444w.txt'
cat_name = 'gds'

# Filters
# f_names = ['F336WU', 'F435W', 'F475W', 'F606W', 'F606WU', 'F775W', 'F814W', 'F814WU', 'F850LP', 'F850LPU', 
#            'F105W', 'F110W', 'F125W', 'F140W', 'F160W', 'F182M', 'F210M', 'F430M', 'F460M', 'F480M', 'F444W']
f_names = ['F336WU', 'F435W', 'F606W', 'F606WU', 'F775W', 'F814W', 'F850LP', 
           'F090W', 'F105W', 'F115W', 'F150W', 'F182M', 'F200W', 'F210M', 'F277W', 'F335M', 'F356W', 'F410M', 'F430M', 'F444W']
nircam_names = ['F090W', 'F115W', 'F150W', 'F182M', 'F200W', 'F210M', 'F277W', 'F335M', 'F356W', 'F410M', 'F430M','F444W']

filter_dict = {
    'F336WU': 'HST_WFC3_UVIS1.F336W.dat',
    'F435W': 'HST_ACS_WFC.F435W.dat',
    'F606W': 'HST_ACS_WFC.F606W.dat',
    'F606WU': 'HST_WFC3_UVIS1.F606W.dat',
    'F775W': 'HST_ACS_WFC.F775W.dat',
    'F814W': 'HST_ACS_WFC.F814W.dat',
    'F850LP': 'HST_ACS_WFC.F850LP.dat',
    'F090W': 'JWST_NIRCam.F090W.dat',
    'F105W': 'HST_WFC3_IR.F105W.dat',
    'F115W': 'JWST_NIRCam.F115W.dat',
    'F150W': 'JWST_NIRCam.F150W.dat',
    'F182M': 'JWST_NIRCam.F182M.dat',
    'F200W': 'JWST_NIRCam.F200W.dat',
    'F210M': 'JWST_NIRCam.F210M.dat',
    'F277W': 'JWST_NIRCam.F277W.dat',
    'F335M': 'JWST_NIRCam.F335M.dat',
    'F356W': 'JWST_NIRCam.F356W.dat',
    'F410M': 'JWST_NIRCam.F410M.dat',
    'F430M': 'JWST_NIRCam.F430M.dat',
    'F444W': 'JWST_NIRCam.F444W.dat'
}