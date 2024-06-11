"""
catalogs
Created on 20-01-2024

@author(s): Sam Beckers

"""
import os
from pathlib import Path
import numpy as np
import pandas as pd
from astropy.io import fits
import matplotlib.pyplot as plt
from PyPDF2 import PdfMerger
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "Times New Roman",
    "font.sans-serif": "helvetica"
})
from paths_and_global_vars import *

def get_cat_name_filter_numbers():
    """
    Retrieves the catalog names and filter numbers from a file.

    Returns:
        cat_names (list): A list of catalog names.
        filter_numbers (list): A list of filter names extracted from the catalog names.
    """
    cat_names = []
    with open(f_path / cat_filter_names, 'r') as catalog_file:
        catalog_names = catalog_file.read().splitlines()
        for cat_name in catalog_names:
            cat_names.append(cat_name)
    return cat_names, [cat_name.split('_')[0][3:] for cat_name in cat_names]

def full_gds_catalog():
    """
    Generate a full catalog by combining multiple catalogs from different filters.
    """
    # Read in the catalog names
    cat_names, filters = get_cat_name_filter_numbers()

    # Read in the catalogs
    os.chdir(f_path / cat_folder)
    columns = [[[] for _ in range(len(cat_names))] for _ in range(20)] # 20 empty lists for each parameter, empty lists within for each filter
    for idx, cat_name in enumerate(cat_names):
        with open(cat_name, 'r') as catalog:
            for row in catalog:
                if row.startswith('#'): # Skip comment lines that start with #
                    continue
                row_val = row.split() # Split the row into a list of values
                for i in range(len(row_val)): # Loop over the values in the row
                    columns[i][idx].append(row_val[i]) # Add the value to the corresponding parameter and filter

    # Find the maximum number of sources in a catalog
    number_arr = []  
    for i in range(len(columns)):
        number_arr.append(len(columns[0][i]))
    max_sources_idx = np.argmax(number_arr)
    ID = columns[0][max_sources_idx]

    del columns[0] # Remove the ID column

    # Write the catalogs to a new file
    parameters_to_save = [
        'f', 'e', 'MAG_APER', 'MAGERR_APER', 'XPEAK_IMAGE', 'YPEAK_IMAGE',
        'XPEAK_WORLD', 'YPEAK_WORLD', 'ALPHAPEAK_J2000', 'DELTAPEAK_J2000', 'X_IMAGE', 'Y_IMAGE',
        'ALPHA_J2000', 'DELTA_J2000', 'FLAGS', 'CLASS_STAR', 'FLUX_RADIUS', 'XMODEL_IMAGE', 'YMODEL_IMAGE'
    ] #from SE
    header = ['# id'] # Start the header with the source ID
    for param in parameters_to_save:
        for filter_name in filters:
            header.append(f'{param}_{filter_name}') # Add the parameter and filter to the header

    with open(f'{cat_name}_catalog.cat', 'w') as catalog_file:
        catalog_file.write(' '.join(header) + '\n')
        for source_idx in range(len(ID)): # Loop over the sources
            output_row = [ID[source_idx]]  # Start each row with the source ID
            for param_idx, param in enumerate(parameters_to_save):
                for filter_name in filters:
                    # Get the corresponding value for the current source, parameter, and filter
                    value = columns[param_idx][filters.index(filter_name)][source_idx]
                    if param == 'f' or param == 'e':
                        value = str(float(value) * 10**-2) # Convert flux/error from 10*nJy to µJy
                    output_row.append(value)

            # Append the row to the output file
            catalog_file.write(' '.join(output_row) + '\n')
    print('Full catalog saved\n')
    os.chdir(f_path)

def class_star_flags_nondetect_selection():
    """
    Filter the catalog based on:
    - CLASS_STAR_444w <= 0.9 (1.0 is a star)
    - FLAGS_444w <= 7 (accepts 1, 2, 4 and combinations)
    - f_444w/e_444w >= 5 (SNR >= 5)
    - Replace flux with -100.0 if flux and error are both zero (non-detection), s.t. EAZY will not observe it
    """
    try: 
        cat = np.genfromtxt(f_path / cat_folder / f'{cat_name}_catalog.cat', delimiter=' ', names=True, comments='#')

        sel = (cat['CLASS_STAR_444w'] < 0.8) & (cat['FLAGS_444w'] <= 7) & (cat['f_444w']/cat['e_444w'] >= 5)
        cat_filter = cat[sel]

        _, filters = get_cat_name_filter_numbers()
        for filter in filters:
            for idx, (f, e) in enumerate(zip(cat_filter[f'f_{filter}'], cat_filter[f'e_{filter}'])):
                if f == 0.0 and e == 0.0:
                    # print(f'Filter {filter} has zero flux and error at index {idx}')
                    cat_filter[f'f_{filter}'][idx] = -100.0
                
        # Write the filtered catalog to a new file
        header = ' '.join(cat.dtype.names)
        np.savetxt(f_path / cat_folder / f'{cat_name}_catalog_filtered.cat', cat_filter, header=header, comments='#', fmt='%s')
        print(f'Filtered catalog (class_star, flags, SNR, non-detections) saved.\nOriginal catalog: {len(cat)} sources \nFiltered catalog: {len(cat_filter)} sources, {len(cat) - len(cat_filter)} sources removed\n')
    except FileNotFoundError:
        print(f'{cat_name}_catalog.cat not found. Run full_gds_catalog() first.')

