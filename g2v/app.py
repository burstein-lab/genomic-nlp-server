import json

from flask import Flask, jsonify, request
from flask_cors import CORS
from gensim.models import word2vec as w2v
import pandas as pd

from common import ModelData, spaces_df_to_features


# configuration
DEBUG = True

MDL = w2v.Word2Vec.load(
    "gene2vec_w5_v300_tf24_annotation_extended_2021-10-03.w2v",
)


MODEL_DATA = ModelData()


# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/neighbors/get/<label>")
def filter_by_neighbors(label):
    topn = json.loads(request.args.get("k"))
    top_k = [similar for similar, _ in MDL.wv.most_similar(label, topn=topn)]
    df = MODEL_DATA.df[MODEL_DATA.df["word"].isin(top_k)]
    return spaces_df_to_features(df, MODEL_DATA)


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
