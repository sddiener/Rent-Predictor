import numpy as np
import pandas as pd
import pickle as pkl
from sklearn.linear_model import LinearRegression, RidgeCV
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def load_data(path):
    """ Load relevant columns as pandas dataframe. """
    with open(path, 'rb') as f:
        gdf = pkl.load(f)

    columns = ['price', 'log_price', 'area', 'rooms', 'ebk',
               'garten', 'balkon', 'inkl_NK', 'category', 'GEN']
    data = pd.DataFrame(data=gdf[columns])

    return data


def scale_and_onehot_encode(data):
    """ Scales numeric data and one-hot encodes categorical data. """
    transformer = ColumnTransformer(transformers=[
        ('onehot', OneHotEncoder(), ['ebk', 'garten', 'balkon', 'inkl_NK', 'category', 'GEN']),
        ('scale', StandardScaler(), ['area', 'rooms'])
    ], remainder='passthrough')

    # Transform the features
    X = transformer.fit_transform(data.iloc[:, 1:])
    y = data.iloc[:, 0]
    return X, y


def print_errors(y_pred, y_true):
    """ Calculate and print MAE, RMSE and R2 errors. """
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)

    mae = round(mae, 2)
    rmse = round(rmse, 2)
    r2 = round(r2, 3)

    print("MAE: {}".format(mae))
    print("RMSE: {}".format(rmse))
    print("R2: {}".format(r2))


if __name__ == '__main__':
    data = load_data('data/geo_data.pkl')

    # Preprocessing
    X, y = scale_and_onehot_encode(data)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)

    # Train Linear Regression
    print("Training OLS..")

    model_ols = LinearRegression()
    model_ols = model_ols.fit(X_train, y_train)
    y_pred_ols = model_ols.predict(X_test)

    print_errors(y_pred_ols, y_test)

    # Train Linear Regression
    print("Training Ridge..")
    model_ridge = RidgeCV(alphas=(0.1, 1, 3, 5, 7, 10), store_cv_values=True)  # leave one out cv
    model_ridge = model_ridge.fit(X_train, y_train)

    print("alpha: {}".format(model_ridge.alphas))
    print("rmse: ".format(model_ridge.cv_values_.mean(axis=0).sqrt().round(2)))

    y_pred_ridge = model_ridge.predict(X_test)
    print_errors(y_pred_ridge, y_test)

    # Train Random Forest
    