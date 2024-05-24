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
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "Times New Roman",
    "font.sans-serif": "helvetica"
})

def get_cat_name_filter_numbers():
    cat_names = []
    with open(f_path / cat_filter_names, 'r') as catalog_file:
        catalog_names = catalog_file.read().splitlines()
        for cat_name in catalog_names:
            cat_names.append(cat_name)
    return cat_names, [cat_name.split('_')[0][3:] for cat_name in cat_names] # Get the filter names from the catalog names

def full_gds_catalog():
    # Read in the catalog names
    cat_names, filters = get_cat_name_filter_numbers()

    # Read in the catalogs
    os.chdir(f_path / cat_folder)
    columns = [[[] for _ in range(len(cat_names))] for _ in range(20)] # 20 empty lists for each parameter, empty lists within for each filter
    for idx, cat_name in enumerate(cat_names):
        with open(cat_name, 'r') as catalog:
            for row in catalog:
                # Skip comment lines that start with #
                if row.startswith('#'):
                    continue
                row_val= row.split() # Split the row into a list of values
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
    try: 
        cat = np.genfromtxt(f_path / cat_folder / f'{cat_name}_catalog.cat', delimiter=' ', names=True, comments='#')

        sel = (cat['CLASS_STAR_444w'] <= 0.9) & (cat['FLAGS_444w'] <= 7) & (cat['f_444w']/cat['e_444w'] >= 5)
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
    try: 
        cat_zphot = np.genfromtxt(f_path / cat_folder / f'{cat_name}_zphot_catalog_corr.cat', delimiter=' ', names=True, comments='#')
        #(z97 - z02)/(1+z50)/2
        sel2 = (cat_zphot['z_975'] - cat_zphot['z_025'])/(1 + cat_zphot['z_500'])/2 < strictness
        cat_zphot_filter = cat_zphot[sel2]
        header = ' '.join(cat_zphot.dtype.names)
        np.savetxt(f_path / cat_folder / f'{cat_name}_zphot_catalog_filtered_corr.cat', cat_zphot_filter, header=header, comments='#', fmt='%s')
        print(f'Filtered z_phot catalog saved.\nOriginal catalog: {len(cat_zphot)} sources \nFiltered catalog: {len(cat_zphot_filter)} sources, {len(cat_zphot) - len(cat_zphot_filter)} sources removed\n')

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
    try:
        cat = np.genfromtxt(f_path / cat_folder / f'{cat_name}_zphot_catalog_filtered_corr.cat', delimiter=' ', names=True, comments='#')
        z_phot = cat['z_phot']

        plt.figure(dpi=450)
        plt.hist(z_phot, bins=30, color='k')
        plt.xlabel(r'$\rm{z_{phot}}$', fontsize=14)
        plt.ylabel('Count', fontsize=14)
        plt.savefig(fig_path / 'z_phot_hist.pdf', bbox_inches='tight')
        plt.show()
    except FileNotFoundError:
        print(f'{cat_name}_zphot_catalog_filtered_corr.cat not found. Run z_bin_selection() first.')

def main():
    global f_path
    f_path = Path('/Users/sam/FRESCO/') # Path to the FRESCO directory

    global fig_path
    fig_path = Path('/Users/sam/Documents/GitHub/FRP/Figures/')

    global cat_folder
    cat_folder = 'Catalogs_v2'

    global eazy_folder
    eazy_folder = 'eazy outputs'

    global cat_filter_names
    cat_filter_names = 'catalog-names_incl_f444w.txt'

    global cat_name
    cat_name = 'gds'

    full_gds_catalog()
    class_star_flags_nondetect_selection()
    photoz_catalog()
    z_bin_selection(0.006)
    z_phot_hist()

if __name__ == '__main__':
    main()