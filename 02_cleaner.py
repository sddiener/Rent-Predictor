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
        new_data = pd.read_csv(file, index_col=0)
        df = df.append(new_data, ignore_index=True)

    return df

df = combine_files('downloads')
df.to_csv('data/combined_data.csv')