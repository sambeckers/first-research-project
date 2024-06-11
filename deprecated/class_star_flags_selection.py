"""
class_star_flags_selection
Created on 01-04-2024

@author(s): Sam Beckers

Reads in the GDS catalog and filters out objects with a CLASS_STAR value greater than 0.9 or any non-zero FLAGS value. 
The filtered catalog is written to a new file.
"""
import os
import numpy as np
os.chdir('/Users/sam/FRESCO/Catalogs_v2')

cat = np.genfromtxt('gds_catalog.cat', delimiter=' ', names=True, comments='#')

sel = (cat['CLASS_STAR_444w'] < 0.9) & (cat['FLAGS_444w'] == 0) & (cat['f_444w']/cat['e_444w'] > 5)
cat_filter = cat[sel]
print(len(cat_filter), len(cat))

# Write the filtered catalog to a new file
header = ' '.join(cat.dtype.names)
np.savetxt('gds_catalog_filtered.cat', cat_filter, header=header, comments='#', fmt='%s')

try: 
    cat_zphot = np.genfromtxt('gds_zphot_catalog1.cat', delimiter=' ', names=True, comments='#')
    #(z97 - z02)/(1+z50)/2
    sel2 = (cat_zphot['z_975'] - cat_zphot['z_025'])/(1 + cat_zphot['z_500'])/2 < 0.01
    cat_zphot_filter = cat_zphot[sel2]
    print(len(cat_zphot_filter), len(cat_zphot))
    header = ' '.join(cat_zphot.dtype.names)
    np.savetxt('gds_zphot_catalog_filtered1.cat', cat_zphot_filter, header=header, comments='#', fmt='%s')
except FileNotFoundError:
    print('z_phot catalog not found')















# # Open the full catalog
# with open('gds_catalog.cat', 'r') as catalog:
#     data = catalog.readlines()
#     # Read the header
#     header = data[0]
#     header_list = header.split()[1:]

#     # Find the indices of the CLASS_STAR and FLAGS columns
#     class_star_indices = [header_list.index(col) for col in header_list if 'CLASS_STAR' in col]
#     flags_indices = [header_list.index(col) for col in header_list if 'FLAGS' in col]

#     with open('gds_catalog_filtered.cat', 'w') as filtered_catalog:
#         # Write the header to the new file
#         filtered_catalog.write(header)
        
#         # Iterate over the rows and write the filtered rows to the new file
#         for row in data[1:]:
#             row_list = row.split()
#             star_classes = [float(row_list[i]) for i in class_star_indices] # Get the CLASS_STAR values
#             flags = [float(row_list[i]) for i in flags_indices] # Get the FLAGS values
#             if not (any(star_class > 0.9 for star_class in star_classes) and any(flag != 0.0 for flag in flags)): # Check if the object should be filtered out
#                 filtered_catalog.write(row)
#         print('Filtered catalog created')
            
# with open('filtered_catalog.cat', 'r') as filtered_catalog:
#     filtered_data = filtered_catalog.readlines()
#     num_rows = len(filtered_data)
#     print(f'Objects filtered out: {len(data) - num_rows} ({(len(data) - num_rows) / len(data) * 100:.2f}%)')