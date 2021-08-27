import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import pickle as pkl
import numpy as np
from scipy import stats
import seaborn as sns

PLOT_DIR = 'plots/'


def create_histograms(df):
    """ Creates histogram of 6 key variables. """
    fig, axs = plt.subplots(nrows=3, ncols=2, figsize=(8, 10))

    # Continious Variables
    sns.distplot(ax=axs[0, 0], a=df['price'], hist=True, kde=False, label='Price in €')
    sns.distplot(ax=axs[0, 1], a=df['log_price'], hist=True, kde=False, label='log Price')
    sns.distplot(ax=axs[1, 0], a=df['area'], hist=True, kde=False, label='Area in m²')
    sns.distplot(ax=axs[1, 1], a=df['rooms'], hist=True, kde=False, label='Nr of Rooms')

    # Dummies
    names = ['First Use', 'Garden', 'Balcony', 'Incl. add. Costs']
    total_count = [df.shape[0]] * 4
    true_count = df[['ebk', 'garten', 'balkon', 'inkl_NK']].sum()

    sns.barplot(ax=axs[2, 0], x=names, y=total_count, color='skyblue')
    sns.barplot(ax=axs[2, 0], x=names, y=true_count, color='green')
    axs[2, 0].tick_params(axis='x', rotation=90)
    axs[2, 0].set_ylabel('')

    # Categories
    sns.countplot(ax=axs[2, 1], x=df['category'], color='skyblue')
    axs[2, 1].tick_params(axis='x', rotation=90)
    axs[2, 1].set_ylabel('')
    axs[2, 1].set_xlabel('')

    # States
    # sns.countplot(ax=axs[2, 1], x=df['state'])
    # axs[2, 1].tick_params(axis='x', rotation=90)
    # axs[2, 1].set_ylabel('')
    # axs[2, 1].set_xlabel('')

    # Layout
    fig.suptitle('Histograms of Variables', size='larger')
    fig.supylabel('Nr. of Observations in Data')
    fig.tight_layout()

    # Save
    plt.savefig(PLOT_DIR+'data_histograms')
    print("Saved Histograms")


def create_scatterplot(df):
    """ Creates scatterplot of longitude and latitude values. """
    # Plot
    df.plot(kind='scatter', x='lng', y='lat', alpha=1, figsize=(8, 10), s=2)
    plt.title('Datapoints Scatterplot')

    # Save
    plt.savefig(PLOT_DIR+'data_points')
    print("Saved Scatterplots")


def create_coropleth(gdf):
    """ Aggregates on county level and creates coropleth map. """
    print("Aggregate data")
    gdf_diss = gdf.dissolve(by='GEN', aggfunc='mean')

    fig, ax = plt.subplots(1, 1, figsize=(8, 10))
    gdf_diss.plot(column='price', ax=ax, legend=True, cmap=plt.get_cmap('Spectral_r'),
                  legend_kwds={'label': 'Avg. Price in €'})
    plt.title('Average Rent Price per County')
    plt.savefig(PLOT_DIR+'prices_per_county')
    print("Saved Coropleth map")


if __name__ == '__main__':
    # Load data
    with open('data/geo_data.pkl', 'rb') as f:
        gdf = pkl.load(f)

    # Create plots
    create_histograms(gdf)
    create_scatterplot(gdf)
    create_coropleth(gdf)
