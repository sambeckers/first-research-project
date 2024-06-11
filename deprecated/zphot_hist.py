import numpy as np
import matplotlib.pyplot as plt
import os
os.chdir('/Users/sam/FRESCO/Catalogs_v2')

cat = np.genfromtxt('gds_zphot_catalog_filtered1.cat', delimiter=' ', names=True, comments='#')

z_phot = cat['z_phot']

plt.figure(dpi=450)
plt.hist(z_phot, bins=30)
plt.xlabel('z_phot')
plt.ylabel('Count')
plt.show()