import os
import pickle
import json
import math
import re
import subprocess

from flask import Flask, jsonify, request
import numpy as np
from flask_cors import CORS
from gensim.models import word2vec as w2v
import pandas as pd
from google.cloud import storage

from coords import Point


# configuration
DEBUG = True

HEAD_LIMIT = 50
MAX_TILE_SIZE = 1024
MAX_ZOOM = 5
ZOOM_TILE_SPLIT_FACTOR = 4

if not os.path.isfile("model_data.pkl"):
    storage_client = storage.Client()
    with open("model_data.pkl", "wb") as f:
        storage_client.download_blob_to_file(
            "gs://gnlp-public-assets/data/model_data.pkl", f)

if not os.path.isfile("gene_names_to_ko.pkl"):
    storage_client = storage.Client()
    with open("gene_names_to_ko.pkl", "wb") as f:
        storage_client.download_blob_to_file(
            "gs://gnlp-public-assets/data/gene_names_to_ko.pkl", f)

if not os.path.isfile("label_to_word.pkl"):
    storage_client = storage.Client()
    with open("label_to_word.pkl", "wb") as f:
        storage_client.download_blob_to_file(
            "gs://gnlp-public-assets/data/label_to_word.pkl", f)

if not os.path.isfile("gene2vec_w5_v300_tf24_annotation_extended_2021-10-03.w2v"):
    storage_client = storage.Client()
    with open("gene2vec_w5_v300_tf24_annotation_extended_2021-10-03.w2v", "wb") as f:
        storage_client.download_blob_to_file(
            "gs://gnlp-public-assets/data/embeddings/gene2vec_w5_v300_tf24_annotation_extended_2021-10-03.w2v", f)
    with open("gene2vec_w5_v300_tf24_annotation_extended_2021-10-03.w2v.trainables.syn1neg.npy", "wb") as f:
        storage_client.download_blob_to_file(
            "gs://gnlp-public-assets/data/embeddings/gene2vec_w5_v300_tf24_annotation_extended_2021-10-03.w2v.trainables.syn1neg.npy", f)
    with open("gene2vec_w5_v300_tf24_annotation_extended_2021-10-03.w2v.wv.vectors.npy", "wb") as f:
        storage_client.download_blob_to_file(
            "gs://gnlp-public-assets/data/embeddings/gene2vec_w5_v300_tf24_annotation_extended_2021-10-03.w2v.wv.vectors.npy", f)

DF = pd.read_pickle("model_data.pkl")
LABEL_TO_WORD = pd.read_pickle("label_to_word.pkl")
MDL = w2v.Word2Vec.load(
    "gene2vec_w5_v300_tf24_annotation_extended_2021-10-03.w2v")

with open("gene_names_to_ko.pkl", "rb") as o:
    G2KO = pd.DataFrame(pickle.load(o).items(), columns=["name", "ko"])

X_MAX, Y_MAX, X_MIN, Y_MIN = DF.x.max(), DF.y.max(), DF.x.min(), DF.y.min()


def normalize(value, value_min, value_max):
    return (value - value_min) / (value_max - value_min)


def df_coord_to_latlng(y_value, x_value):
    return normalize(y_value, Y_MAX, Y_MIN) * -MAX_TILE_SIZE, normalize(x_value, X_MIN, X_MAX) * MAX_TILE_SIZE
    return -(MAX_TILE_SIZE - (normalize(y_value, Y_MAX, Y_MIN) * MAX_TILE_SIZE)), normalize(x_value, X_MIN, X_MAX) * MAX_TILE_SIZE


# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})


@ app.route("/hello")
def hello():
    return "Hello world!"


# sanity check route
@ app.route("/ping", methods=["GET"])
def ping_pong():
    return jsonify("pong!")


@ app.route("/points")
def points():
    result = {}
    zoom = int(request.args.get("z"))
    tile_x = request.args.get("x")
    tile_y = request.args.get("y")

    result["exists"] = {
        "z": zoom,
        "x": tile_x,
        "y": tile_y,
        "exists": os.path.isfile(f"../web/public/map/{zoom}/space_by_label_{tile_x}_{tile_y}.pkl"),
    }

    df = None
    path = f"../web/public/map/{zoom}/space_by_label_{tile_x}_{tile_y}.pkl"
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
            Point(row.Index, x_coord, y_coord, {"name": f"{x_coord},{y_coord}", "word": row.word}).todict())

    return features


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


