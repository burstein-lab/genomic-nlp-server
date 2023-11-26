import math

from flask import jsonify
import numpy as np
import pandas as pd


TILE_SIZE = 512
MAX_ZOOM = 9


class ModelData:
    """Manages the model data with preset calculated values.
    """
    def __init__(self):
        self.df = pd.read_pickle(
            "model_data.pkl",
        )
        self._x_max = self.df.x.max()
        self._y_max = self.df.y.max()
        self._x_min = self.df.x.min()
        self._y_min = self.df.y.min()

    @property
    def x_max(self):
        return self._x_max

    @property
    def y_max(self):
        return self._y_max

    @property
    def x_min(self):
        return self._x_min

    @property
    def y_min(self):
        return self._y_min


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


def df_to_interactive_spaces(df, model_data: ModelData, additonal_columns: list[str] = None):
    features = []
    if df is None:
        return features

    result = df.apply(
        lambda row: row_to_feature(model_data, row, additonal_columns),
        axis=1,
    )
    return result.tolist()


def row_to_feature(model_data: ModelData, row, additonal_columns: list[str] = None):
    y_coord, x_coord = df_coord_to_latlng(
        row.y,
        row.x,
        model_data,
    )
    data = {
        "name": f"{x_coord},{y_coord}",
        "word": row.word,
        "ko": row.KO if not pd.isnull(row.KO) else None,
        "label": row.label if not pd.isnull(row.label) else None,
        "product": row["product"] if not pd.isnull(row["product"]) else None,
        "gene_name": row.gene_name if not pd.isnull(row.gene_name) else None,
        "significant": row.significant if not pd.isnull(row.significant) else None,
        "ncbi_nr": row.ncbi_nr if not pd.isnull(row.ncbi_nr) else None,
        "predicted_class": row.predicted_class if not pd.isnull(row.predicted_class) else None,
        # hex color
        "color": row.color if not pd.isnull(row.color) else None,
        "hypothetical": row.hypothetical if not pd.isnull(row.hypothetical) else None,
        "word_count": row.word_count if not pd.isnull(row.word_count) else -1,
        "tax_distribution": row.tax_distribution if not pd.isnull(row.tax_distribution) else None,
    }

    if additonal_columns is not None:
        for column in additonal_columns:
            data[column] = row[column]

    return Point(
        row.word,
        x_coord,
        y_coord,
        data,
    ).todict()


def df_coord_to_latlng(y_value, x_value, model_data: ModelData):
    return normalize(y_value, model_data.y_max, model_data.y_min) * - TILE_SIZE, normalize(x_value, model_data.x_min, model_data.x_max) * TILE_SIZE


def normalize(value, value_min, value_max):
    return (value - value_min) / (value_max - value_min)


def calc_zoom(spaces, model_data: ModelData):
    if len(spaces) == 0:
        return 0

    min_y, min_x = df_coord_to_latlng(
        spaces.y.min(),
        spaces.x.min(),
        model_data,
    )
    max_y, max_x = df_coord_to_latlng(
        spaces.y.max(),
        spaces.x.max(),
        model_data,
    )
    gap = max(max_y - min_y, max_x - min_x)
    if gap == 0 or np.isnan(gap):
        return MAX_ZOOM

    return min(math.floor(math.log2(TILE_SIZE) - math.log2(gap)), MAX_ZOOM)


def calc_middle_value(column):
    return (column.max() + column.min()) / 2.0


def calc_center(spaces, model_data: ModelData):
    lat, lng = df_coord_to_latlng(
        calc_middle_value(spaces.y),
        calc_middle_value(spaces.x),
        model_data,
    )
    return {"lat": None if pd.isnull(lat) else lat, "lng": None if pd.isnull(lng) else lng}


def jsonify_spaces(spaces, model_data: ModelData, additional_columns: list[str] = None):
    return jsonify(
        {
            "spaces": df_to_interactive_spaces(spaces, model_data, additional_columns),
            "latlng": calc_center(spaces, model_data),
            "zoom": calc_zoom(spaces, model_data),
        },
    )
