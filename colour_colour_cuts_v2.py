"""
colour_colour_cuts_v2
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
import warnings
warnings.filterwarnings("ignore")

# Define the filter file names
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

def get_filters():
    """Prompt the user to enter the filters they want to plot 
    and return the filter transmission curves

    Returns:
        eazy.filters.FilterDefinition: The filter transmission curve for the x-axis
        eazy.filters.FilterDefinition: The filter transmission curve for both x and y axis
        eazy.filters.FilterDefinition: The filter transmission curve for the y-axis
        list: The names of the filters
    """
    print('The available filters are:\n', list(filter_dict.keys()))
    # cc_input = input('Enter the colours you want to plot (e.g. "F210M - F444W vs F182M - F210M"):')
    cc_input = 'F182M - F210M vs F814W - F182M'

    f_name_list = []
    for idx, i in enumerate([0, 2, 4, 6]):
        f_name = cc_input.split(' ')[i]
        f_name_list.append(f_name)
        if f_name not in list(filter_dict.keys()):
            print(f'Filter {f_name} not recognised')
            return
    fxy = define_eazy_filter(filter_dict[f_name_list[0]])
    fx = define_eazy_filter(filter_dict[f_name_list[1]])
    fy = define_eazy_filter(filter_dict[f_name_list[2]])
    return fx, fxy, fy, f_name_list

f_x, f_xy, f_y, f_names = get_filters()

def compute_sed_color(sed, filter_x, filter_xy, filter_y, z_arr):
    """Compute the colors of the SED at different redshifts

    Args:
        sed (eazy.templates.Template): the Spectral Energy Distribution
        filter_x (eazy.filters.FilterDefinition): the filter transmission curve for the x-axis
        filter_xy (eazy.filters.FilterDefinition): the filter transmission curve for both x and y axis
        filter_y (eazy.filters.FilterDefinition): the filter transmission curve for the y-axis
        z_arr (np.array): Array of redshifts

    Returns:
        x (list): List of x-axis colors (e.g. F210M - F444W)
        y (list): List of y-axis colors (e.g. F182M - F210M)
    """
    x, y = [], []
    for z in z_arr:
        x.append(-2.5*np.log10(sed.integrate_filter(filter_xy, z=z, include_igm = True, redshift_type = 'interp')/sed.integrate_filter(filter_x, z=z, include_igm = True, redshift_type = 'interp')))
        y.append(-2.5*np.log10(sed.integrate_filter(filter_y, z=z, include_igm = True, redshift_type = 'interp')/sed.integrate_filter(filter_xy, z=z, include_igm = True, redshift_type = 'interp')))
    return x,y

def plot_tracks():
    """
    Plot the SED colors at different redshifts for a set of templates
    """
    zarr = np.arange(0, 12, 0.5)
    os.chdir('/Users/sam/eazy-photoz')
    template_list = templates.read_templates_file('templates/sfhz/corr_sfhz_13.param')
    for temp in template_list:
        # if temp == template_list[0]:
        AV, SFR = temp.meta['AV'], temp.meta['SFR'] # get the absorption coefficient and SFR values from the template header
        x, y = compute_sed_color(temp, f_x, f_xy, f_y, zarr)
        plt.plot(x, y, '--', alpha=0.5, markersize=0.5, label=f'{AV}, {SFR:.2e}')

def plot_source_color():
    """
    Plot the colors of sources in the catalog
    """
    cat_zphot = np.genfromtxt('/Users/sam/FRESCO/Catalogs_v2/gds_zphot_catalog_filtered_carnall.cat', delimiter=' ', names=True, comments='#')
    F_x_F_xy_F_y = []
    for f_name in [f_names[1], f_names[0], f_names[2]]:
        filter_list = [filter_name[1:].lower() for filter_name in filter_dict.keys()]
        index = np.flatnonzero(np.core.defchararray.find(list(filter_dict.keys()),f_name)!=-1)[0]
        F_x_F_xy_F_y.append(cat_zphot[f'f_{filter_list[index]}'])
    x = -2.5*np.log10(F_x_F_xy_F_y[1]/F_x_F_xy_F_y[0])
    y = -2.5*np.log10(F_x_F_xy_F_y[2]/F_x_F_xy_F_y[1])
    plt.scatter(x, y, c='r')

def colour_colour_plot():
    """
    Plot the colour-colour diagram
    """
    plt.figure(dpi=450)
    plot_tracks()
    plot_source_color()
    plt.xlim(-.5,2)
    plt.ylim(-1,12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title=r'$\alpha_{\nu} [\rm{cm}^{-1}]$, SFR [M$_\odot$ yr$^{{-1}}$]', title_fontsize=12, fontsize=12)
    # Axes settings
    plt.gca().xaxis.set_minor_locator(AutoMinorLocator()) # set minor ticks
    plt.gca().yaxis.set_minor_locator(AutoMinorLocator())
    plt.tick_params(which='both', right='true', top='true', direction='in', labelsize=12, width=0.7)
    plt.tick_params(which='major', length=6)
    plt.tick_params(which='minor', length=3)     
    plt.xlabel(f_names[0]+r'$-$'+f_names[1], fontsize=14)
    plt.ylabel(f_names[2]+r'$-$'+f_names[3], fontsize=14)
    plt.gca().set_box_aspect(1) # set square (equal) aspect ratio without changing data limits
    plt.savefig('/Users/sam/Documents/GitHub/FRP/Figures/colour_colour_plot_v3.pdf', bbox_inches = 'tight')
    plt.show()

def main():
    colour_colour_plot()
main()