import pickle
import math
import re

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np

from common import df_to_features, df_coord_to_latlng, ModelData, TILE_SIZE, spaces_df_to_features


# configuration
DEBUG = True

HEAD_LIMIT = 50
MAX_ZOOM = 8
ZOOM_TILE_SPLIT_FACTOR = 4

MODEL_DATA = ModelData()
LABEL_TO_WORD = pd.DataFrame.from_dict(
    pd.read_pickle("label_to_word.pkl").keys(),
)
LABEL_TO_WORD.columns = ["label"]

with open("gene_names_to_ko.pkl", "rb") as o:
    G2KO = pd.DataFrame(pickle.load(o).items(), columns=["name", "ko"])


# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})


# sanity check route
@app.route("/ping", methods=["GET"])
def ping_pong():
    return jsonify("pong!")


def calc_center(spaces):
    lat, lng = df_coord_to_latlng(
        calc_middle_value(spaces.y),
        calc_middle_value(spaces.x),
        MODEL_DATA,
    )
    return {"lat": lat, "lng": lng}


def calc_middle_value(column):
    return (column.max() + column.min()) / 2.0


def calc_zoom(spaces):
    min_y, min_x = df_coord_to_latlng(
        spaces.y.min(),
        spaces.x.min(),
        MODEL_DATA,
    )
    max_y, max_x = df_coord_to_latlng(
        spaces.y.max(),
        spaces.x.max(),
        MODEL_DATA,
    )
    print(max_y, min_y, max_x, min_x)
    gap = max(max_y - min_y, max_x - min_x)
    if gap == 0 or np.isnan(gap):
        return MAX_ZOOM

    return min(math.floor(math.log2(TILE_SIZE) - math.log2(gap)), MAX_ZOOM)


@app.route("/<type_>/search")
def filter_by_space(type_):
    filter_ = request.args.get("filter")
    match type_:
        case "gene":
            return jsonify(search_g2ko(filter_))
        case "label":
            return jsonify(search(LABEL_TO_WORD, "label", filter_))
        case "space":
            return jsonify(search(MODEL_DATA.df, "KO", filter_) + search(MODEL_DATA.df, "word", filter_))
        case _:
            return jsonify(search(MODEL_DATA.df, type_, filter_))


@app.route("/space/get/<name>")
def space_get(name):
    spaces = []
    if name.lower().startswith("ko") and "." not in name:
        spaces = MODEL_DATA.df[MODEL_DATA.df["KO"].str.match(name)]

    else:
        spaces = MODEL_DATA.df[MODEL_DATA.df["word"].str.match(name)]

    return spaces_df_to_features(spaces)


@app.route("/label/get/<label>")
def filter_by_label(label):
    return spaces_df_to_features(MODEL_DATA.df[MODEL_DATA.df["label"] == label])


@app.route("/gene/get/<name>")
def filter_by_gene(name):
    df = G2KO.dropna()
    # pylint: disable=unsubscriptable-object
    g2ko_spaces = df[df["name"].str.match(name)]
    spaces = MODEL_DATA.df[MODEL_DATA.df["KO"].isin(g2ko_spaces["ko"])]
    return spaces_df_to_features(spaces)


@app.route("/word/get/<label>")
def filter_by_word(label):
    notna_df = MODEL_DATA.df.dropna(subset=["word"])
    return spaces_df_to_features(notna_df[notna_df["word"].str.match(label.replace(",", "|"))])


@app.route("/plot/scatter/<word>")
def plot_scatter(word):
    word_data = MODEL_DATA.df[MODEL_DATA.df['word'] == word]
    pred_df = pd.DataFrame(word_data['prediction_summary'].values[0].items(), columns=[
                           'class', 'score']).sort_values(by='score', ascending=False).reset_index(drop=True)

    my_range = range(1, len(pred_df.index)+1)
    data = []
    my_range = list(my_range)
    for i, value in enumerate(pred_df['score'].values):
        data.append({
            "x": my_range[i],
            "y": math.log(value),
        })

    return jsonify(
        {
            "label": f"Word: {word}, Hypothetical: {word_data['hypothetical'].values[0]}, Significant: {word_data['significant'].values[0]}",
            "data": data,
            "ticks": list(pred_df["class"].values),
        }
    )


def search_g2ko(filter_: str):
    notna_column = G2KO["name"].dropna()
    result = notna_column[notna_column.str.contains(
        filter_.replace(",", "|"), flags=re.IGNORECASE, na=False)].head(HEAD_LIMIT)

    return sorted(list(set(result)))


def search(df, column, filter_: str):
    if column == "ko":
        column = "KO"

    notna_column = df[column].dropna()
    notna_column.sort_values(inplace=True)
    result = notna_column[notna_column.str.contains(
        filter_.replace(",", "|"), flags=re.IGNORECASE, na=False)].head(HEAD_LIMIT)

    return sorted(list(set(result)))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
