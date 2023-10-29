import argparse
import os
import simplejson

import matplotlib.pyplot as plt
import pandas as pd

from common import ModelData, TILE_SIZE, df_to_interactive_spaces

GREY_HEX = "#808080"
GREY_OPACITY = int(0.3 * 255)


def hex_to_rgb(value):
    hex_value = value.lstrip('#')
    return tuple(int(hex_value[i:i+2], 16) for i in (0, 2, 4))


class Plotter:
    """Plots data in png format as well as saving small enough chunks in json format"""

    def __init__(self, bins):
        self.bins = bins
        self.model_data = ModelData()
        self.model_data.df["rgb_color"] = self.model_data.df.apply(
            lambda row: hex_to_rgb(row.color), axis=1,
        )
        # in order to plot grey circles first.
        self.model_data.df["order"] = self.model_data.df.apply(
            lambda row: 0 if row.color == GREY_HEX else 1, axis=1,
        )

        self.model_data.df.sort_values(
            by=["order"],
            ascending=True,
            inplace=True,
        )

    @staticmethod
    def normalize_to_standard(value, value_min, value_max):
        return (value - value_min) / (value_max - value_min)

    @staticmethod
    def normalize_from_standard(value, value_min, value_max):
        return value * (value_max - value_min) + value_min

    def _focus(self, x_range, y_range):
        x_range_min = self.normalize_from_standard(
            x_range[0],
            self.model_data.x_min,
            self.model_data.x_max,
        )
        x_range_max = self.normalize_from_standard(
            x_range[1],
            self.model_data.x_min,
            self.model_data.x_max,
        )
        y_range_min = self.normalize_from_standard(
            y_range[0],
            self.model_data.y_min,
            self.model_data.y_max,
        )
        y_range_max = self.normalize_from_standard(
            y_range[1],
            self.model_data.y_min,
            self.model_data.y_max,
        )
        return x_range_min, x_range_max, y_range_min, y_range_max

    def plot_jsons(self, outdir: str, zoom: int, threshold: int) -> pd.DataFrame:
        df = self.model_data.df.copy()
        zoom_levels = calc_zoom_levels(zoom)
        for i, x_lines in enumerate(zoom_levels):
            for j, zoom_ranges in enumerate(x_lines):
                print("json plot zoom:", zoom, "i:", i, "j:", j)
                min_x, max_x, min_y, max_y = self._focus(*zoom_ranges)
                # Including all boundaries. We won't have overlaps even if this and neighboring tiles will be plotted because the points are masked from the main df.
                mask = (
                    (df["x"] >= min_x) &
                    (df["x"] <= max_x) &
                    (df["y"] >= min_y) &
                    (df["y"] <= max_y)
                )

                plot_df = df[mask]
                if (threshold != -1 and len(plot_df) >= threshold) or len(plot_df) == 0:
                    if len(plot_df) >= threshold:
                        print("zoom:", zoom, "i:", i, "j:", j,
                              "above threshold:", len(plot_df))
                    continue

                with open(os.path.join(outdir, f"space_by_label_{i}_{len(x_lines) - 1 - j}.json"), "w", encoding="utf8") as dest:
                    dest.write(
                        simplejson.dumps(
                            {"spaces": df_to_interactive_spaces(
                                plot_df, self.model_data)},
                            ignore_nan=True,
                        ),
                    )
                df = df[~mask]

        return df

    def plot_static(self, df: pd.DataFrame, outdir: str, zoom: int) -> str:
        zoom_levels = calc_zoom_levels(zoom)
        radius = 1 + zoom
        uncropped_size = TILE_SIZE * (2 ** zoom)
        df = df.copy()
        df['plot_x'] = df.apply(lambda row: round(
            uncropped_size * self.normalize_to_standard(row['x'], self.model_data.x_min, self.model_data.x_max)), axis=1)
        df['plot_y'] = df.apply(lambda row: round(
            uncropped_size * self.normalize_to_standard(row['y'], self.model_data.y_min, self.model_data.y_max)), axis=1)
        for i, x_lines in enumerate(zoom_levels):
            for j, zoom_ranges in enumerate(x_lines):
                print("img plot zoom:", zoom, "i:", i, "j:", j)
                plt.clf()
                fig = plt.gcf()
                fig.set_size_inches(TILE_SIZE, TILE_SIZE)
                threshold = radius
                min_x, max_x, min_y, max_y = self._focus(*zoom_ranges)
                min_x_edge = round(
                    uncropped_size * zoom_ranges[0][0]) - threshold
                min_y_edge = round(
                    uncropped_size * zoom_ranges[1][0]) - threshold
                max_x_edge = round(
                    uncropped_size * zoom_ranges[0][1]) + threshold
                max_y_edge = round(
                    uncropped_size * zoom_ranges[1][1]) + threshold

                mask = (
                    (df["plot_x"] > min_x_edge) &
                    (df["plot_x"] < max_x_edge) &
                    (df["plot_y"] > min_y_edge) &
                    (df["plot_y"] < max_y_edge)
                )
                plot_df = df[mask]
                circles = plot_df.apply(
                    lambda row: self.create_circle(
                        min_x,  # pylint: disable=cell-var-from-loop
                        max_x,  # pylint: disable=cell-var-from-loop
                        min_y,  # pylint: disable=cell-var-from-loop
                        max_y,  # pylint: disable=cell-var-from-loop
                        radius,
                        row,
                    ),
                    axis=1,
                )
                if len(circles) == 0:
                    continue

                fig.patches.extend(circles)
                filename = os.path.join(
                    outdir, f'space_by_label_{i}_{len(x_lines) - 1 - j}.png')
                fig.savefig(filename, dpi=1, transparent=True)

    def create_circle(self, min_x, max_x, min_y, max_y, radius, row):
        opacity = int(0.5 * 255)
        center = (
            round(
                TILE_SIZE *
                self.normalize_to_standard(
                    row.x,
                    min_x,
                    max_x,
                ),
            ),
            round(
                TILE_SIZE *
                self.normalize_to_standard(
                    row.y,
                    min_y,
                    max_y,
                ),
            ),
        )
        return plt.Circle(
            center,
            radius,
            color=tuple((i / 255 for i in (*row.rgb_color,
                        GREY_OPACITY if row.color == GREY_HEX else opacity))),
            fill=True,
        )


