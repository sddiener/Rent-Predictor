import pandas as pd
import os


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
    # Convert id to float
    df['id'] = df['id'].str.replace('selObject_', '').astype(int)

    # Create dummies for tags
    df['EBK'] = df['tags'].apply(lambda x: 'EBK' in x)
    df['Garten'] = df['tags'].apply(lambda x: 'Garten' in x)
    df['Balkon'] = df['tags'].apply(lambda x: 'Balkon' in x)
    df = df.drop('tags', axis=1)

    # Clean price column
    df = df[df['price'].str.contains('zzgl.|inkl.')] # remove rows without these strings in price (i.e. "Preis auf Anfrage" and "Garagen")
    df['inkl_NK'] = df['price'].apply(lambda x: 'inkl.' in x) # create dummy if additional costs are included

    df['price'] = df['price'].str.extract('(\d[\d,.]*)') # extract numbers
    df['price'] = df['price'].str.replace('.','', regex=True) # remove thousands dot
    df['price'] = df['price'].str.replace(',','.').astype(float) # replace seperator and convert to float

    # Convert area to float
    df['area'] = df['area'].str.extract('(\d[\d,.]*)') # extract numbers
    df['area'] = df['area'].astype(float) 

    # Convert rooms to float
    df['rooms'] = df['rooms'].str.extract('(\d[\d,.]*)') # extract numbers
    df['rooms'] = df['rooms'].str.replace(',','.').astype(float) # replace seperator and convert to float

    # Split bullets
    df['bullets'] = df['bullets'].apply(lambda x: x[-1]) # extract numbers
    df['type'] = df['bullets'].apply(lambda x: x[0]) 
    df['location'] = df['bullets'].apply(lambda x: ' '.join(x[2:]))
    df = df.drop('bullets', axis=1)

    return df


df = combine_files('downloads')
df.to_csv('data/combined_data.csv')

df = clean_data(df)
df.to_csv('data/cleaned_data.csv')