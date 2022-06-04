import os
import re
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd

from coords import Point


# configuration
DEBUG = True

# TODO(#38)
X_MAX, Y_MAX, X_MIN, Y_MIN = 14.375574111938477, 20.35647964477539, - \
    12.750589370727539, -5.537705898284912


DF = pd.read_pickle("model_data.pkl")


def normalize(value, value_min, value_max):
    return (value - value_min) / (value_max - value_min)


def df_coord_to_map(x_value, y_value):
    tile_size = 1024
    return normalize(x_value, X_MIN, X_MAX) * tile_size, normalize(y_value, Y_MAX, Y_MIN) * -tile_size


# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/')
def hello():
    return 'Hello world!'


# sanity check route
@app.route("/ping", methods=["GET"])
def ping_pong():
    return jsonify("pong!")


@app.route("/points")
def points():
    result = {}
    features = []
    zoom = int(request.args.get("z"))
    tile_x = request.args.get("x")
    tile_y = request.args.get("y")

    result["exists"] = {
        "z": zoom,
        "x": tile_x,
        "y": tile_y,
        "exists": os.path.isfile(f"web/src/assets/map/{zoom}/space_by_label_{tile_x}_{tile_y}.pkl"),
    }

    path = f"web/src/assets/map/{zoom}/space_by_label_{tile_x}_{tile_y}.pkl"
    if os.path.isfile(path):
        tile_df = pd.read_pickle(path)
        for row in tile_df.itertuples():
            x_coord, y_coord = df_coord_to_map(row.x, row.y)
            features.append(
                Point(x_coord, y_coord, f"{zoom},{tile_x},{tile_y}<br />{x_coord},{y_coord}").todict())

    result["features"] = features
    return jsonify(result)


@app.route("/space/get/<name>")
def space_get(name):
    spaces = []
    if name.lower().startswith("ko") and "." not in name:
        spaces = DF[DF["KO"].str.match(name)]

    else:
        spaces = DF[DF["word"].str.match(name)]

    return spaces.to_json()


@app.route("/space/search")
def space_search():
    filter_ = request.args.get("filter")
    print(filter_)
    return jsonify(sorted(list(set(add_space("KO", filter_))) + list(add_space("word", filter_))))


def add_space(column, filter_):
    notna_column = DF[column].dropna()
    return notna_column[notna_column.str.contains(filter_, flags=re.IGNORECASE, na=False)].head(50)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
