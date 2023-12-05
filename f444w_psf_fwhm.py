"""
f444w_psf_fwhm.py
Created on 16-11-23

@author(s): Sam Beckers

Simulates the PSF of the F444W filter and measures the FWHM of the PSF using WebbPSF.
"""
import os
os.environ['WEBBPSF_PATH'] = '/Users/sam/Library/Mobile Documents/com~apple~CloudDocs/Astronomy Data Science MSc 2324 Yr 1/FRP/webbpsf-data'
from webbpsf import NIRCam, measure_fwhm, display_psf
import matplotlib.pyplot as plt

nc = NIRCam()
nc.filter = 'F444W'
psf = nc.calc_psf()

display_psf(psf, ext=1, title='F444W PSF (Simulated)')
fwhm = measure_fwhm(psf)
print('FWHM = {} arcsec'.format(fwhm))

os.chdir('Library/Mobile Documents/com~apple~CloudDocs/Astronomy Data Science MSc 2324 Yr 1/FRP/FRESCO')
psf.writeto('default.psf', overwrite=True)

os.chdir('/Users/sam/Documents/GitHub/FRP/Figures')
plt.savefig('f444w_psf.pdf', dpi=300)
