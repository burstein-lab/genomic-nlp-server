import argparse
import itertools
import os


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


class Space:
    """Plots a pickled dataframe
    """

    def __init__(self, data_path, dest, bins=1, max_bins=30, fmt='svg', save_img=True):
        self.data_path = data_path
        self.dest = dest
        self.bins = bins
        self.max_bins = max_bins
        self.fmt = fmt
        self.save_img = save_img
        self.space_data = None

    def load_data(self, x_range, y_range):
        if not os.path.exists(self.data_path):
            raise FileNotFoundError
        try:
            space_data = pd.read_pickle(self.data_path)
            x_min = space_data.x.min()
            y_min = space_data.y.min()
            x_max = space_data.x.max()
            y_max = space_data.y.max()

            x_range_min = self.normalize(x_range[0], x_min, x_max)
            x_range_max = self.normalize(x_range[1], x_min, x_max)
            y_range_min = self.normalize(y_range[0], y_min, y_max)
            y_range_max = self.normalize(y_range[1], y_min, y_max)
            space_data = space_data[space_data["x"] <=
                                    x_range_max][space_data["x"] >= x_range_min]
            space_data = space_data[space_data["y"] <=
                                    y_range_max][space_data["y"] >= y_range_min]
            self.space_data = space_data
        except Exception as exc:
            raise TypeError(f'Input data file should be a pickled data frame, provided'
                            f' {os.path.splitext(self.data_path)[1]} extension') from exc

    @staticmethod
    def normalize(value, value_min, value_max):
        return value * (value_max - value_min) + value_min

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

    def plot_binned_spaces(self, permutations, bin_df):
        # perm_img_dir = os.path.join(self.outdir, f'binned_{self.bins}')
        for perm in permutations:
            perm_df = bin_df[bin_df['2d_bin'] == perm]

            _ = plt.figure(figsize=(15, 15), frameon=False)
            # fig.set_size_inches(15,15)
            # ax = plt.Axes(fig, [0., 0., 1., 1.])
            # ax.set_axis_off()
            # fig.add_axes(ax)

            _ = sns.scatterplot(x='x', y='y', data=perm_df, hue='label', legend=False, alpha=0.4,
                                s=10, palette='gist_rainbow')
            # plt.xticks([])
            # plt.yticks([])
            # plt.xlabel('')
            # plt.ylabel('')

            # hide axes
            # for axis in ['top', 'bottom', 'left', 'right']:
            #     ax.spines[axis].set_linewidth(2)  # change width
            #     ax.spines[axis].set_color('#EDE8EB')    # change color

            if self.save_img:
                # ax = plt.Axes(fig, [0., 0., 1., 1.])
                # ax.set_axis_off()
                # fig.add_axes(ax)
                plt.axis('off')
                plt.savefig(self.dest, bbox_inches='tight',
                            transparent=False, pad_inches=-0.5)
            else:
                plt.show()


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
        outdir = os.path.join(args.outdir, str(zoom))
        os.makedirs(outdir, exist_ok=True)
        zoom_levels = calc_zoom_levels(zoom)
        for i, x_lines in enumerate(zoom_levels):
            for j, zoom_ranges in enumerate(x_lines):
                gene_space = Space(
                    data_path=args.data,
                    dest=os.path.join(
                        outdir, f'space_by_label_{i}_{len(x_lines) - j - 1}.{args.fmt}'),
                    bins=args.bins,
                    max_bins=args.max_bins,
                    fmt=args.fmt,
                    save_img=args.save_img,
                )
                gene_space.load_data(*zoom_ranges)
                if len(gene_space.space_data) < args.min_img_points:
                    pd.to_pickle(gene_space.space_data, os.path.join(
                        outdir, f'space_by_label_{i}_{len(x_lines) - j - 1}.pkl'))
                    continue

                perms = gene_space.extract_permutations()
                binned_df = gene_space.bin_space_for_image()
                gene_space.plot_binned_spaces(perms, binned_df)


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
    argparse.add_argument('--min-img-points', default=1000, type=int,
                          help='Number of points for image. If less a pickle will be created [default: 1000]')
    argparse.add_argument('--save_img', default=1, type=int, help='whether to save figures or display them, 1 is True,'
                                                                  ' else 0 [default: 1]')
    plot_everything(argparse.parse_args())
