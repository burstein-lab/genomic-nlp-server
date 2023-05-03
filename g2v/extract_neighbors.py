import argparse
import os
import numpy as np
import pandas as pd

from tqdm import tqdm
from gensim.models import word2vec as w2v


parser = argparse.ArgumentParser('Extract All nearest neighbors')
parser.add_argument('--model', required=True, help='model data in a pickle format')
parser.add_argument('--emb', required=True, help='embedding model in gensim format')
parser.add_argument('-k', default=20, help='number of nearest neighbors to extract')
parser.add_argument('--out', default='./', help='output directory to save results')

args = parser.parse_args()

# load metadata and model
mdl = w2v.Word2Vec.load(
    args.model,
)
data = pd.read_pickle(args.emb)
k = args.k

# This part might take a while...
for w in tqdm(data['word'].unique()):
    top_k = mdl.wv.most_similar(w, topn=k)
    np.savetxt(os.path.join(args.out, f'{w}.txt'),
              top_k, fmt='%s')

