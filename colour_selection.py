"""
colour_colour_cuts_v2
Created on 18-02-2024

@author(s): Sam Beckers

Make colour-colour cuts and plot them for a set of SEDs, colors and a redshift range.
The SED is redshifted and integrated through the filters to compute the magnitudes.
"""
from eazy import filters, templates
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import AutoMinorLocator
# Set plt font to LaTeX
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "Times New Roman",
    "font.sans-serif": "helvetica"
})
import numpy as np
from pathlib import Path
import os
import warnings
warnings.filterwarnings("ignore")
from paths_and_global_vars import *

def define_eazy_filter(filter_path):
    """Define the filter transmission curve, compatible with eazy
    Args:
        filter_path (str): Path to the filter transmission curve (e.g. 'JWST_NIRCam.F182M.dat')

    Returns:
        eazy.filters.FilterDefinition: The filter definition
    """
    # Read in the filter transmission curves
    f_path = Path('/Users/sam/FRESCO/') # Path to the FRESCO directory
    os.chdir(f_path / 'filter_throughputs')
    with open(filter_path, 'r') as filter_file:
        filter_data = filter_file.read().splitlines()
        wx = []
        wy = []
        for i in range(len(filter_data)):
            wx.append(float(filter_data[i].split()[0]))
            wy.append(float(filter_data[i].split()[1]))
    
    f = filters.FilterDefinition(wave=np.array(wx), throughput=np.array(wy))
    return f

def get_filters(filters=None):
    """Prompt the user to enter the filters they want to plot 
    and return the filter transmission curves

    Returns:
        eazy.filters.FilterDefinition: The filter transmission curve for the x-axis
        eazy.filters.FilterDefinition: The filter transmission curve for both x and y axis
        eazy.filters.FilterDefinition: The filter transmission curve for the y-axis
        list: The names of the filters
    """
    # print('The available filters are:\n', list(filter_dict.keys()))
    # cc_input = input('Enter the colours you want to plot (e.g. "F210M - F444W vs F182M - F210M"):')
    if filters == None:
        cc_input = 'F182M - F210M vs F814W - F182M'
    else:
        cc_input = filters

    fnamelist = []
    for idx, i in enumerate([0, 2, 4, 6]):
        f_name = cc_input.split(' ')[i]
        fnamelist.append(f_name)
        if f_name not in list(filter_dict.keys()):
            print(f'Filter {f_name} not recognised')
            return
    fxy = define_eazy_filter(filter_dict[fnamelist[0]])
    fx = define_eazy_filter(filter_dict[fnamelist[1]])
    fy = define_eazy_filter(filter_dict[fnamelist[2]])
    return fx, fxy, fy, fnamelist

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

def plot_tracks(sfhz=False, spline=False, plot=True):
    """
    Plot the SED colors at different redshifts for a set of templates
    """
    zarr = np.arange(0, 12, 1)
    os.chdir(eazy_path)
    if sfhz:
        template_list = templates.read_templates_file('templates/sfhz/corr_sfhz_13.param')
    if spline:
        template_list = templates.read_templates_file('templates/spline_templates_v3/c2020_spline.param')
    colors = [plt.cm.copper(i/len(template_list)) for i in range(len(template_list))]
    x_sel, y_sel = [], []
    for temp, color in zip(template_list, reversed(colors)):
        AV, SFR = temp.meta['AV'], temp.meta['SFR']
        x, y = compute_sed_color(temp, f_x, f_xy, f_y, zarr)
        if plot:
            plt.plot(x, y, '--', lw=1, markersize=0.5, label=f'{AV}, {SFR:.2e}', c=color, zorder=1, alpha=0.7)
        for idx, z in enumerate(zarr):
            if z>=z_selection:
                if plot: 
                    plt.scatter(x[idx], y[idx], marker='o', c='b', s=1, zorder=1)
                    if z in [6, 7, 8, 10, 12]:
                        plt.annotate(f'{z}', (x[idx]+0.01, y[idx]+0.01), color='b', fontsize=8, zorder=1)
            if z==z_selection:
                x_sel.append(x[idx])
                y_sel.append(y[idx])
    return x_sel, y_sel        

