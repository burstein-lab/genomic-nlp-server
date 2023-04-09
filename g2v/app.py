import os

from flask import Flask, jsonify
from flask_cors import CORS
from gensim.models import word2vec as w2v
import pandas as pd
from google.cloud import storage


# configuration
DEBUG = True

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

MDL = w2v.Word2Vec.load(
    "gene2vec_w5_v300_tf24_annotation_extended_2021-10-03.w2v",
)


# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})


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