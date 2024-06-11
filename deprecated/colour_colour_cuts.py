"""
colour_colour_cuts
Created on 18-02-2024

@author(s): Sam Beckers

Make colour-colour cuts and plot them for a given SED, colors and redshift range.
User is prompted to enter the colours they want to plot, from which the filter transmission curves are defined.
The SED is redshifted and integrated through the filters to compute the magnitudes.
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
    os.chdir('/Users/sam/FRESCO/Filter throughputs')
    with open(filter_path, 'r') as filter_file:
        filter_data = filter_file.read().splitlines()
        wx = []
        wy = []
        for i in range(len(filter_data)):
            wx.append(float(filter_data[i].split()[0]))
            wy.append(float(filter_data[i].split()[1]))
    
    f = filters.FilterDefinition(wave=np.array(wx), throughput=np.array(wy))
    return f

def compute_mags(SED, filter, z):
    """Redshift the filter wavelengths, integrate the SED through the filter and compute the magnitude
    Args:
        SED (str): Path to the SED file
        filter (eazy.filters.FilterDefinition): The filter definition
        z (np.array): Array of redshifts

    Returns:
        list: List of magnitudes
    """
    mag_list = []
    for z in z_arr:
        filter_throughput_z = filters.FilterDefinition(wave=filter.wave, throughput=filter.throughput)
        f_lambda = SED.integrate_filter(filter_throughput_z, z=z, include_igm=True, redshift_type='interp')
        mag = -2.5*np.log10(f_lambda)
        mag_list.append(mag)
    return mag_list

def source_mags(filter):
    cat_zphot = np.genfromtxt('/Users/sam/FRESCO/Catalogs_v2/gds_zphot_catalog_filtered1.cat', delimiter=' ', names=True, comments='#')
    filter_list = [filter_name[1:].lower() for filter_name in filter_dict.keys()]
    # print(cat_zphot[f'MAG_APER_{filter_list[20]}'])
    index = np.flatnonzero(np.core.defchararray.find(list(filter_dict.keys()),filter)!=-1)[0]
    flux = cat_zphot[f'f_{filter_list[index]}']
    return -2.5*np.log10(flux)

def make_colour_plot(template, z, include_sources=False):
    """Make a colour-colour plot of an SED at different redshifts

    Args:
        template (str): Path to the SED file (e.g. 'templates/spline_templates_v3/spline_age0.31_av1.0.fits'
        z (np.array): Array of redshifts (e.g. np.arange(6, 20, 0.1)
    """
    # Define the filters

    # Compute the magnitudes
    f_name_list = []
    m_list = [[] for _ in range(4)]
    m_source_list = [[] for _ in range(4)]
    for idx, i in enumerate([0, 2, 4, 6]):
        f_name = cc_input.split(' ')[i]
        f_name_list.append(f_name)
        if f_name not in list(filter_dict.keys()):
            print(f'Filter {f_name} not recognised')
            return
        f = define_eazy_filter(filter_dict[f_name])
        m = compute_mags(template, f, z)
        m_list[idx] = m
        m_source = source_mags(f_name)
        m_source_list[idx] = m_source

    # Plot the colours
    x_list = [m_list[0][i]-m_list[1][i] for i in range(len(m_list[0]))]
    y_list = [m_list[2][i]-m_list[3][i] for i in range(len(m_list[0]))]
    plt.plot(x_list, y_list, c='k', ls='dotted', lw=1, alpha=0.8)

    # Plot the source magnitudes
    if include_sources:
        x_list_source = [m_source_list[0][i]-m_source_list[1][i] for i in range(len(m_source_list[0]))]
        y_list_source = [m_source_list[2][i]-m_source_list[3][i] for i in range(len(m_source_list[0]))]
        plt.scatter(x_list_source, y_list_source, c='r', s=5)

    # Plot the redshift markers
    z_show = z[::5] # only show every 5th redshift
    z_show_idx = [np.argmin(np.abs(z - z_s)) for z_s in z_show]
    y_list_z = [y_list[i] for i in z_show_idx]
    x_list_z = [x_list[i] for i in z_show_idx]
    plt.scatter(x_list_z, y_list_z, c='blue', s=5)
    z_annotate = [0, 3, 6.0, 9.0, 12.0, 15.0]
    z_annotate_idx = [np.argmin(np.abs(z - z_s)) for z_s in z_annotate]
    y_list_z = [y_list[i] for i in z_annotate_idx]
    x_list_z = [x_list[i] for i in z_annotate_idx]
    for i, txt in enumerate(z_annotate):
        plt.annotate(str(txt), (x_list_z[i]+0.02, y_list_z[i]), textcoords="offset points", ha='left', fontsize=8, color='b', 
                     bbox=dict(facecolor='white', edgecolor='none', pad=0.25), fontweight='bold')

    # Axes settings
    plt.gca().xaxis.set_minor_locator(AutoMinorLocator()) # set minor ticks
    plt.gca().yaxis.set_minor_locator(AutoMinorLocator())
    plt.tick_params(which='both', right='true', top='true', direction='in', labelsize=12, width=0.7)
    plt.tick_params(which='major', length=6)
    plt.tick_params(which='minor', length=3)     
    plt.axis('square') # force the plot to be square
    plt.xlabel(f_name_list[0]+r'$-$'+f_name_list[1], fontsize=14)
    plt.ylabel(f_name_list[2]+r'$-$'+f_name_list[3], fontsize=14)
    plt.savefig('/Users/sam/Documents/GitHub/FRP/Figures/colour_colour_plot_v2.pdf', bbox_inches = 'tight')
    plt.show()

z_arr = np.arange(0, 15, 0.1)

os.chdir('/Users/sam/eazy-photoz')
template_list = templates.read_templates_file('templates/sfhz/carnall_sfhz_13.param')
# print(template_list[0].zindex())
# for temp in template_list:
#     print(temp)
#     make_colour_plot(temp, z_arr, include_sources=True)

make_colour_plot(template_list[0], z_arr, include_sources=True)