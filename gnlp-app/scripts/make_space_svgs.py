import argparse
import itertools
import os


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

class Space:
    def __init__(self, data_path=data_path, outdir='../src/assets/', bins=1, max_bins=30, fmt='svg', save_img=True):
        self.data_path = data_path
        self.outdir = outdir
        self.bins = bins
        self.max_bins = max_bins
        self.fmt = fmt
        self.save_img = save_img
        self.space_data = None

    def load_data(self):
        if not os.path.exists(self.data_path):
            raise FileNotFoundError
        try:
            df = pd.read_pickle(self.data_path)
            self.space_data = df
        except:
            raise TypeError(f'Input data file should be a pickled data frame, provided'
                            f' {os.path.splitext(self.data_path)[1]} extension')

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
        perm_img_dir = os.path.join(self.outdir, f'binned_{self.bins}')
        if self.save_img:
            os.makedirs(perm_img_dir, exist_ok=True)

        for perm in permutations:
            perm_df = binned_df[binned_df['2d_bin'] == perm]

            fig = plt.figure(figsize=(15,15))
            ax = sns.scatterplot(x='x', y='y', data=perm_df, hue='label', legend=False, alpha=0.4,
                                 s=10, palette='gist_rainbow')
            plt.xticks([])
            plt.yticks([])
            plt.xlabel('')
            plt.ylabel('')

            # hide axes
            for axis in ['top', 'bottom', 'left', 'right']:
                ax.spines[axis].set_linewidth(2)  # change width
                ax.spines[axis].set_color('#EDE8EB')    # change color

            if self.save_img:
                plt.savefig(os.path.join(perm_img_dir,f'space_by_label_bin.{self.fmt}'), fmt=self.fmt, layout='tight')
            else:
                plt.show()


if __name__ == "__main__":
    argparse = argparse.ArgumentParser()
    argparse.add_argument('--data', required=True, type=str, help='path to the gene space dataset')
    argparse.add_argument('--outdir', default='../src/assets/', type=str, help='output dir for img to be saved [default[/src/assest]')
    argparse.add_argument('--bins', default=1, type=int, help='number of bins to split the space [default:1]')
    argparse.add_argument('--max_bins', default=30, type=int, help='max number of bins [default:30]')
    argparse.add_argument('--fmt', default='svg', type=str, help='image format [default: svg]')
    argparse.add_argument('--save_img', default=1, type=int, help='whether to save figures or display them, 1 is True,'
                                                                  ' else 0 [default: 1]')
    params = argparse.parse_args()

    gene_space = Space(data_path=params.data, outdir=params.outdir, bins=params.bins,
                        max_bins=params.max_bins, fmt=params.fmt, save_img=params.save_img)
    gene_space.load_data()
    perms = gene_space.extract_permutations()
    binned_df = gene_space.bin_space_for_image()

    gene_space.plot_binned_spaces(perms, binned_df)




