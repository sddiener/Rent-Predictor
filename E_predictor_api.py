from B_cleaner import geocode_address, add_counties
import pandas as pd
import geopandas as gpd
import pickle as pkl


def convert_address_to_county(address_str):
    # Call google API
    geo_object = geocode_address(address_str)

    # Extract info from geo_col
    lat = geo_object.get('geometry').get('location').get('lat')
    lng = geo_object.get('geometry').get('location').get('lng')

    # Convert to county
    df = pd.DataFrame({'lat': [lat], 'lng': [lng]})
    map = gpd.read_file('data/vg2500_geo84/vg2500_krs.shp')

    gdf = add_counties(df, map)  # calculates intersection with map.shp
    county = gdf['GEN'][0]  # first element
    return county


def make_prediction(model, df):
    """ Make predictions from input data """
    assert (df.columns == ['area', 'rooms', 'ebk', 'garten', 'balkon', 'inkl_NK', 'category',
                           'GEN']).all()

    # Convert address str to country str (GEN)
    df['GEN'][0] = convert_address_to_county(df['GEN'][0])

    # Preprocessing Data
    with open('models/transformer.pkl', 'rb') as f:
        transformer = pkl.load(f)

    X = transformer.transform(df)  # onehot encode and scale data

    # Prediction
    pred = model.predict(X)
    pred = {'pred': pred}  # convert to dict

    return pred


if __name__ == '__main__':
    print("Checking prediction")
    df = pd.DataFrame(data={
        'area': [100],
        'rooms': [3],
        'ebk': [False],
        'garten': [False],
        'balkon': [False],
        'inkl_NK': [False],
        'category': ['Etagenwohnung'],
        'GEN': ['Hamburg']
    })

    with open('models/ols.pkl', 'rb') as f:
        model = pkl.load(f)
    pred = make_prediction(model, df)
    print(pred)
