import os
import math
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

MAX_TILE_SIZE = 1024
MAX_ZOOM = 5
ZOOM_TILE_SPLIT_FACTOR = 4


DF = pd.read_pickle("model_data.pkl")


def normalize(value, value_min, value_max):
    return (value - value_min) / (value_max - value_min)


def df_coord_to_latlng(y_value, x_value):
    return normalize(y_value, Y_MAX, Y_MIN) * -MAX_TILE_SIZE, normalize(x_value, X_MIN, X_MAX) * MAX_TILE_SIZE


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
        features = df_to_features(pd.read_pickle(path))

    result["features"] = features
    return jsonify(result)


def df_to_features(df):
    features = []
    for row in df.itertuples():
        y_coord, x_coord = df_coord_to_latlng(row.y, row.x)
        features.append(
            Point(x_coord, y_coord, f"{x_coord},{y_coord}").todict())

    return features


@app.route("/space/get/<name>")
def space_get(name):
    spaces = []
    if name.lower().startswith("ko") and "." not in name:
        spaces = DF[DF["KO"].str.match(name)]

    else:
        spaces = DF[DF["word"].str.match(name)]

    return jsonify(
        {
            "spaces": df_to_features(spaces),
            "latlng": calc_center(spaces),
            "zoom": calc_zoom(spaces),
        },
    )


def calc_center(spaces):
    lat, lng = df_coord_to_latlng(
        calc_middle_value(spaces.y),
        calc_middle_value(spaces.x),
    )
    return {"lat": lat, "lng": lng}


def calc_middle_value(column):
    return (column.max() + column.min()) / 2.0


def calc_zoom(spaces):
    min_y, min_x = df_coord_to_latlng(spaces.y.min(), spaces.x.min())
    max_y, max_x = df_coord_to_latlng(spaces.y.max(), spaces.x.max())
    gap = max(max_y - min_y, max_x - min_x)
    if gap == 0:
        return MAX_ZOOM

    return min(math.floor(math.log2(MAX_TILE_SIZE) - math.log2(gap)), MAX_ZOOM)


@app.route("/space/search")
def space_search():
    filter_ = request.args.get("filter")
    return jsonify(sorted(list(set(add_space("KO", filter_))) + list(add_space("word", filter_))))


def add_space(column, filter_):
    notna_column = DF[column].dropna()
    return notna_column[notna_column.str.contains(filter_, flags=re.IGNORECASE, na=False)].head(50)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
