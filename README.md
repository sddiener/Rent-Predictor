# Rent Predictor

The Rent Predictor is a web app that uses machine learning to predict rents in Germany.

### **[Click here to try out the live demo!](https://immo-calculator.nw.r.appspot.com/)**

## Data Collection
The training data consists of ~49'000 apartment ads, which were scraped from the German real estate platform immonet.de.

<img src="plots/immonet_anzeige_annotated.png" width="700"/>

Each ad contains information about the aparment's:

1) Type
2) Approximate address
3) Availability of a garden, balcony, and existance of previous tenants (first use)
4) Price in € (inclusive or exclusive additional costs)
5) Are in m²
6) Nr of rooms

Cleaned data frame:

<img src="plots/data_head_cleaned.png" width="700" />

## Exploratory Data Analysis
### 1) Distribution of price and features:

<img src="plots/data_histograms.png" width="600" />

### 2) Spacial distribution of apartments:
Addresses were converted to longitude and latitude values using the google maps API, resulting in the following distribution.

<img src="plots/data_points.png" width="600"/>

### 3) Coropleth map of price per county:
Using a shapefile of all german counties, regional price differences can be illustrated graphically.
The high-price areas in the metropolitan centers of Berlin and Munich are clearly visible, as are the low-price areas in the eastern German states.

<img src="plots/prices_per_county.png" width="600"/>

## Modelling

After hyperparameter optimization, OLS showed to be the best performing model.

<img src="plots/eval_df.png" width="600"/>


## Deployment

The model was deployed using Google App Engine.

<img src="plots/app_interface.png" width="600"/>
