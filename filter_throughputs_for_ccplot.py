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

# def plot_filter(filter_path, label=None):
    """Plot the filter transmission curve
    Args:
        filter_path (str): Path to the filter transmission curve (e.g. 'JWST_NIRCam.F182M.dat')
        ax (matplotlib.axes._subplots.AxesSubplot): The axis to plot the filter on
        label (str): The label for the filter
        color (str): The color of the filter
    """
    f = define_eazy_filter(filter_path)
    # plt.figure(dpi=450)
    plt.plot(f.wave, f.throughput,lw=2, label=label)
    plt.xscale('log')

def plot_SED_and_filters(sed, filter_dict, z):
    """Plot SED and filter throughputs in the same figure
    Args:
        sed_path (str): Path to the SED file
        filter_dict (dict): Dictionary containing filter names and their corresponding transmission curve paths
    """

    # sed = templates.Template(sed_path)

    fig, ax = plt.subplots(dpi=450, figsize=(8,4))
    ax.semilogy(sed.wave*(1+z), sed.flux_flam(), label=f'SED, z={z}', lw=1, c='k')
    ax.set_xlabel(r'$\lambda [\rm{\r{A}}]$', fontsize=14)
    ax.set_ylabel(r'$\lambda F_{\lambda}$ [erg s$^{-1}$ cm$^{-2}$]', fontsize=14)
    ax.legend(loc='upper right', fontsize=14)

    ax2 = ax.twinx()
    f_min_arr = []
    f_max_arr = []

    cmap = plt.get_cmap('rainbow')
    colors = cmap(np.linspace(0,1,len(filter_dict))) 
    
    for (i, (filter_name, filter_path)) in enumerate(filter_dict.items()):
        f = define_eazy_filter(filter_path)
        f_min_arr.append(f.wave.min())
        f_max_arr.append(f.wave.max())
        ax2.plot(f.wave, f.throughput, label=filter_name, lw=2,c=colors[i])
        ax2.fill_between(f.wave, f.throughput, alpha=0.2, color=colors[i])
        ax2.set_ylabel('Filter Throughput [arbitrary units]', fontsize=14)
        ax2.set_ylim(0,1)

    ly_alpha_break = 912*(1+z)
    ly_alpha = 1216*(1+z)
    # flux_flam_at_break = sed.flux_flam()[np.where(sed.wave*(1+z) >= ly_alpha_break)[0][0]]
    
    plt.annotate("",
            xy=(ly_alpha_break,max(sed.flux_flam())), xycoords='data',
            xytext=(ly_alpha_break, max(sed.flux_flam())+0.15), textcoords='data',
            arrowprops=dict(arrowstyle="-|>",
                            connectionstyle="arc3", color='k', lw=1),
            )
    plt.text(ly_alpha_break+1000, max(sed.flux_flam())+0.1, r'Ly$\alpha$ break at'+f' {ly_alpha_break}'+r'$\rm{\r{A}}$ (912$\rm{\r{A}}$ rest-frame)', fontsize=11, ha='left')

    plt.xlim(10**3,right=max(f_max_arr))
    fig.tight_layout()
    plt.legend(bbox_to_anchor=(1.1, 0.5), loc='center left', fontsize=14, ncol=2)
    plt.show()

os.chdir('/Users/sam/eazy-photoz')
template_list = templates.read_templates_file('templates/spline_templates_v3/c2020_spline.param')
# template_list = templates.read_templates_file('templates/sfhz/carnall_sfhz_13.param')
print(template_list)
# SED = '/Users/sam/eazy-photoz/templates/spline_templates_v3/spline_age0.31_av1.0.fits'

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

# for SED in template_list:
#     plot_SED_and_filters(SED, filter_dict, 15)

plot_SED_and_filters(template_list[0], filter_dict, 7)