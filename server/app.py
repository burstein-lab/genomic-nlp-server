import json
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd

from coords import Point


# configuration
DEBUG = True

# TODO(#38)
X_MAX, Y_MAX, X_MIN, Y_MIN = 14.375574111938477, 20.35647964477539, - \
    12.750589370727539, -5.537705898284912


def normalize(value, value_min, value_max):
    return (value - value_min) / (value_max - value_min)
    # return a * (a_max - a_min) + a_min


def df_coord_to_map(x, y):
    zoom_factor = 1024  # zoom split factor times pixels per tile.
    return normalize(x, X_MIN, X_MAX) * zoom_factor, normalize(y, Y_MAX, Y_MIN) * -zoom_factor


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


@app.route('/points')
def points():
    result = {}
    features = []
    zoom = int(request.args.get("z"))
    tile_x = request.args.get("x")
    tile_y = request.args.get("y")
    # print(z, x, y, os.path.isfile(f"../web/src/assets/map/{z}/space_by_label_{x}_{y}.pkl"))
    # for i in range(1000):
    #     features.append(Point(i / 10, i / 10, str(i)).todict())

    result["exists"] = {
        "z": zoom,
        "x": tile_x,
        "y": tile_y,
        "exists": os.path.isfile(f"web/src/assets/map/{zoom}/space_by_label_{tile_x}_{tile_y}.pkl"),
    }

    path = f"web/src/assets/map/{zoom}/space_by_label_{tile_x}_{tile_y}.pkl"
    if os.path.isfile(path):
        df = pd.read_pickle(path)
        for i, r in df.iterrows():
            x_coord, y_coord = df_coord_to_map(r["x"], r["y"])
            features.append(
                Point(x_coord, y_coord, f"{zoom},{tile_x},{tile_y}<br />{x_coord},{y_coord}").todict())

    result["features"] = features
    return json.dumps(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
