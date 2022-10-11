import argparse
import io
import itertools
import os

import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import pandas as pd
import seaborn as sns


def bbox_gen():
    """
    In order to get an estimated border, run im.getbbox() on one of the images. This calculates the size of an image without zero-values pixels meaning dead-zones are not included in the size.
    BBOX = im.getbbox()
    """

    while True:
        yield None

    # Images within the map overlap each other. Therefore, cropped points are being compensated for.
    yield (211, 196, 1262, 1335)  # (left, top, right, bottom)
    while True:
        yield (211, 196, 1262, 1335)


BBOX_GEN = bbox_gen()


class Space:
    def __init__(self, data_path):
        self.data_path = data_path
        self.space_data = pd.read_pickle(data_path)
        self.max_x = self.space_data.x.max()
        self.mix_x = self.space_data.x.min()
        self.max_y = self.space_data.y.max()
        self.min_y = self.space_data.y.min()

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
            result = result[result["x"] <= x_range_max]
            result = result[result["x"] >= x_range_min]
            result = result[result["y"] <= y_range_max]
            result = result[result["y"] >= y_range_min]
            return result, (x_range_min, x_range_max), (y_range_min, y_range_max)
        except Exception as exc:
            raise TypeError(f'Input data file should be a pickled data frame, provided'
                            f' {os.path.splitext(self.data_path)[1]} extension') from exc

    @staticmethod
    def normalize(value, value_min, value_max):
        return value * (value_max - value_min) + value_min


class Plot:
    """Plots a pickled dataframe
    """

    def __init__(self, space_data, dest, bins=1, max_bins=30, fmt='svg', save_img=True):
        self.space_data = space_data
        self.dest = dest
        self.bins = bins
        self.max_bins = max_bins
        self.fmt = fmt
        self.save_img = save_img

    def bin_space_for_image(self):
        if self.bins < 1 | self.bins > self.max_bins:
            raise ValueError(f"Bin number should be in the range of [1,{self.max_bins}], but {self.bins} were provided"
                             f"please choose a valid bin number")
        bin_df = self.space_data
        _, xedges, yedges = np.histogram2d(
            bin_df['x'], bin_df['y'], bins=self.bins)
        bin_df['x_bin'] = bin_df['x'].apply(
            lambda x: np.searchsorted(xedges, x))
        bin_df['y_bin'] = bin_df['x'].apply(
            lambda y: np.searchsorted(yedges, y))

        # indices are calculated through right assignment, 0 indicated the minimal x/y value
        bin_df['x_bin'] = bin_df['x_bin'].apply(lambda x: 1 if x == 0 else x)
        bin_df['y_bin'] = bin_df['y_bin'].apply(lambda y: 1 if y == 0 else y)

        bin_df["2d_bin"] = bin_df.apply(lambda row: (
            row['x_bin'], row['y_bin']), axis=1)

        return bin_df

    def extract_permutations(self):
        bins = np.arange(1, self.bins + 1)
        return list(itertools.permutations(bins)) + [(bin, bin) for bin in bins]

    def plot_binned_spaces(self, permutations, bin_df: pd.DataFrame, x_limits, y_limits):
        for perm in permutations:
            perm_df = bin_df[bin_df['2d_bin'] == perm]
            if perm_df.empty:
                continue

            _ = plt.figure(figsize=(15, 15), frameon=False)
            ax = sns.scatterplot(
                x='x',
                y='y',
                data=perm_df,
                hue='label',
                legend=False,
                alpha=0.4,
                s=10,
                palette='gist_rainbow',
            )
            ax.set(
                xlim=x_limits,
                ylim=y_limits,
            )
            plt.axis('off')
            buf = io.BytesIO()
            plt.savefig(buf, transparent=True,
                        bbox_inches='tight', pad_inches=0)
            # plt.savefig(buf, bbox_inches='tight',
            #             transparent=False, pad_inches=0)
            buf.seek(0)
            with Image.open(buf) as im:
                bbox = next(BBOX_GEN)
                print(im.getbbox(), bbox)
                im.crop(bbox).save(self.dest, self.fmt)

            buf.close()


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
        ((0, 0), (1, 1)),
    ]
    1 -> [
        ((0, 0), (0.5, 0.5)),
        ((0.5, 0.5), (1, 1)),
    ]
    2 -> [
        ((0, 0), (0.25, 0.25)),
        ((0.25, 0.25), (0.5, 0.5)),
        ((0.5, 0.5), (0.75, 0.75)),
        ((0.75, 0.75), (1, 1)),
    ]
    """
    return zoom_union(zoom_splitter(zoom))


def plot_everything(args):
    for zoom in range(args.max_zoom + 1):
        space_data = Space(args.data)
        outdir = os.path.join(args.outdir, str(zoom))

        os.makedirs(outdir, exist_ok=True)
        zoom_levels = calc_zoom_levels(zoom)
        for i, x_lines in enumerate(zoom_levels):
            for j, zoom_ranges in enumerate(x_lines):
                focused_df, x_limits, y_limits = space_data.focus(*zoom_ranges)
                if len(focused_df) < args.min_img_points:
                    pd.to_pickle(gene_space.space_data, os.path.join(
                        outdir, f'space_by_label_{i}_{len(x_lines) - j - 1}.pkl'))
                    continue

                gene_space = Plot(
                    space_data=focused_df,
                    dest=os.path.join(
                        outdir, f'space_by_label_{i}_{len(x_lines) - j - 1}.{args.fmt}'),
                    bins=args.bins,
                    max_bins=args.max_bins,
                    fmt=args.fmt,
                    save_img=args.save_img,
                )
                perms = gene_space.extract_permutations()
                binned_df = gene_space.bin_space_for_image()
                gene_space.plot_binned_spaces(
                    perms, binned_df, x_limits, y_limits)


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
    argparse.add_argument('--min-img-points', default=500, type=int,
                          help='Number of points for image. If less a pickle will be created [default: 1000]')
    argparse.add_argument('--save_img', default=1, type=int, help='whether to save figures or display them, 1 is True,'
                                                                  ' else 0 [default: 1]')
    plot_everything(argparse.parse_args())
