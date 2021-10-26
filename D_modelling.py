from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import pickle as pkl
from sklearn.model_selection import RandomizedSearchCV
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from xgboost import XGBRegressor
import seaborn as sns


def load_data(path):
    """ Load relevant columns as pandas dataframe. """
    with open(path, 'rb') as f:
        gdf = pkl.load(f)

    columns = ['price', 'area', 'rooms', 'ebk', 'garten', 'balkon', 'inkl_NK', 'category', 'GEN']
    data = pd.DataFrame(data=gdf[columns])

    return data


def scale_and_onehot_encode(data):
    """ Scales numeric data and one-hot encodes categorical data. """
    transformer = ColumnTransformer(transformers=[
        ('onehot', OneHotEncoder(), ['ebk', 'garten', 'balkon', 'inkl_NK', 'category', 'GEN']),
        ('scale', StandardScaler(), ['area', 'rooms'])
    ], remainder='passthrough')

    # Transform the features
    transformer.fit(data.iloc[:, 1:])  # fit transformer to training set
    X = transformer.transform(data.iloc[:, 1:])  # transform the data
    y = data.iloc[:, 0]
    return X, y, transformer


def eval_model(model, X_test, y_test, p=True):
    """ Calculate and print MAE, RMSE and R2 errors. """
    # make predictions
    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    model_name = type(model).__name__
    mae = round(mae, 2)
    rmse = round(rmse, 2)
    r2 = round(r2, 3)

    if p:
        print("Model name: {}".format(model_name))
        print("MAE: {}".format(mae))
        print("RMSE: {}".format(rmse))
        print("R2: {}".format(r2))

    return [model_name, mae, rmse, r2]


def save_and_plot_evaluation(model_paths, X_test, y_test):
    """ Loads and evaluates every model and create evaluation dataframe and visualization """
    eval_df = pd.DataFrame(columns=['model', 'MAE', 'RMSE', 'R2'])

    for i, path in enumerate(model_paths):
        # open model
        with open(path, 'rb') as f:
            model = pkl.load(f)

        # append eval to df
        row = eval_model(model, X_test, y_test, p=False)
        eval_df.loc[i, :] = row

    # save df
    eval_df.to_csv('models/evaluation_df.csv')

    eval_df_long = eval_df.melt(id_vars='model')

    # plot df
    ax = sns.barplot(data=eval_df_long, x='model', y='value', hue='variable', palette=sns.color_palette("Set2"))
    for container in ax.containers:
        ax.bar_label(container)
    sns.move_legend(ax, "lower center", bbox_to_anchor=(.5, 1), ncol=3, title=None, frameon=False)
    # plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig('plots/eval_df.png')

    return eval_df


def search_best_model(model, params, X_train, y_train, n_iter, cv, verbose=0):
    """ Finds best model hyperparameters and retrains on all data. """
    # fit the grid search
    print("\nRandom Search {}...".format(model))
    grid = RandomizedSearchCV(model, params, cv=cv, n_iter=n_iter, n_jobs=-1, verbose=verbose)
    grid.fit(X_train, y_train)

    # retrain best estimator
    print('Best model: {}'.format(grid.best_estimator_))
    best_model = grid.best_estimator_
    best_model.fit(X_train, y_train)

    return best_model


if __name__ == '__main__':
    data = load_data('data/geo_data.pkl')

    # Preprocessing
    X, y, transformer = scale_and_onehot_encode(data)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)

    with open('models/transformer.pkl', 'wb') as f:
        pkl.dump(transformer, f)

    # Train Linear Regression
    print("Training OLS...")
    model_ols = LinearRegression()
    model_ols = model_ols.fit(X_train, y_train)
    eval_model(model_ols, X_test, y_test)

    with open('models/ols.pkl', 'wb') as f:
        pkl.dump(model_ols, f)

    # Train Ridge Regression
    params_ridge = {'alpha': [int(x) for x in np.linspace(0.01, 20, num=20)]}
    model_ridge = search_best_model(Ridge(), params_ridge, X_train, y_train, n_iter=50, cv=5)
    eval_model(model_ridge, X_test, y_test)

    with open('models/ridge.pkl', 'wb') as f:
        pkl.dump(model_ridge, f)

    # Train Random Forest
    params_rf = {
        'bootstrap': [True, False],  # Method of selecting samples for training each tree
        'max_depth': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, None],  # Max nr of levels in tree
        'max_features': ['auto', 'sqrt'],  # Number of features to consider at every split
        'min_samples_leaf': [1, 2, 4],  # Min. nr of samples required at each leaf node
        'min_samples_split': [2, 5, 10, 15],  # Min. nr of samples required to split a node
        'n_estimators': [200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000]}  # Nr trees

    model_rf = search_best_model(RandomForestRegressor(), params_rf,
                                 X_train, y_train, n_iter=100, cv=3, verbose=1)
    eval_model(model_rf, X_test, y_test)

    with open('models/randomforest.pkl', 'wb') as f:
        pkl.dump(model_rf, f)

    # Train XGB
    params_xgb = {
        'objective': ['reg:squarederror'],
        'booster': ['gbtree', 'gblinear'],
        'learning_rate': [0.1],
        'max_depth': [7, 10, 15, 20],
        'subsample': [0.6, 0.8, 1.0],
        'min_child_weight': [10, 15, 20, 25],
        'colsample_bytree': [0.8, 0.9, 1],
        'n_estimators': [300, 500, 700, 1000, 1500, 2000],
        "reg_alpha": [0.1, 0.5, 0.2, 1],
        "reg_lambda": [2, 3, 5],
        "gamma": [0, 1, 2, 3]}

    model_xgb = search_best_model(XGBRegressor(),
                                  params_xgb, X_train, y_train, n_iter=200, cv=5, verbose=0)
    eval_model(model_xgb, X_test, y_test)

    with open('models/xgb.pkl', 'wb') as f:
        pkl.dump(model_xgb, f)

    # Train SVM
    params_svm = {'kernel': ('linear', 'rbf'),
                  'C': [1, 10, 100]}

    model_svm = search_best_model(SVR(), params_svm, X_train, y_train, n_iter=6, cv=5, verbose=1)
    eval_model(model_svm, X_test, y_test)

    with open('models/svm.pkl', 'wb') as f:
        pkl.dump(model_svm, f)

    # Save model evaluations
    model_paths = ['models/ols.pkl', 'models/ridge.pkl', 'models/randomforest.pkl', 'models/svm.pkl', 'models/xgb.pkl']
    save_and_plot_evaluation(model_paths, X_test, y_test)