@app.route("/<type_>/search")
def filter_by_space(type_):
    filter_ = request.args.get("filter")
    match type_:
        case "gene":
            return jsonify(search_g2ko(filter_))
        case "label":
            if filter_ == "":
                return jsonify(list(LABEL_TO_WORD.keys())[:HEAD_LIMIT])

            return jsonify(sorted(LABEL_TO_WORD[filter_]))
        case "space":
            return jsonify(search("KO", filter_) + search("word", filter_))
        case _:
            return jsonify(search(type_, filter_))


@app.route("/space/get/<name>")
def space_get(name):
    spaces = []
    if name.lower().startswith("ko") and "." not in name:
        spaces = DF[DF["KO"].str.match(name)]

    else:
        spaces = DF[DF["word"].str.match(name)]

    return spaces_df_to_features(spaces)


@app.route("/label/get/<label>")
def filter_by_label(label):
    return spaces_df_to_features(DF[DF["label"] == label])


@app.route("/neighbors/get/<label>")
def filter_by_neighbors(label):
    k = json.loads(request.args.get("k"))
    top_k = [similar for similar, _ in MDL.wv.most_similar(label, topn=k)]
    df = DF[DF["word"].isin(top_k)]
    return spaces_df_to_features(df)


@app.route("/gene/get/<name>")
def filter_by_gene(name):
    df = G2KO.dropna()
    g2ko_spaces = df[df["name"].str.match(name)]
    spaces = DF[DF["KO"].isin(g2ko_spaces["ko"])]
    return spaces_df_to_features(spaces)


@app.route("/word/get/<label>")
def filter_by_word(label):
    notna_df = DF.dropna(subset=["word"])
    return spaces_df_to_features(notna_df[notna_df["word"].str.match(label.replace(",", "|"))])


@app.route("/plot/bar/<word>")
def plot_bar(word):
    top_k_df = pd.DataFrame(MDL.wv.most_similar(
        word, topn=10), columns=["word", "distance"])

    return jsonify(
        {
            "x": top_k_df["word"].tolist(),
            "y": top_k_df["distance"].tolist(),
        }
    )


@app.route("/plot/scatter/<word>")
def plot_scatter(word):
    word_data = DF[DF['word'] == word]
    pred_df = pd.DataFrame(word_data['prediction_summary'].values[0].items(), columns=[
                           'class', 'score']).sort_values(by='score', ascending=False).reset_index(drop=True)

    my_range = range(1, len(pred_df.index)+1)
    # my_size = np.where(pred_df.index == 0, 80, 50)
    # my_color=np.where(pred_df.index == 0, 'orange', 'skyblue')
    #plt.vlines(x=my_range, ymin=0, ymax=pred_df['score'], color=my_color, alpha=0.4)
    #sns.scatterplot(x=list(my_range),y=pred_df['score'].values, alpha=1,c=my_color, s=my_size)
    # plt.yscale('log')

    #plt.xticks(my_range, pred_df['class'])
    #plt.title(f"Word: w, hypothetical: {word_data['hypothetical'].values[0]} Significant: {word_data['significant'].values[0]}", loc='left')
    #plt.ylabel('Prediction Score')
    #_ = plt.xticks(rotation=90)

    data = []
    my_range = list(my_range)
    for i, v in enumerate(pred_df['score'].values):
        data.append({
            "x": my_range[i],
            "y": math.log(v),
        })

    return jsonify(
        {
            "label": f"Word: {word}, Hypothetical: {word_data['hypothetical'].values[0]}, Significant: {word_data['significant'].values[0]}",
            "data": data,
        }
    )


def search_g2ko(filter_: str):
    notna_column = G2KO["name"].dropna()
    result = notna_column[notna_column.str.contains(
        filter_.replace(",", "|"), flags=re.IGNORECASE, na=False)].head(HEAD_LIMIT)

    return sorted(list(set(result)))


def search(column, filter_: str):
    if column == "ko":
        column = "KO"

    notna_column = DF[column].dropna()
    notna_column.sort_values(inplace=True)
    result = notna_column[notna_column.str.contains(
        filter_.replace(",", "|"), flags=re.IGNORECASE, na=False)].head(HEAD_LIMIT)

    return sorted(list(set(result)))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
