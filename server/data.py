import os
import pickle
import glob

import pandas as pd
from gensim.models import word2vec as w2v


METADATA = pd.read_csv(
    r"/Users/daniellemiller/Google Drive/PhD/Projects/gene2vec/ko_data/metadata.csv")


# TODO(#27) - hard coded models files (partial data)
DATA_DICT = {
    "batch52_300t": r"/Volumes/GoogleDrive/My Drive/PhD/Projects/gene2vec/global_sewage/trained_models/ALL/batch_52",
    "batch52_300u": r"/Volumes/GoogleDrive/My Drive/PhD/Projects/gene2vec/global_sewage/trained_models/ALL/batch_52",
    "batch87_512t": r"/Volumes/GoogleDrive/My Drive/PhD/Projects/gene2vec/global_sewage/trained_models/ALL/batch_87",
    "batch87_512u": r"/Volumes/GoogleDrive/My Drive/PhD/Projects/gene2vec/global_sewage/trained_models/ALL/batch_87",
}


def load_data_for_app(dataset):
    if dataset.endswith("u"):
        alias = "umap"
    else:
        alias = "tsne"
    mdl_files = glob.glob(f"{DATA_DICT[dataset]}/*")
    embedding_path = [f for f in mdl_files if f"words_{alias}" in f][0]
    mdl_path = [f for f in mdl_files if f.endswith("w2v")][0]

    with open(embedding_path, 'rb') as handle:
        embedding_df = pickle.load(handle)
    g2v = w2v.Word2Vec.load(mdl_path)

    embedding_df["KO"] = embedding_df["word"]
    embedding_df["hypothetical"] = embedding_df["word"].apply(
        lambda x: "YES" if "Cluster" in x else "NO")
    embedding_df = embedding_df.merge(
        METADATA, on=["KO"], how="left").fillna("unknown")
    clustering_data = pd.read_csv(os.path.join(
        DATA_DICT[dataset], f"{alias}_clusters.csv"))
    clustering_data["cluster"] = clustering_data["cluster"].astype(str)
    embedding_df = embedding_df.merge(clustering_data, on=["word"], how="left")

    return embedding_df, g2v