import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import pickle as pkl
import numpy as np
from scipy import stats

PLOT_DIR = "plots/"

# Load data
map = gpd.read_file('data/vg2500_geo84/vg2500_krs.shp')
map['geometry_map'] = map['geometry']

with open("data/cleaned_data.pkl", 'rb') as f:
    data = pkl.load(f)

# convert to geopandasdataframe
gdata = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data.lng, data.lat))
gdata.crs = "EPSG:4326"  # must match map data before joining


# Plot data
data.hist(bins=50, figsize=(10, 7))
plt.savefig(PLOT_DIR+"data_hist")

data.plot(kind='scatter', x="lng", y="lat", alpha=1, figsize=(4, 5), s=2)
# c='log_price', label='log price', cmap=plt.get_cmap('gist_ncar'), colorbar=True)
plt.savefig(PLOT_DIR+"data_points")


# Add map to data
gdata = gpd.sjoin(gdata, map, how='left', op="within")
gdata = gdata.set_geometry('geometry_map')  # set geometry to areas
gdata_diss = gdata.dissolve(by='GEN', aggfunc='mean')

fig, ax = plt.subplots(1, 1, figsize=(8, 10))

gdata_diss.plot(column='price', ax=ax, legend=True, cmap=plt.get_cmap('Spectral_r'),
                legend_kwds={'label': "Avg. Price in €"})
plt.title('Average Prices Counties')
plt.savefig(PLOT_DIR+"avg_prices_county")
