import os
import pandas as pd
import requests
import pickle as pkl
import time
from data.state_dict import state_dict
import numpy as np
import geopandas as gpd

# bool wheather new address to geocode dictionary must be created (limited api calls)
CREATE_NEW_GEODICT = False
GEODICT_PATH = 'data/geo_dict.pkl'
COMBINED_DATA_PATH = 'data/combined_data.csv'
CLEANED_DATA_PATH = 'data/cleaned_data.pkl'
GEO_DATA_PATH = 'data/geo_data.pkl'


def combine_files(dir):
    ''' Combines identical dataframes in directory '''
    # list all files in directory
    file_paths = []
    for path, subdirs, filenames in os.walk(dir):
        for name in filenames:
            file_paths.append(os.path.join(path, name))

    print('Combining {} dataframes..'.format(len(file_paths)))

    # combine all files in data
    df = pd.DataFrame()
    for file in file_paths:
        # read and evaluate string column as list
        new_data = pd.read_csv(file, index_col=0, converters={'bullets': eval})
        df = df.append(new_data, ignore_index=True)

    return df


def geocode_address(address):
    ''' Converts address string to geocode object '''
    API_KEY = os.environ['GMAPS_API_KEY']
    params = {
        'key': API_KEY,
        'address': address,
    }

    base_url = 'https://maps.googleapis.com/maps/api/geocode/json?'

    response = requests.get(base_url, params=params).json()

    if response['status'] == 'OK':
        # dict_keys(['address_components', 'formatted_address', 'geometry', 'place_id', 'types'])
        results_dict = response['results'][0]
    else:
        results_dict = None
        print('Response status FAILED')

    return results_dict


def create_geo_dict(address_list, path):
    ''' Encode list of addresses with google API '''
    call_api = input(
        'Make API calls for {} addresses? (y/n): '.format(len(address_list)))
    if call_api == 'y':
        geocode_output = []
        for i, address in enumerate(address_list):
            print('- Geocode address ({}/{}): {}'.format(i,
                  len(address_list), address))
            geocode_output.append(geocode_address(address))
            time.sleep(0.1)

        geo_dict = dict(zip(address_list, geocode_output))
        with open(path, 'wb') as file:
            pkl.dump(geo_dict, file)
        print('Saved geo_dict to "{}"'.format(path))
        return geo_dict
    else:
        print('Aborted. Returning None')
        return None


def address_to_coordinates(address_col):
    # Create geocoded column
    if CREATE_NEW_GEODICT:
        address_list = address_col.unique()
        geo_dict = create_geo_dict(address_list, GEODICT_PATH)
    else:
        print('Load existing geo_dict')
        with open(GEODICT_PATH, 'rb') as file:
            geo_dict = pkl.load(file)

    geo_col = address_col.map(geo_dict)

    # Exctract info from geo_col
    lat_col = geo_col.apply(lambda x:
                            None if x is None else x.get('geometry').get('location').get('lat'))
    lng_col = geo_col.apply(lambda x:
                            None if x is None else x.get('geometry').get('location').get('lng'))
    return lat_col, lng_col


def clean_data(df):
    ''' Cleans columns and extracts info from string columns '''
    # Convert id to float
    df['id'] = df['id'].str.replace('selObject_', '').astype(int)

    # Create dummies from tags
    df['ebk'] = df['tags'].apply(lambda x: 'EBK' in x)
    df['garten'] = df['tags'].apply(lambda x: 'Garten' in x)
    df['balkon'] = df['tags'].apply(lambda x: 'Balkon' in x)
    df = df.drop('tags', axis=1)

    # Clean price column
    # remove rows without 'zzgl.|inkl.' in price (i.e. 'Preis auf Anfrage' and 'Garagen')
    df = df[df['price'].str.contains('zzgl.|inkl.')]
    df['inkl_NK'] = df['price'].apply(lambda x: 'inkl.' in x)  # create dummy for NK

    df['price'] = df['price'].str.extract('(\d[\d,.]*)')  # extract numbers
    df['price'] = df['price'].str.replace('.', '', regex=True)  # remove thousands dot
    df['price'] = df['price'].str.replace(',', '.').astype(float)  # convert to float

    # Convert area to float
    df['area'] = df['area'].str.extract('(\d[\d,.]*)')  # extract numbers
    df['area'] = df['area'].astype(float)

    # Convert rooms to float
    df['rooms'] = df['rooms'].str.extract('(\d[\d,.]*)')  # extract numbers
    df['rooms'] = df['rooms'].str.replace(',', '.').astype(float)  # replace sep., convert to float

    # Split bullets
    df['bullets'] = df['bullets'].apply(lambda x: x[-1])
    df['category'] = df['bullets'].apply(lambda x: x[0])
    df['city'] = df['bullets'].apply(lambda x: ' '.join(x[2:]))
    df = df.drop('bullets', axis=1)

    # Create address column
    df['state'] = df['state'].map(state_dict)
    df['address'] = df['city'] + ', ' + df['state'] + ', ' + 'Germany'

    # Remove outliers
    df['price'] = df['price'].where(df['price'].between(
        df['price'].quantile(.0001), df['price'].quantile(.9999)), None)
    df['area'] = df['area'].where(df['area'].between(
        df['area'].quantile(.0001), df['area'].quantile(.9999)), None)

    # Convert address to coordinates
    df['lat'], df['lng'] = address_to_coordinates(df['address'])

    # Drop NA & duplicates
    df = df.dropna()
    df = df.drop_duplicates(subset=['title', 'price', 'area'])
    df = df.reset_index(drop=True)

    # Drop unnecessary columns
    df = df.drop(['id', 'page', 'city', 'address'], axis=1)
    return df


def add_counties(df, map):
    """ Coverts data to geopandas DF and adds new shape file as main geometry."""
    map['geometry_map'] = map['geometry']

    # convert to geopandasdataframe
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lng, df.lat))
    gdf.crs = 'EPSG:4326'  # must match map data before joining

    gdf = gpd.sjoin(gdf, map, how='left', op='within')
    gdf = gdf.set_geometry('geometry_map')  # set geometry to areas
    gdf = gdf.drop(['index_right', 'USE', 'RS', 'RS_ALT', 'SHAPE_LENG', 'SHAPE_AREA'], axis=1)
    gdf = gdf.reset_index(drop=True)
    return gdf


if __name__ == '__main__':
    # Create complete data frame
    df = combine_files('downloads')
    df.to_csv(COMBINED_DATA_PATH)

    # Clean data frame
    df = clean_data(df)
    with open(CLEANED_DATA_PATH, 'wb') as f:
        pkl.dump(df, f)

    # Add german county to each observation
    map = gpd.read_file('data/vg2500_geo84/vg2500_krs.shp')
    gdf = add_counties(df, map)

    with open(GEO_DATA_PATH, 'wb') as f:
        pkl.dump(gdf, f)