def plot_source_color_and_save_cuts(slope):
    """
    Plot the colors of sources in the catalog
    Make a colour cut and save the selected sources

    Args:
        slope (float): The slope of the linear fit to the z=6 points
    """
    cat_SE = np.genfromtxt(f_path / cat_folder / f'{cat_name}_filtered.cat', delimiter=' ', names=True, comments='#')
    F_x_F_xy_F_y = []
    for f_name in [f_name_list[1], f_name_list[0], f_name_list[2]]:
        filter_list = [filter_name[1:].lower() for filter_name in filter_dict.keys()] # get the filter names without the 'F'
        index = np.flatnonzero(np.core.defchararray.find(list(filter_dict.keys()),f_name)!=-1)[0] # get the index of the filter
        F_x_F_xy_F_y.append(cat_SE[f'f_{filter_list[index]}'])
    x = -2.5*np.log10(F_x_F_xy_F_y[1]/F_x_F_xy_F_y[0])
    y = -2.5*np.log10(F_x_F_xy_F_y[2]/F_x_F_xy_F_y[1])

    sel = (y>2) & (x<1) & (y>(slope*x+2)) # Boolean function of colour cut
    if hexbin:
        plt.hexbin(x[~sel], y[~sel], gridsize=1000, cmap='plasma', zorder=1, bins='log', alpha=0.9) #~ is the logical NOT operator
        plt.scatter(x[sel], y[sel], marker='s', edgecolor='k', c='red', s=15, label=r'$z \geq 7$', zorder=2)
        print(f'Number of sources selected: {np.sum(sel)}')
        print(f'Highest y flux: {np.max(y[sel])}')
        print(f'Lowest x flux: {np.min(x[sel])}')
    else:
        plt.scatter(x, y, marker='*', c='red', s=15, label='Sources', zorder=2)

    # Write new catalog with selected sources
    header = ' '.join(cat_SE.dtype.names)
    selected_catalog = cat_SE[sel]
    np.savetxt(f_path / cat_folder / f'{cat_name}_colour_sel.cat', selected_catalog, header=header, comments='#', fmt='%s')

def colour_colour_plot():
    """
    Plot the colour-colour diagram
    """
    plt.figure(dpi=450)
    x_sel, y_sel = plot_tracks(sfhz=True)

    # Calculate cuts
    slope = np.polyfit(x_sel, y_sel, 1)[0] # linear fit to z=z_selection points
    def fit(x, intercept=2):
        return slope*x + intercept # fit function
    x_cut = np.linspace(0, 1, 100)

    # Plot the cuts
    plt.plot(x_cut, fit(x_cut), lw=1.5, c='red', zorder=3)
    plt.hlines(y=2, xmin=-.7, xmax=0, lw=1.5, color='red', zorder=3)
    plt.vlines(x=1, ymin=fit(x_cut)[-1], ymax=12, lw=1.5, color='red', zorder=3)

    plot_source_color_and_save_cuts(slope)
    plt.xlim(-.7, 2)
    plt.ylim(-1, 12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title=r'$A_V$, sSFR [yr$^{{-1}}$]', title_fontsize=12, fontsize=12)
    if hexbin:
        og_handles, _ = plt.gca().get_legend_handles_labels()
        plt.legend(handles=og_handles + [Line2D([0], [0], marker='h', color='w', label='Sources',
                          markerfacecolor='darkblue', markersize=10)], bbox_to_anchor=(1.05, 1), loc='upper left', title=r'$A_V$, sSFR [yr$^{{-1}}$]', title_fontsize=12, fontsize=12)
    # Axes settings
    plt.gca().xaxis.set_minor_locator(AutoMinorLocator()) # set minor ticks
    plt.gca().yaxis.set_minor_locator(AutoMinorLocator())
    plt.tick_params(which='both', right='true', top='true', direction='in', labelsize=12, width=0.7)
    plt.tick_params(which='major', length=6)
    plt.tick_params(which='minor', length=3)     
    plt.xlabel(f_name_list[0]+r'$-$'+f_name_list[1], fontsize=14)
    plt.ylabel(f_name_list[2]+r'$-$'+f_name_list[3], fontsize=14)
    plt.title(rf'{{{f_name_list[0]}}}-dropout ($z\sim{{{z_selection}}}$)', fontsize=14)
    plt.gca().set_box_aspect(1) # set square (equal) aspect ratio without changing data limits
    plt.tight_layout()
    plt.savefig(fig_path / 'colour' / 'colour_colour_plot_v7.pdf', bbox_inches = 'tight')
    plt.show()

def main():
    global hexbin, f_x, f_xy, f_y, f_name_list, z_selection
    hexbin = True

    z_selection = 7

    # Define the filters
    f_x, f_xy, f_y, f_name_list = get_filters('F115W - F150W vs F090W - F115W')

    colour_colour_plot()

if __name__ == '__main__':
    main()