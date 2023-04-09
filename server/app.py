import os
import pickle
import json
import math
import re

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from google.cloud import storage

from common import df_to_features, df_coord_to_latlng, TILE_SIZE


# configuration
DEBUG = True

HEAD_LIMIT = 50
MAX_ZOOM = 8
ZOOM_TILE_SPLIT_FACTOR = 4

if not os.path.isfile("model_data.pkl"):
    storage_client = storage.Client(project="genomic-nlp")
    with open("model_data.pkl", "wb") as f:
        storage_client.download_blob_to_file(
            "gs://gnlp.bursteinlab.org/data/model_data.pkl", f)

if not os.path.isfile("gene_names_to_ko.pkl"):
    storage_client = storage.Client(project="genomic-nlp")
    with open("gene_names_to_ko.pkl", "wb") as f:
        storage_client.download_blob_to_file(
            "gs://gnlp.bursteinlab.org/data/gene_names_to_ko.pkl", f)

if not os.path.isfile("label_to_word.pkl"):
    storage_client = storage.Client(project="genomic-nlp")
    with open("label_to_word.pkl", "wb") as f:
        storage_client.download_blob_to_file(
            "gs://gnlp.bursteinlab.org/data/label_to_word.pkl", f)

if not os.path.isfile("gene2vec_w5_v300_tf24_annotation_extended_2021-10-03.w2v"):
    storage_client = storage.Client(project="genomic-nlp")
    with open("gene2vec_w5_v300_tf24_annotation_extended_2021-10-03.w2v", "wb") as f:
        storage_client.download_blob_to_file(
            "gs://gnlp.bursteinlab.org/data/embeddings/gene2vec_w5_v300_tf24_annotation_extended_2021-10-03.w2v", f)
    with open("gene2vec_w5_v300_tf24_annotation_extended_2021-10-03.w2v.trainables.syn1neg.npy", "wb") as f:
        storage_client.download_blob_to_file(
            "gs://gnlp.bursteinlab.org/data/embeddings/gene2vec_w5_v300_tf24_annotation_extended_2021-10-03.w2v.trainables.syn1neg.npy", f)
    with open("gene2vec_w5_v300_tf24_annotation_extended_2021-10-03.w2v.wv.vectors.npy", "wb") as f:
        storage_client.download_blob_to_file(
            "gs://gnlp.bursteinlab.org/data/embeddings/gene2vec_w5_v300_tf24_annotation_extended_2021-10-03.w2v.wv.vectors.npy", f)

DF = pd.read_pickle("model_data.pkl")
LABEL_TO_WORD = pd.DataFrame.from_dict(
    pd.read_pickle("label_to_word.pkl").keys(),
)
LABEL_TO_WORD.columns = ["label"]

with open("gene_names_to_ko.pkl", "rb") as o:
    G2KO = pd.DataFrame(pickle.load(o).items(), columns=["name", "ko"])

X_MAX, Y_MAX, X_MIN, Y_MIN = DF.x.max(), DF.y.max(), DF.x.min(), DF.y.min()


# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})


# sanity check route
@app.route("/ping", methods=["GET"])
def ping_pong():
    return jsonify("pong!")


def spaces_df_to_features(spaces):
    return jsonify(
        {
            "spaces": df_to_features(spaces, Y_MIN, Y_MAX, X_MIN, X_MAX),
            "latlng": calc_center(spaces),
            "zoom": calc_zoom(spaces),
        },
    )


def calc_center(spaces):
    lat, lng = df_coord_to_latlng(
        calc_middle_value(spaces.y),
        calc_middle_value(spaces.x),
        Y_MIN,
        Y_MAX,
        X_MIN,
        X_MAX,
    )
    return {"lat": lat, "lng": lng}


def calc_middle_value(column):
    return (column.max() + column.min()) / 2.0


def calc_zoom(spaces):
    min_y, min_x = df_coord_to_latlng(
        spaces.y.min(),
        spaces.x.min(),
        Y_MIN,
        Y_MAX,
        X_MIN,
        X_MAX,
    )
    max_y, max_x = df_coord_to_latlng(
        spaces.y.max(),
        spaces.x.max(),
        Y_MIN,
        Y_MAX,
        X_MIN,
        X_MAX,
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
            return jsonify(search(DF, "KO", filter_) + search(DF, "word", filter_))
        case _:
            return jsonify(search(DF, type_, filter_))


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
    topn = json.loads(request.args.get("k"))
    top_k = [similar for similar, _ in MDL.wv.most_similar(label, topn=topn)]
    df = DF[DF["word"].isin(top_k)]
    return spaces_df_to_features(df)


@app.route("/gene/get/<name>")
def filter_by_gene(name):
    df = G2KO.dropna()
    # pylint: disable=unsubscriptable-object
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
