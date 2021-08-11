import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import pickle as pkl
import numpy as np
from scipy import stats

# Load data
map_df = gpd.read_file('data/vg2500_geo84/vg2500_krs.shp') # 10km squares: data/Germany_shapefile/de_10km.shp
with open("data/cleaned_data.pkl", 'rb') as f:
    data = pkl.load(f)

data['log_price'] = np.log(data['price'])

# Plot map  # TODO check intersection and add landkreise as dummies (+ interaction terms) 
map_df.info()
map_df.plot()
plt.show()  

# Plot data
data.info()
data.describe()
data.hist(bins= 50, figsize=(20,15))
plt.show()

data.plot(kind='scatter', x="lng", y="lat", alpha=1, figsize=(4,5), label='log price', s=2, c='log_price', cmap=plt.get_cmap('gist_ncar'), colorbar=True)
plt.show()

data.plot(kind='scatter', x='area', y='price', alpha=0.1)
plt.show()
