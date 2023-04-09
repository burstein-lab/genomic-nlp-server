import os

import pandas as pd


TILE_SIZE = 1024


class Point:
    """Defines a point coordinations and its value in space
    """

    def __init__(self, id_, x_coord, y_coord, value) -> None:
        self.id_ = id_
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.value = value

    @classmethod
    def fromdict(cls, id_, x_coord, y_coord, value):
        return cls(id_, x_coord, y_coord, value)

    def todict(self) -> dict:
        return {
            "id": self.id_,
            "x": self.x_coord,
            "y": self.y_coord,
            "value": self.value,
        }


def df_to_features(df, y_min, y_max, x_min, x_max):
    features = []
    if df is None:
        return features

    for row in df.itertuples():
        y_coord, x_coord = df_coord_to_latlng(
            row.y, row.x, y_min, y_max, x_min, x_max)
        features.append(
            Point(
                row.Index,
                x_coord,
                y_coord,
                {
                    "name": f"{x_coord},{y_coord}",
                    "word": row.word,
                    "ko": row.KO,
                    "label": row.label,
                    "product": row.product if not pd.isnull(row.product) else None,
                    "gene_name": row.gene_name,
                    "significant": row.significant,
                    "predicted_class": row.predicted_class,
                    "color": row.color,  # hex color
                    "hypothetical": row.hypothetical,
                },
            ).todict(),
        )

    return features


def df_coord_to_latlng(y_value, x_value, y_min, y_max, x_min, x_max):
    return normalize(y_value, y_max, y_min) * - TILE_SIZE, normalize(x_value, x_min, x_max) * TILE_SIZE


def normalize(value, value_min, value_max):
    return (value - value_min) / (value_max - value_min)


class ModelData:
    def __init__(self):
        self.df = pd.read_pickle(
            "model_data.pkl",
            usecols=[
                "x",
                "y",
                "word",
                "KO",
                "label",
                "product",
                "gene_name",
                "significant",
                "predicted_class",
                "color",
                "hypothetical",
            ],
        )
        self.x_max = self.df.x.max()
        self.y_max = self.df.y.max()
        self.x_min = self.df.x.min()
        self.y_min = self.df.y.min()


def load_model_data():
    from google.cloud import storage
    if not os.path.isfile("model_data.pkl"):
        storage_client = storage.Client(project="genomic-nlp")
        with open("model_data.pkl", "wb") as f:
            storage_client.download_blob_to_file(
                "gs://gnlp.bursteinlab.org/data/model_data.pkl", f)

    return ModelData()
