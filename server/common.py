import pandas as pd


TILE_SIZE = 1024


class ModelData:
    def __init__(self):
        self.df = pd.read_pickle(
            "model_data.pkl",
        )
        self.x_max = self.df.x.max()
        self.y_max = self.df.y.max()
        self.x_min = self.df.x.min()
        self.y_min = self.df.y.min()


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


def df_to_features(df, model_data: ModelData):
    features = []
    if df is None:
        return features

    for row in df.itertuples():
        y_coord, x_coord = df_coord_to_latlng(
            row.y,
            row.x,
            model_data,
        )
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


def df_coord_to_latlng(y_value, x_value, model_data: ModelData):
    return normalize(y_value, model_data.y_max, model_data.y_min) * - TILE_SIZE, normalize(x_value, model_data.x_min, model_data.x_max) * TILE_SIZE


def normalize(value, value_min, value_max):
    return (value - value_min) / (value_max - value_min)


def spaces_df_to_features(spaces):
    return jsonify(
        {
            "spaces": df_to_features(spaces, MODEL_DATA),
            "latlng": calc_center(spaces),
            "zoom": calc_zoom(spaces),
        },
    )

