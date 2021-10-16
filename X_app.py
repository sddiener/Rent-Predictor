import flask
from flask import Flask
from flask import request
import pandas as pd
from E_predictor_api import make_prediction

app = Flask(__name__)


@app.route('/', methods=["GET", "POST"])
def predict():
    # print(request.method)
    if request.method == "POST":  # create input data frame
        df = pd.DataFrame(data={
            'area': [request.form.get('area')],
            'rooms': [request.form.get('rooms')],
            'ebk': [bool(request.form.get('ebk'))],  # convert 1/0 to bool
            'garten': [bool(request.form.get('garten'))],  # convert 1/0 to bool
            'balkon': [bool(request.form.get('balkon'))],  # convert 1/0 to bool
            'inkl_NK': [bool(request.form.get('inkl_NK'))],  # convert 1/0 to bool
            'category': [request.form.get('category')],
            'GEN': [request.form.get('GEN')]
        })
        print("Input data frame (not working) \n{}".format(df))  # >>> TODO: BOOLS instead of 0/1

        pred = make_prediction(df)
        # print("Prediction: {}".format(pred))
        return flask.render_template('predictor.html',
                                     tables=[df.to_html(classes='data', header="true")],
                                     pred=pred)
    else:
        return flask.render_template('predictor.html', inputs="no input", pred="no prediction")


if __name__ == '__main__':
    app.run(debug=True)
