import pickle as pkl
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

PLOT_DIR = 'plots/'


def create_histograms(df):
    """ Creates histogram of 6 key variables. """

    # Create logs of variables
    df['log_price'] = np.log(df['price'])
    df['log_area'] = np.log(df['area'])
    df['log_rooms'] = np.log(df['rooms'])

    # Plot
    fig, axs = plt.subplots(nrows=3, ncols=3, figsize=(12, 12))

    # Continious Variables
    sns.histplot(ax=axs[0, 0], data=df['price'], kde=False, label='Price in €')
    sns.histplot(ax=axs[1, 0], data=df['log_price'], kde=False, label='log Price')
    sns.histplot(ax=axs[0, 1], data=df['area'], kde=False, label='Area in m²')
    sns.histplot(ax=axs[1, 1], data=df['log_area'], kde=False, label='Area in m²')
    sns.histplot(ax=axs[0, 2], data=df['rooms'], kde=False, label='Nr of Rooms')
    axs[0, 2].set_xlim([0, 10])
    sns.histplot(ax=axs[1, 2], data=df['log_rooms'], kde=False, label='Nr of Rooms')

    # Dummies
    names = ['First Use', 'Garden', 'Balcony', 'Incl. add. Costs']
    total_count = [df.shape[0]] * 4
    true_count = df[['ebk', 'garten', 'balkon', 'inkl_NK']].sum()

    sns.barplot(ax=axs[2, 0], x=names, y=total_count, color='skyblue')
    sns.barplot(ax=axs[2, 0], x=names, y=true_count, color='green')
    axs[2, 0].tick_params(axis='x', rotation=90)
    axs[2, 0].set_xlabel('# of True values')

    # Categories
    sns.countplot(ax=axs[2, 1], x=df['category'], color='skyblue')
    axs[2, 1].tick_params(axis='x', rotation=90)

    # States
    sns.countplot(ax=axs[2, 2], x=df['state'])
    axs[2, 2].tick_params(axis='x', rotation=90)

    # Remove y_ticks
    for ax_row in axs:
        for ax in ax_row:
            ax.set_ylabel('')

    # Layout
    fig.suptitle('Histograms of Variables', fontsize=20)
    fig.supylabel('Nr. of Observations in Data')
    fig.tight_layout()

    # Save
    plt.savefig(PLOT_DIR+'data_histograms.png')
    print("Saved Histograms")


def create_scatterplot(df):
    """ Creates scatterplot of longitude and latitude values. """
    # Plot
    df.plot(kind='scatter', x='lng', y='lat', alpha=1, figsize=(8, 10), s=2)
    plt.title('Datapoints Scatterplot')

    # Save
    plt.savefig(PLOT_DIR+'data_points.png')
    print("Saved Scatterplots")


def create_coropleth(gdf):
    """ Aggregates on county level and creates coropleth map. """
    print("Aggregate data")
    gdf_diss = gdf.dissolve(by='GEN', aggfunc='mean')

    fig, ax = plt.subplots(1, 1, figsize=(8, 10))
    gdf_diss.plot(column='price', ax=ax, legend=True, cmap=plt.get_cmap('Spectral_r'),
                  legend_kwds={'label': 'Avg. Price in €'})
    plt.title('Average Rent Price per County')
    plt.savefig(PLOT_DIR+'prices_per_county.png')
    print("Saved Coropleth map")


if __name__ == '__main__':
    # Load data
    with open('data/geo_data.pkl', 'rb') as f:
        gdf = pkl.load(f)

    # Create plots
    create_histograms(gdf)
    create_scatterplot(gdf)
    create_coropleth(gdf)