def photoz_catalog():
    """
    Create a catalog combining the filtered SE catalog & photometric redshifts from EAZY.
    """
    # Read in filter names
    try: 
        _, filters = get_cat_name_filter_numbers()

        # Read in the catalog including headers
        cat = np.genfromtxt(f_path / cat_folder / f'{cat_name}_catalog_filtered.cat', delimiter=' ', names=True, comments='#')

        # Read in the eazy zout catalog FITS
        zout = fits.open(f_path / eazy_folder / f'{cat_name}_photoz.eazypy.zout.fits')
        z_phot = zout[1].data['z_phot']
        z_phot_6 = z_phot[z_phot > 6] # Select sources with z_phot > 6

        ID = cat['id'][z_phot>6].astype('int') # convert values to int

        ra = cat['ALPHA_J2000_444w'][z_phot>6]
        dec = cat['DELTA_J2000_444w'][z_phot>6]

        flux = [[] for _ in range(len(filters))]
        flux_err = [[] for _ in range(len(filters))]
        mag_aper = [[] for _ in range(len(filters))]
        for idx, filter in enumerate(filters):
            flux[idx] = cat[f'f_{filter}'][z_phot>6]
            flux_err[idx] = cat[f'e_{filter}'][z_phot>6]
            mag_aper[idx] = cat[f'MAG_APER_{filter}'][z_phot>6]

        # Create a DataFrame with the params for the selected sources
        df = pd.DataFrame({
            'ID': ID,
            'z_phot': z_phot_6,
            'z_025': zout[1].data['z025'][z_phot>6],
            'z_975': zout[1].data['z975'][z_phot>6],
            'z_500': zout[1].data['z500'][z_phot>6],
            'ra': ra,
            'dec': dec,
            **{f'f_{filter}': flux[idx] for idx, filter in enumerate(filters)},
            **{f'e_{filter}': flux_err[idx] for idx, filter in enumerate(filters)},
            **{f'MAG_APER_{filter}': mag_aper[idx] for idx, filter in enumerate(filters)}
        })

        # Save DataFrame to a new .cat file
        df.to_csv(f_path / cat_folder / f'{cat_name}_zphot_catalog.cat', sep=' ', index=False)
        print('Photometric redshift catalog saved\n')
        zout.close()
    except FileNotFoundError:
        print(f'{cat_name}_catalog_filtered.cat not found. Run class_star_flags_selection() first.')

def z_bin_selection(strictness):
    """
    Filter the z_phot catalog based on the strictness of the z_phot bin width.
    Plot the number of sources remaining as a function of the strictness.

    Args:
        strictness (float): The strictness of the z_phot bin width (e.g. 0.006)
    """
    try: 
        cat_zphot = np.genfromtxt(f_path / cat_folder / f'{cat_name}_zphot_catalog.cat', delimiter=' ', names=True, comments='#')
        #(z97 - z02)/(1+z50)/2
        sel2 = (cat_zphot['z_975'] - cat_zphot['z_025'])/(1 + cat_zphot['z_500'])/2 < strictness
        cat_zphot_filter = cat_zphot[sel2]
        header = ' '.join(cat_zphot.dtype.names)
        np.savetxt(f_path / cat_folder / f'{cat_name}_zphot_catalog_filtered.cat', cat_zphot_filter, header=header, comments='#', fmt='%s')
        print(f'Filtered z_phot catalog saved.\nOriginal catalog: {len(cat_zphot)} sources \nFiltered catalog: {len(cat_zphot_filter)} sources, {len(cat_zphot) - len(cat_zphot_filter)} sources removed\n')

        # Plot the number of sources remaining as a function of the strictness
        strictness_arr = np.linspace(0.01, 0.001, 100)
        num_sources = []
        for s in strictness_arr:
            sel = (cat_zphot['z_975'] - cat_zphot['z_025'])/(1 + cat_zphot['z_500'])/2 < s
            num_sources.append(len(cat_zphot[sel]))
        
        plt.figure(dpi=450)
        plt.plot(strictness_arr, num_sources, c='k')
        plt.axvline(x=strictness, c='r', ls='--', label=f'Chosen strictness = {strictness}')
        plt.xlabel(r'Strictness in $p(z)$ bin width', fontsize=14)
        plt.ylabel('Number of remaining sources', fontsize=14)
        plt.legend()
        plt.savefig(fig_path / 'z_bin_selection.pdf', bbox_inches='tight')
        plt.show()
    except FileNotFoundError:
        print(f'{cat_name}_zphot_catalog.cat not found. Run photoz_gds_catalog() first.')

