# :dna: GeNLP

**GeNLP: An interactive web application for microbial gene exploration and prediction**

#### :globe_with_meridians: Visit the [GeNLP website](http://gnlp.bursteinlab.org/)

The quick user guide is available at our [GitHub wiki](https://github.com/burstein-lab/genomic-nlp-server/wiki)

![](https://github.com/burstein-lab/genomic-nlp-server/blob/main/img/gifx2-720.gif)

This repository contains the implementation of _GeNLP_, a user-friendly web server to explore gene relationships!<br>
The server is based on a pre-trained published language model:<br>
"[Deciphering microbial gene function using natural language processing](https://www.nature.com/articles/s41467-022-33397-4)"<br>

Weights and trained model are available on the paper's [GitHub repository](https://github.com/burstein-lab/genomic-nlp).

## Getting Started

This web service does not require any previous installation.<br/>
In the following use case, we demonstrate the core features of the web server together with potential biological insights.
<br>
Upon entering the web service, a map of all genes supported by our model is presented, color-coded by their functional group, unknown proteins are colored in light grey.<br>

### Search for sequence
We start by using the server on an unknown protein sequence, with no mapping to existing databases.

```
>Protein1
MTKLELLVSVMVDGKWYSTDDLVSRVGHRFSATKHVAEKQGYQFEKRREGMRFEYRMVST
TIELAR
```

To obtain a prediction, go to the search panel and choose `Sequence`. The app will run in the background and find the matching
gene identifier in our model for Protein1.<br>
_NOTICE_: This process might take a few minutes :hugs:<br>

After the search is completed, the predicted gene identifier and its corresponding prediction scores will be available for download.
We will use the predicted gene identifier: `hypo.clst.15503442` to explore `Protein1`.<br>

### Explore prediction

_note_: if you ran the search by sequence the predicted gene `hypo.clst.15503442` will be highlighted in the genomic map.<br>
Go to the search bar and select _model word_ mode. Type the identifier name in the search bar below (it should auto-complete).<br>
The highlighted dot on the space marked `hypo.clst.15503442`. By zooming in to the cluster in which this dot resides we can interactively inspect the neighboring genes, most of which are related to the CRISPR-Cas system.
For in-depth analysis, click on the dot to open a panel with the following information:

- Predicted class
- Prediction confidence
- Neighbors
- Gene prediction
- NCBI NR description
- Gene count in family

#### Gene function prediction

The predicted class is _Prokaryotic Defense System_ and the prediction is _reliable_ (trusted prediction is True).<br>
By clicking on `FUNC PRED` a panel will open showing all scores received by the model for the different classes. Here, the
_Prokaryotic Defense System_ prediction was unequivocal, with a score close to 1 (possible scores are between 0 to 1).<br>

#### Analyzing neighbors

By clicking on the `NEIGHBORS` tab a bar plot will be opened with the closest 10 neighbors in the space.
The neighbors are:

1. Five Cas proteins, including Cas3, Csc1, Csc2 and two variants on Csc3.
2. Five Hypothetical proteins, all with a trusted prediction of a "Prokaryotic Defense System".
   Hovering on a specific bar will show extended information on each gene.<br>

This strengthens the confidence that this protein is related to Defense mechanisms, and more specifically to Subtype I in which Csc proteins are apparent.<br>

_*Note*_: distances were calculated on a high dimensional space, thus elements might not seem to be close in the 2D space map.<br>

#### Taxonomic mapping of genes in a family

Selecting the `TAX MAP` tab will display a bar plot showcasing the top 10 taxonomic orders associated with the gene family `hypo.clst.15503442`.<br>
The plot also indicates the percentage of genes from this family that have a known taxonomy in the database—specifically, in this case, 79.17% of genes were mapped.
