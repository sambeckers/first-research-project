from astropy.io import fits
import numpy as np

# Load the FITS file
file_path = '/Users/sam/FRESCO/eazy outputs/gds_photoz.eazypy.zout.fits'
hdul = fits.open(file_path)

# Print column names
print("Column Names:")
for col in hdul[1].columns.names:
    print(col)

# Access and print data from a specific column (replace 'COLUMN_NAME' with the desired column name)
column_name = 'COLUMN_NAME'
# column_data = hdul[1].data[column_name]
# print(f"\nValues in '{column_name}':")
# print(column_data)

z_phot_values = hdul[1].data['z_phot']
id = hdul[1].data['id']
# for i in id:
#     print(i)

# Print the values in the 'z_phot' column
# print("Values in 'z_phot':")
# for value in z_phot_values:
#     if value > 6:
#         print(value)


# Close the FITS file
hdul.close()
