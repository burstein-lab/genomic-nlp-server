import argparse
import itertools
import os


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

class Space:
    def __init__(self, data_path, outdir='../src/assets/', bins=1, max_bins=30, fmt='svg', save_img=True):
        self.data_path = data_path
        self.outdir = outdir
        self.bins = bins
        self.max_bins = max_bins
        self.fmt = fmt
        self.save_img = save_img
        self.space_data = None

    def load_data(self, x_range, y_range):
        if not os.path.exists(self.data_path):
            raise FileNotFoundError
        try:
            df = pd.read_pickle(self.data_path)
            x_min = df.x.min()
            y_min = df.y.min()
            x_max = df.x.max()
            y_max = df.y.max()

            x_range_min = self.normalize(x_range[0], x_min, x_max)
            x_range_max = self.normalize(x_range[1], x_min, x_max)
            y_range_min = self.normalize(y_range[0], y_min, y_max)
            y_range_max = self.normalize(y_range[1], y_min, y_max)
            df = df[df["x"] <= x_range_max][df["x"] >= x_range_min]
            df = df[df["y"] <= y_range_max][df["y"] >= y_range_min]
            self.space_data = df
        except:
            raise TypeError(f'Input data file should be a pickled data frame, provided'
                            f' {os.path.splitext(self.data_path)[1]} extension')

    def normalize(self, a, a_min, a_max):
        # return (a - a_min) / (a_max - a_min)
        return a * (a_max - a_min) + a_min

    def bin_space_for_image(self):
        if self.bins < 1 | self.bins > self.max_bins:
            raise ValueError(f"Bin number should be in the range of [1,{self.max_bins}], but {self.bins} were provided"
                             f"please choose a valid bin number")
        if self.space_data is None:
            self.load_data()
        df = self.space_data

        counts, xedges, yedges = np.histogram2d(df['x'], df['y'], bins=self.bins)
        df['x_bin'] = df['x'].apply(lambda x: np.searchsorted(xedges, x))
        df['y_bin'] = df['x'].apply(lambda y: np.searchsorted(yedges, y))

        # indices are calculated through right assignment, 0 indicated the minimal x/y value
        df['x_bin'] = df['x_bin'].apply(lambda x: 1 if x == 0 else x)
        df['y_bin'] = df['y_bin'].apply(lambda y: 1 if y == 0 else y)

        df["2d_bin"] = df.apply(lambda row: (row['x_bin'], row['y_bin']), axis=1)

        return df

    def extract_permutations(self):
        bins = np.arange(1, self.bins + 1)
        return list(itertools.permutations(bins)) + [(b,b) for b in bins]

    def plot_binned_spaces(self, permutations, binned_df):
        # perm_img_dir = os.path.join(self.outdir, f'binned_{self.bins}')
        for perm in permutations:
            perm_df = binned_df[binned_df['2d_bin'] == perm]

            fig = plt.figure(figsize=(15,15), frameon=False)
            # fig.set_size_inches(15,15)
            # ax = plt.Axes(fig, [0., 0., 1., 1.])
            # ax.set_axis_off()
            # fig.add_axes(ax)

            ax = sns.scatterplot(x='x', y='y', data=perm_df, hue='label', legend=False, alpha=0.4,
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
                plt.savefig(self.outdir, bbox_inches='tight', transparent=False, pad_inches=-0.5)
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
        r = []
        for j in range(len(parts) - 1):
            r.append([
                [parts[i], parts[i+1]],
                [parts[j], parts[j+1]],
            ])
        result.append(r)

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



if __name__ == "__main__":
    argparse = argparse.ArgumentParser()
    argparse.add_argument('--data', required=True, type=str, help='path to the gene space dataset')
    argparse.add_argument('--outdir', default='../src/assets/', type=str, help='output dir for img to be saved [default[/src/assest]')
    argparse.add_argument('--max-zoom', default=0, type=int)
    argparse.add_argument('--bins', default=1, type=int, help='number of bins to split the space [default:1]')
    argparse.add_argument('--max_bins', default=30, type=int, help='max number of bins [default:30]')
    argparse.add_argument('--fmt', default='svg', type=str, help='image format [default: svg]')
    argparse.add_argument('--save_img', default=1, type=int, help='whether to save figures or display them, 1 is True,'
                                                                  ' else 0 [default: 1]')
    params = argparse.parse_args()

    for zoom in range(params.max_zoom + 1):
        outdir = os.path.join(params.outdir, str(zoom))
        os.makedirs(outdir, exist_ok=True)
        zoom_levels = calc_zoom_levels(zoom)
        for i, x_lines in enumerate(zoom_levels):
            for j, zoom_ranges in enumerate(x_lines):
                try:
                    gene_space = Space(
                        data_path=params.data,
                        outdir=os.path.join(outdir, f'space_by_label_{i}_{len(x_lines) - j - 1}.{params.fmt}'),
                        bins=params.bins,
                        max_bins=params.max_bins,
                        fmt=params.fmt,
                        save_img=params.save_img,
                    )
                    gene_space.load_data(*zoom_ranges)
                    perms = gene_space.extract_permutations()
                    binned_df = gene_space.bin_space_for_image()
                    gene_space.plot_binned_spaces(perms, binned_df)
                except:
                    pass
