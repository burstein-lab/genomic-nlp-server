import pickle
import math
import re
from urllib.parse import unquote_plus

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd

from common import ModelData, jsonify_spaces


PAGE_SIZE = 20

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


@app.route("/<type_>/search")
def filter_by_space(type_):
    page = int(request.args.get("page"))
    filter_ = unquote_plus(request.args.get("filter"))
    result = sorted(set(_filter_by_space(unquote_plus(type_), filter_)))
    return jsonify({
        "items": result[(page - 1) * PAGE_SIZE:page * PAGE_SIZE],
        "done": len(result) <= page * PAGE_SIZE,
    })


@app.route("/space/get/<name>")
def space_get(name):
    return jsonify_spaces(
        MODEL_DATA.df[MODEL_DATA.df["KO"].str.match(
            unquote_plus(name), na=False)],
        MODEL_DATA,
    )


@app.route("/label/get/<label>")
def filter_by_label(label):
    return jsonify_spaces(MODEL_DATA.df[MODEL_DATA.df["label"] == unquote_plus(label)], MODEL_DATA)


@app.route("/gene_product/get/<name>")
def filter_by_gene_product(name):
    return jsonify_spaces(MODEL_DATA.df[MODEL_DATA.df["gene_product"] == unquote_plus(name)], MODEL_DATA)


@app.route("/gene/get/<name>")
def filter_by_gene(name):
    df = G2KO.dropna()
    # pylint: disable=unsubscriptable-object
    g2ko_spaces = df[df["name"].str.match(unquote_plus(name))]
    spaces = MODEL_DATA.df[MODEL_DATA.df["KO"].isin(g2ko_spaces["ko"])]
    return jsonify_spaces(spaces, MODEL_DATA)


@app.route("/word/get/<label>")
def filter_by_word(label):
    notna_df = MODEL_DATA.df.dropna(subset=["word"])
    return jsonify_spaces(notna_df[notna_df["word"].str.match(unquote_plus(label).replace(",", "|"))], MODEL_DATA)


@app.route("/plot/scatter/<word>")
def plot_scatter(word):
    word_data = MODEL_DATA.df[MODEL_DATA.df['word'] == unquote_plus(word)]
    pred_df = pd.DataFrame(
        word_data['prediction_summary'].values[0].items(),
        columns=['class', 'score'],
    ).sort_values(
        by='score',
        ascending=False,
    ).reset_index(drop=True)

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
            "label": f"Word: {unquote_plus(word)}, Hypothetical: {word_data['hypothetical'].values[0]}, Significant: {word_data['significant'].values[0]}",
            "data": data,
            "ticks": list(pred_df["class"].values),
        }
    )


@app.route("/neighbors/get/<word>")
def neighbors(word):
    additional_columns = []
    if unquote_plus(request.args.get("with_distance")) == "true":
        additional_columns.append("distance")

    top_k_df = pd.read_csv(
        f'https://storage.googleapis.com/gnlp.bursteinlab.org/knn/{unquote_plus(word)}.txt',
        names=["word", "distance"],
        delimiter=" ",
    )

    k = len(top_k_df)
    if request.args.get("k") != None:
        k = int(request.args.get("k"))

    df = pd.merge(top_k_df.nlargest(k, "distance"), MODEL_DATA.df, on="word")
    return jsonify_spaces(df, MODEL_DATA, additional_columns)


def _filter_by_space(type_, filter_):
    match type_:
        case "gene":
            return _search(G2KO, "name", unquote_plus(filter_))
        case "label":
            return _search(LABEL_TO_WORD, "label", unquote_plus(filter_))
        case "space":
            return _search(MODEL_DATA.df, "KO", unquote_plus(filter_))
        case _:
            if type_ == "ko":
                type_ = "KO"

            return _search(MODEL_DATA.df, unquote_plus(type_), unquote_plus(filter_))


def _search(df, column, filter_: str) -> list[str]:
    notna_column = df[column].dropna()
    result = notna_column[
        notna_column.str.contains(
            filter_.replace(",", "|"),
            flags=re.IGNORECASE,
            na=False,
        )
    ]

    return list(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
