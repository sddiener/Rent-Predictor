import os
import pandas as pd
import requests

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
        new_data = pd.read_csv(file, index_col=0, converters={'bullets': eval}) # read and evaluate string column as list
        df = df.append(new_data, ignore_index=True)

    return df

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
    df = df[df['price'].str.contains('zzgl.|inkl.')] # remove rows without these strings in price (i.e. "Preis auf Anfrage" and "Garagen")
    df['inkl_NK'] = df['price'].apply(lambda x: 'inkl.' in x) # create dummy if additional costs are included

    df['price'] = df['price'].str.extract('(\d[\d,.]*)') # extract numbers
    df['price'] = df['price'].str.replace('.','', regex=True) # remove thousands dot
    df['price'] = df['price'].str.replace(',','.').astype(float) # replace seperator and convert to float

    # Convert area to float  # TODO filter NAs
    df['area'] = df['area'].str.extract('(\d[\d,.]*)') # extract numbers
    df['area'] = df['area'].astype(float) 

    # Convert rooms to float  # TODO filter NAs
    df['rooms'] = df['rooms'].str.extract('(\d[\d,.]*)') # extract numbers
    df['rooms'] = df['rooms'].str.replace(',','.').astype(float) # replace seperator and convert to float

    # Split bullets
    df['bullets'] = df['bullets'].apply(lambda x: x[-1]) 
    df['type'] = df['bullets'].apply(lambda x: x[0]) 
    df['city'] = df['bullets'].apply(lambda x: ' '.join(x[2:]))
    df = df.drop('bullets', axis=1)

    # Create address column
    state_dict={ 
        1:"Schleswig-Holstein",
        2:"Hamburg",
        3:"Niedersachsen",
        4:"Bremen",
        5:"Nordrhein-Westfalen",
        6:"Hessen",
        7:"Rheinland-Pfalz",
        8:"Baden-Württemberg",
        9:"Bayern",
        10:"Saarland",
        11:"Berlin",
        12:"Brandenburg",
        13:"Mecklenburg-Vorpommern",
        14:"Sachsen",
        15:"Sachsen-Anhalt",
        16:"Thüringen"
    }
    df['state'] = df['state'].map(state_dict)
    df['address'] = df['city'] + ', ' + df['state'] + ', ' + 'Germany'
    return df

def geocode_address(address):
    ''' Converts address to geocode dictionary '''
    API_KEY =  os.environ['GMAPS_API_KEY']
    params = {
        'key': API_KEY,
        'address': address,
    }

    base_url = 'https://maps.googleapis.com/maps/api/geocode/json?'

    response = requests.get(base_url, params=params).json()

    if response['status'] == 'OK':
        results_dict = response['results'][0]   # dict_keys(['address_components', 'formatted_address', 'geometry', 'place_id', 'types'])
    else:
        print('Response status FAILED')

    return results_dict

df = combine_files('downloads')
df.to_csv('data/combined_data.csv')
df = clean_data(df)
df.to_csv('data/cleaned_data.csv')

# address = df['address'][0]

# # create dict for address to geo_obj #TODO geoencode all addresses (apply dict to address col)
# address_input = df['address'].unique()[1:5]
# geocode_output = list(map(geocode_address, address_input))
# geo_dict = dict(zip(address_input, geocode_output))



# results_dict['address_components']
# results_dict['formatted_address']
# results_dict['geometry']
