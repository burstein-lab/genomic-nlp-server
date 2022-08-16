import os
import math
import re

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd

from coords import Point


# configuration
DEBUG = True

MAX_TILE_SIZE = 1024
MAX_ZOOM = 5
ZOOM_TILE_SPLIT_FACTOR = 4

DF = pd.read_pickle("model_data.pkl")
X_MAX, Y_MAX, X_MIN, Y_MIN = DF.x.max(), DF.y.max(), DF.x.min(), DF.y.min()


def normalize(value, value_min, value_max):
    return (value - value_min) / (value_max - value_min)


def df_coord_to_latlng(y_value, x_value):
    return normalize(y_value, Y_MAX, Y_MIN) * -MAX_TILE_SIZE, normalize(x_value, X_MIN, X_MAX) * MAX_TILE_SIZE


# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/hello')
def hello():
    return 'Hello world!'


# sanity check route
@app.route("/ping", methods=["GET"])
def ping_pong():
    return jsonify("pong!")


@app.route("/points")
def points():
    result = {}
    zoom = int(request.args.get("z"))
    tile_x = request.args.get("x")
    tile_y = request.args.get("y")

    result["exists"] = {
        "z": zoom,
        "x": tile_x,
        "y": tile_y,
        "exists": os.path.isfile(f"web/public/map/{zoom}/space_by_label_{tile_x}_{tile_y}.pkl"),
    }

    df = None
    path = f"web/public/map/{zoom}/space_by_label_{tile_x}_{tile_y}.pkl"
    if os.path.isfile(path):
        df = pd.read_pickle(path)

    return jsonify_features(df)


def jsonify_features(df):
    result = {
        "features": df_to_features(df),
    }
    return jsonify(result)


def df_to_features(df):
    features = []
    if df is None:
        return features

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

    return spaces_df_to_features(spaces)


def spaces_df_to_features(spaces):
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
def filter_by_space():
    filter_ = request.args.get("filter")
    return jsonify(search_df("KO", filter_) + search_df("word", filter_))


@app.route("/label/search")
def get_labels():
    filter_ = request.args.get("filter")
    return jsonify(search_df("label", filter_))


@app.route("/label/get/<label>")
def filter_by_label(label):
    return spaces_df_to_features(DF[DF["label"] == label])


def search_df(column, filter_):
    notna_column = DF[column].dropna()
    result = notna_column[notna_column.str.contains(
        filter_, flags=re.IGNORECASE, na=False)].head(50)
    return sorted(list(set(result)))


if __name__ == "__main__":
    app.run(host="0.0.0.0")
