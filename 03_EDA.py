import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


# SHAPE_PATH = "data/Germany_shapefile/de_10km.shp"
# SHAPE_PATH = "data/vg2500_geo84/vg2500_bld.shp"
# SHAPE_PATH = "data/vg2500_geo84/vg2500_rbz.shp"
# SHAPE_PATH = "data/vg2500_geo84/vg2500_sta.shp"
SHAPE_PATH = "data/vg2500_geo84/vg2500_krs.shp"
map_df = gpd.read_file(SHAPE_PATH)
print(map_df)
map_df.plot()
plt.show()