def z_phot_hist():
    """
    Plot a histogram of the z_phot values.
    """
    try:
        cat = np.genfromtxt(f_path / cat_folder / f'{cat_name}_zphot_catalog_filtered.cat', delimiter=' ', names=True, comments='#')
        z_phot = cat['z_phot']

        plt.figure(dpi=450)
        plt.hist(z_phot, bins=30, color='k')
        plt.xlabel(r'$\rm{z_{phot}}$', fontsize=14)
        plt.ylabel('Count', fontsize=14)
        plt.savefig(fig_path / 'z_phot_hist.pdf', bbox_inches='tight')
        plt.show()
    except FileNotFoundError:
        print(f'{cat_name}_zphot_catalog_filtered.cat not found. Run z_bin_selection() first.')

def format_cc_sel_catalog():
    try:
        cat_cc = np.genfromtxt(f_path / cat_folder / f'{cat_name}_catalog_colourcut_sel.cat', delimiter=' ', names=True, comments='#')
        _, filters = get_cat_name_filter_numbers()
        flux = [[] for _ in range(len(filters))]
        flux_err = [[] for _ in range(len(filters))]
        mag_aper = [[] for _ in range(len(filters))]
        for idx, filter in enumerate(filters):
            flux[idx] = cat_cc[f'f_{filter}']
            flux_err[idx] = cat_cc[f'e_{filter}']
            mag_aper[idx] = cat_cc[f'MAG_APER_{filter}']
        df = pd.DataFrame({
            'ID': cat_cc['id'],
            'ra': cat_cc['ALPHA_J2000_444w'],
            'dec': cat_cc['DELTA_J2000_444w'],
            **{f'f_{filter}': flux[idx] for idx, filter in enumerate(filters)},
            **{f'e_{filter}': flux_err[idx] for idx, filter in enumerate(filters)},
            **{f'MAG_APER_{filter}': mag_aper[idx] for idx, filter in enumerate(filters)}
        })
        df.to_csv(f_path / cat_folder / f'{cat_name}_catalog_colourcut_sel_formatted.cat', sep=' ', index=False)
        print('Formatted colour-cut selection catalog saved\n')
    except FileNotFoundError:
        print(f'{cat_name}_catalog_colourcut_sel.cat not found. Run colour_colour_cuts_v2.py first.')

def final_catalog():
    try:
        cat_cc = np.genfromtxt(f_path / cat_folder / f'{cat_name}_catalog_colourcut_sel.cat', delimiter=' ', names=True, comments='#')
        cat_zphot = np.genfromtxt(f_path / cat_folder / f'{cat_name}_photoz_final_v2.cat', delimiter=' ', names=True, comments='#')
        print(len(cat_zphot['ID']))

        count = 0
        print('Sources in both catalogs:')
        for id in cat_cc['id']:
            if id in cat_zphot['ID']:
                print(f'{id}, z_phot={cat_zphot[cat_zphot["ID"] == id]["z_phot"][0]}')
                count += 1
        print(f'Count: {count}')
        
    except FileNotFoundError:
        print(f'{cat_name}_catalog_colourcut_sel.cat or {cat_name}_zphot_catalog_final.cat not found. Run colour_colour_cuts_v2.py or photoz_gds.ipynb first.')

