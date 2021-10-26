import flask
from flask import Flask
from flask import request
import pandas as pd
from E_predictor_api import make_prediction

app = Flask(__name__)


@app.route('/', methods=["GET", "POST"])
def predict():  # todo: try to catch error
    if request.method == "POST":
        # create input data frame
        df = pd.DataFrame(data={
            'area': [request.form.get('area')],
            'rooms': [request.form.get('rooms')],
            'ebk': [request.form.get('ebk') == "1"],  # converts 1/0 to bools
            'garten': [request.form.get('garten') == "1"],
            'balkon': [request.form.get('balkon') == "1"],
            'inkl_NK': [request.form.get('inkl_NK') == "1"],
            'category': [request.form.get('category')],
            'GEN': [request.form.get('GEN')]
        })
        # Check if address is valid
        try:
            pred = make_prediction(df)
        except AttributeError:
            pred = "ERROR: Invalid address"

        return flask.render_template('index.html', pred=pred)
    else:
        return flask.render_template('index.html', pred="")


if __name__ == '__main__':
    app.run(debug=True)
