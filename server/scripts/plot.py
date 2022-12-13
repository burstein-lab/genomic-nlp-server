import argparse
import shutil
import itertools
import os

import cv2
from PIL import Image
import numpy as np
import pandas as pd


Image.MAX_IMAGE_PIXELS = 1073741824


TILE_SIZE = 1024
# https://coolors.co/b24c63-5438dc-357ded-56eef4-32e875
COLOR_PICKER = itertools.cycle([
    (178, 76, 99),
    (84, 56, 220),
    (53, 125, 237),
    (86, 238, 244),
    (50, 232, 117),
])


class NewPlotter:
    def __init__(self, data_path, bins):
        self.data_path = data_path
        self.bins = bins
        self.space_data = pd.read_pickle(data_path)
        self.max_x = self.space_data.x.max()
        self.min_x = self.space_data.x.min()
        self.max_y = self.space_data.y.max()
        self.min_y = self.space_data.y.min()

    @staticmethod
    def normalize_to_standard(value, value_min, value_max):
        return (value - value_min) / (value_max - value_min)

    @staticmethod
    def normalize_from_standard(value, value_min, value_max):
        return value * (value_max - value_min) + value_min

    def crop_tiles(self, filename, outdir, zoom):
        if zoom == 0:
            shutil.copy(
                filename,
                os.path.join(outdir, "space_by_label_0_0.png"),
            )
            return

        # Based on https://stackoverflow.com/a/65698752
        img = Image.open(filename)
        w, h = img.size
        d = TILE_SIZE
        print("image size:", w, h)

        grid = itertools.product(range(0, h-h % d, d), range(0, w-w % d, d))
        for i, j in grid:
            box = (j, i, j+d, i+d)
            out = os.path.join(
                outdir, f'space_by_label_{int(j / TILE_SIZE)}_{int(i / TILE_SIZE)}.png')
            img.crop(box).save(out)

    def _focus(self, x_range, y_range):
        x_range_min = self.normalize_from_standard(
            x_range[0],
            self.min_x,
            self.max_x,
        )
        x_range_max = self.normalize_from_standard(
            x_range[1],
            self.min_x,
            self.max_x,
        )
        y_range_min = self.normalize_from_standard(
            y_range[0],
            self.min_y,
            self.max_y,
        )
        y_range_max = self.normalize_from_standard(
            y_range[1],
            self.min_y,
            self.max_y,
        )
        return x_range_min, x_range_max, y_range_min, y_range_max

    def plot_pkls(self, outdir: str, zoom: int, threshold: int) -> pd.DataFrame:
        df = self.space_data.copy()
        zoom_levels = calc_zoom_levels(zoom)
        for i, x_lines in enumerate(zoom_levels):
            for j, zoom_ranges in enumerate(x_lines):
                min_x, max_x, min_y, max_y = self._focus(*zoom_ranges)
                # Including all boundaries. We won't have overlaps even if this and neighboring tiles will be plotted because the points are masked from the main df.
                mask = (
                    (df["x"] >= min_x) &
                    (df["x"] <= max_x) &
                    (df["y"] >= min_y) &
                    (df["y"] <= max_y)
                )

                pkl_df = df[mask]
                if len(pkl_df) >= threshold or len(pkl_df) == 0:
                    if len(pkl_df) >= threshold:
                        print("zoom:", zoom, "i:", i, "j:", j,
                              "above threshold:", len(pkl_df))
                    continue

                pd.to_pickle(
                    pkl_df,
                    os.path.join(outdir, f'space_by_label_{i}_{j}.pkl'),
                )
                df = df[~mask]

        return df

    def plot_binned_spaces(self, perm_df: pd.DataFrame, outdir: str, zoom: int) -> str:
        tile_size = TILE_SIZE * (2 ** zoom)
        # https://stackoverflow.com/questions/44595160/create-transparent-image-in-opencv-python
        layer1 = np.zeros((tile_size, tile_size, 4))

        radius = 3  # including border
        border_width = 1
        opacity = int(0.8 * 255)

        for _, row in perm_df.iterrows():
            color = next(COLOR_PICKER)
            center = (
                round(
                    tile_size *
                    self.normalize_to_standard(
                        row['x'],
                        self.min_x,
                        self.max_x,
                    ),
                ),
                round(
                    tile_size *
                    self.normalize_to_standard(
                        row['y'],
                        self.min_y,
                        self.max_y,
                    ),
                ),
            )
            # RGBA color
            cv2.circle(layer1, center, radius, (*color, opacity), -1)
            cv2.circle(
                layer1,
                center,
                radius,
                (*color, 255),
                border_width,
            )

        filename = os.path.join(outdir, "uncropped.png")
        cv2.imwrite(filename, layer1)

        return filename


class SpaceFocus:
    def __init__(self, data_path):
        self.data_path = data_path
        self.space_data = pd.read_pickle(data_path)

    def focus(self, x_range, y_range):
        try:
            result = self.space_data
            x_min = result.x.min()
            y_min = result.y.min()
            x_max = result.x.max()
            y_max = result.y.max()

            x_range_min = self.normalize(x_range[0], x_min, x_max)
            x_range_max = self.normalize(x_range[1], x_min, x_max)
            y_range_min = self.normalize(y_range[0], y_min, y_max)
            y_range_max = self.normalize(y_range[1], y_min, y_max)
            result = result[result["x"] < x_range_max]
            result = result[result["x"] >= x_range_min]
            result = result[result["y"] < y_range_max]
            result = result[result["y"] >= y_range_min]
            return result, (x_range_min, x_range_max), (y_range_min, y_range_max)
        except Exception as exc:
            raise TypeError(f'Input data file should be a pickled data frame, provided'
                            f' {os.path.splitext(self.data_path)[1]} extension') from exc

    @staticmethod
    def normalize(value, value_min, value_max):
        return value * (value_max - value_min) + value_min


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
    new_plotter = NewPlotter(args.data, args.bins)
    for zoom in range(args.max_zoom + 1):
        outdir = os.path.join(args.outdir, str(zoom))
        os.makedirs(outdir, exist_ok=True)
        perm_df = new_plotter.plot_pkls(
            outdir,
            zoom,
            args.min_img_points,
        )
        if not len(perm_df):
            print("finished plotting at zoom", zoom)
            break
        else:
            print("len of perm_df", len(perm_df), "zoom", zoom)

        filename = new_plotter.plot_binned_spaces(
            perm_df,
            outdir,
            zoom,
        )
        new_plotter.crop_tiles(filename, outdir, zoom)


if __name__ == "__main__":
    argparse = argparse.ArgumentParser()
    argparse.add_argument('--data', required=True, type=str,
                          help='path to the gene space dataset')
    argparse.add_argument('--outdir', default='../src/assets/', type=str,
                          help='output dir for img to be saved [default[/src/assest]')
    argparse.add_argument('--max-zoom', default=0, type=int)
    argparse.add_argument('--bins', default=1, type=int,
                          help='number of bins to split the space [default:1]')
    argparse.add_argument('--max_bins', default=30, type=int,
                          help='max number of bins [default:30]')
    argparse.add_argument('--fmt', default='svg', type=str,
                          help='image format [default: svg]')
    argparse.add_argument('--min-img-points', default=2000, type=int,
                          help='Number of points for image. If less a pickle will be created [default: 1000]')
    argparse.add_argument('--save_img', default=1, type=int, help='whether to save figures or display them, 1 is True,'
                          ' else 0 [default: 1]')
    plot_everything(argparse.parse_args())