def zoom_splitter(zoom):
    result = [0]
    part = 1 / (2 ** zoom)
    while result[-1] < 1:
        result.append(result[-1] + part)

    return result


def zoom_union(parts):
    result = []
    for i in range(len(parts) - 1):
        tile_edges = []
        for j in range(len(parts) - 1):
            tile_edges.append([
                [parts[i], parts[i+1]],
                [parts[j], parts[j+1]],
            ])
        result.append(tile_edges)

    return result


def calc_zoom_levels(zoom):
    """
    0 -> [
        [
            [[0, 1.0], [0, 1.0]],
        ],
    ]
    1 -> [
        [
            [[0, 0.5], [0, 0.5]],
            [[0, 0.5], [0.5, 1.0]],
        ],
        [
            [[0.5, 1.0], [0, 0.5]],
            [[0.5, 1.0], [0.5, 1.0]],
        ],
    ]
    """
    return zoom_union(zoom_splitter(zoom))


def plot_everything(args):
    new_plotter = Plotter(args.bins)
    for zoom in range(args.min_zoom, max(args.min_zoom, args.max_zoom) + 1):
        outdir = os.path.join(args.outdir, str(zoom))
        os.makedirs(outdir, exist_ok=True)
        df = new_plotter.plot_jsons(
            outdir,
            zoom,
            -1 if zoom > args.max_png_zoom else args.min_img_points,
        )
        print("finished plotting jsons at zoom", zoom)
        if len(df) == 0:
            print("finished plotting at zoom", zoom)
            continue

        print("len of df", len(df), "zoom", zoom)

        new_plotter.plot_static(
            df,
            outdir,
            zoom,
        )
        print("finished plotting images at zoom", zoom)


if __name__ == "__main__":
    argparse = argparse.ArgumentParser()
    argparse.add_argument('--outdir', default='../src/assets/', type=str,
                          help='output dir for img to be saved')
    argparse.add_argument('--min-zoom', default=0, type=int)
    argparse.add_argument('--max-zoom', default=0, type=int)
    argparse.add_argument('--max-png-zoom', default=0, type=int)
    argparse.add_argument('--bins', default=1, type=int,
                          help='number of bins to split the space')
    argparse.add_argument('--max_bins', default=30, type=int,
                          help='max number of bins')
    argparse.add_argument('--min-img-points', default=2000, type=int,
                          help='Number of points for image. If less a pickle will be created')
    plot_everything(argparse.parse_args())