def cat_from_IDs():
    IDs = [141.0, 207.0,  340.0, 402.0, 743.0, 747.0, 789.0, 799.0, 1574.0, 1814.0, 1838.0, 2039.0, 2403.0, 
           2472.0, 2478.0, 2610.0, 2993.0, 3019.0, 3173.0, 3326.0, 3363.0, 3516.0, 3685.0, 3772.0, 3810.0,
           4231.0, 4689.0, 4760.0, 5093.0, 5204.0, 5378.0, 5614.0, 5844.0, 6016.0, 6030.0, 6174.0, 6491.0,
           7037.0, 7058.0, 7914.0, 8158.0, 8223.0, 8296.0, 8432.0, 8474.0, 8556.0, 8620.0, 
           8655.0, 8665.0, 8775.0, 8857.0, 8978.0, 9183.0, 9239.0, 9328.0, 9359.0, 9554.0, 9649.0, 10041.0, 10089.0, 
           10394.0, 10491.0, 10782.0, 10839.0, 11131.0, 11205.0, 11286.0, 11301.0, 11366.0, 11629.0, 11685.0, 
           11895.0, 11992.0, 12436.0, 12799.0, 12925.0, 13464.0, 13762.0, 13932.0, 13953.0, 13965.0, 14145.0,
           14155.0, 14219.0, 14430.0, 14529.0, 14962.0, 14992.0, 15200.0, 15208.0, 15229.0, 15255.0, 15367.0,
           16081.0, 16366.0, 16419.0, 16435.0, 16622.0, 16661.0, 16686.0, 16733.0, 16751.0, 16897.0, 17096.0,
           17250.0, 17279.0, 17873.0, 18105.0, 18146.0, 18741.0, 18806.0, 18907.0, 18911.0, 19101.0, 19691.0, 
           19742.0, 19844.0, 20426.0, 20656.0, 20789.0, 20947.0, 20970.0, 21499.0, 21692.0, 21724.0, 21926.0]
    cat = np.genfromtxt(f_path / cat_folder / f'{cat_name}_catalog_colourcut_sel_formatted.cat', delimiter=' ', names=True, comments='#')
    sel = np.isin(cat['ID'], IDs) # Match the IDs in the catalog with the IDs in the list
    for idx, i in enumerate(np.isin(IDs, cat['ID'][sel])):
        if not i:
            print(f'{IDs[idx]} not in photometric catalog. Check for typos / wrong catalog.')
    df = pd.DataFrame(cat[sel])

    zout = fits.open(f_path / eazy_folder / f'{cat_name}_photoz.eazypy.zout.fits')
    sel2 = np.isin(zout[1].data['id'], IDs) # Match the IDs in the zout catalog with the IDs in the list
    for idx, i in enumerate(np.isin(IDs, zout[1].data['id'][sel2])):
        if not i:
            print(f'{IDs[idx]} not in zout catalog. Check for typos / wrong catalog.')
    z_phot = zout[1].data['z_phot']
    df.insert(1, 'z_phot', z_phot[sel2].byteswap().newbyteorder()) # Insert z_phot column at 1st index. byteswap and newbyteorder to fix endianness

    df.to_csv(f_path / cat_folder / f'{cat_name}_catalog_colourcut_sel_formatted_vi.cat', sep=' ', index=False)

    def plot_merger(IDs, name):
        """
        Merge the PDFs of the colour-colour fits for the selected sources.

        Args:
            IDs (list): A list of source IDs to merge.
        """
        merger = PdfMerger()
        for id in IDs:
            # Open each PDF file and append it to the merger
            with open(fig_path / f'colour_colour_fits/gds_photoz_fit_{id}.pdf', 'rb') as f:
                merger.append(f)
        # Write the merged PDF to the output file
        with open(fig_path / f'colour_colour_fits/{name}.pdf', 'wb') as f:
            merger.write(f)

    plot_merger(IDs, 'colour_cut_sel_fits_vi')

    id_z_6 = pd.read_csv(fig_path/ 'colour_colour_fits/id_z_6.cat')
    sel3 = np.isin(id_z_6['ID (z>6)'], IDs)
    plot_merger(id_z_6['ID (z>6)'][~sel3], 'colour_cut_sel_vi_rejected')
    plot_merger([340.0, 743.0, 747.0, 789.0, 799.0, 1574.0, 1814.0, 2610.0, 3019.0, 3363.0, 3516.0, 3685.0, 
                3772.0, 5378.0, 7037.0, 7914.0, 8556.0, 8665.0, 9328.0, 11286.0, 11895.0, 14430.0, 14529.0,
                15367.0, 16686.0, 16751.0, 16897.0, 18146.0, 21724.0, 21926.0], 'colour_cut_sel_vi_candidates')
    

def main():
    """
    Main function to run the catalog functions.
    Adjust the global constants to match the file paths on your system/catalog
    """
    # full_gds_catalog()
    # class_star_flags_nondetect_selection()
    # photoz_catalog()
    # z_bin_selection(0.006)
    # z_phot_hist()
    # format_cc_sel_catalog()
    # final_catalog()
    cat_from_IDs()

if __name__ == '__main__':
    main()