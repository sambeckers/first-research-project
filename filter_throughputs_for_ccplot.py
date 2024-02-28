"""
filter_throughputs_for_ccplot
Created on 18-02-2024

@author(s): Sam Beckers


"""
from eazy import filters, templates
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
# Set plt font to LaTeX
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "Times New Roman",
    "font.sans-serif": "helvetica"
})
import numpy as np
import os
os.chdir('/Users/sam/FRESCO/Filter throughputs')

# Define the filters
filter_dict = {'F336WU': 'HST_WFC3_UVIS1.F336W.dat',
                'F435W': 'HST_ACS_WFC.F435W.dat',
                'F475W': 'HST_ACS_WFC.F475W.dat',
                'F606W': 'HST_ACS_WFC.F606W.dat',
                'F606WU': 'HST_WFC3_UVIS1.F606W.dat',
                'F775W': 'HST_ACS_WFC.F775W.dat',
                'F814W': 'HST_ACS_WFC.F814W.dat',
                'F814WU': 'HST_WFC3_UVIS1.F814W.dat',
                'F850LP': 'HST_WFC3_UVIS1.F850LP.dat',
                'F850LPU': 'HST_WFC3_UVIS1.F850LP.dat',
                'F105W': 'HST_WFC3_IR.F105W.dat',
                'F110W': 'HST_WFC3_IR.F110W.dat',
                'F125W': 'HST_WFC3_IR.F125W.dat',
                'F140W': 'HST_WFC3_IR.F140W.dat',
                'F160W': 'HST_WFC3_IR.F160W.dat',
                'F182M': 'JWST_NIRCam.F182M.dat',
                'F210M': 'JWST_NIRCam.F210M.dat',
                'F430M': 'JWST_NIRCam.F430M.dat',
                'F460M': 'JWST_NIRCam.F460M.dat',
                'F480M': 'JWST_NIRCam.F480M.dat',
                'F444W': 'JWST_NIRCam.F444W.dat',}

def define_eazy_filter(filter_path):
    """Define the filter transmission curve, compatible with eazy
    Args:
        filter_path (str): Path to the filter transmission curve (e.g. 'JWST_NIRCam.F182M.dat')

    Returns:
        eazy.filters.FilterDefinition: The filter definition
    """
    # Read in the filter transmission curves
    with open(filter_path, 'r') as filter_file:
        filter_data = filter_file.read().splitlines()
        wx = []
        wy = []
        for i in range(len(filter_data)):
            wx.append(float(filter_data[i].split()[0]))
            wy.append(float(filter_data[i].split()[1]))
    
    f = filters.FilterDefinition(wave=np.array(wx), throughput=np.array(wy))
    return f

def plot_filter(filter_path):
    """Plot the filter transmission curve
    Args:
        filter_path (str): Path to the filter transmission curve (e.g. 'JWST_NIRCam.F182M.dat')
        ax (matplotlib.axes._subplots.AxesSubplot): The axis to plot the filter on
        label (str): The label for the filter
        color (str): The color of the filter
    """
    f = define_eazy_filter(filter_path)
    plt.figure(dpi=450)
    plt.plot(f.wave, f.throughput,lw=2)

def plot_sed_and_filters(sed_path, filter_dict):
    """Plot SED and filter throughputs in the same figure
    Args:
        sed_path (str): Path to the SED file
        filter_dict (dict): Dictionary containing filter names and their corresponding transmission curve paths
    """
    # Read SED data
    sed_data = templates.Template(sed_path)
    print(sed_data.flux)
    # Plot SED
    plt.figure(dpi=450)
    plt.plot(sed_data.wave, sed_data.flux, label='SED', lw=2)

    # Plot Filters
    for filter_name, filter_path in filter_dict.items():
        plot_filter(filter_path, label=filter_name)

    # Set labels and legend
    plt.xlabel('Wavelength (Angstrom)')
    plt.ylabel('Flux Density')
    plt.legend()

    # Show plot
    plt.show()

plot_filter(filter_dict['F444W'])

SED = '/Users/sam/eazy-photoz/templates/spline_templates_v3/spline_age0.31_av1.0.fits'

plot_sed_and_filters(SED, filter_dict)