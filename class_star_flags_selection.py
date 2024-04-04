"""
class_star_flags_selection
Created on 01-04-2024

@author(s): Sam Beckers

Reads in the GDS catalog and filters out objects with a CLASS_STAR value greater than 0.9 or any non-zero FLAGS value. 
The filtered catalog is written to a new file.
"""

from astropy.table import Table
import os
import numpy as np
os.chdir('/Users/sam/FRESCO/Catalogs_v2')

# Open the full catalog
with open('gds_catalog.cat', 'r') as catalog:
    data = catalog.readlines()
    # Read the header
    header = data[0]
    header_list = header.split()[1:]

    # Find the indices of the CLASS_STAR and FLAGS columns
    class_star_indices = [header_list.index(col) for col in header_list if 'CLASS_STAR' in col]
    flags_indices = [header_list.index(col) for col in header_list if 'FLAGS' in col]

    with open('gds_catalog_filtered.cat', 'w') as filtered_catalog:
        # Write the header to the new file
        filtered_catalog.write(header)
        
        # Iterate over the rows and write the filtered rows to the new file
        for row in data[1:]:
            row_list = row.split()
            star_classes = [float(row_list[i]) for i in class_star_indices] # Get the CLASS_STAR values
            flags = [float(row_list[i]) for i in flags_indices] # Get the FLAGS values
            if not (any(star_class > 0.9 for star_class in star_classes) and any(flag != 0.0 for flag in flags)): # Check if the object should be filtered out
                filtered_catalog.write(row)
        print('Filtered catalog created')
            
with open('filtered_catalog.cat', 'r') as filtered_catalog:
    filtered_data = filtered_catalog.readlines()
    num_rows = len(filtered_data)
    print(f'Objects filtered out: {len(data) - num_rows} ({(len(data) - num_rows) / len(data) * 100:.2f}%)')