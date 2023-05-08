# :dna: GeNLP
**GeNLP: An interactive web application for microbial gene exploration and prediction**

#### :globe_with_meridians: Visit the [GeNLP website](http://gnlp.bursteinlab.org/)

The quick user guide is available at our [GitHub wiki](https://github.com/burstein-lab/genomic-nlp-server/wiki)

![](https://github.com/burstein-lab/genomic-nlp-server/blob/main/img/demo.gif)


This repository contains the implementation of *GeNLP*, a user-friendly web server to explore gene relationships!<br>
The server is based on a pre-trained published language model:<br>
"[Deciphering microbial gene function using natural language processing](https://www.nature.com/articles/s41467-022-33397-4)"<br>

Weights and trained model are available on the paper's [GitHub repository](https://github.com/burstein-lab/genomic-nlp).

## Getting Started
This is a web service and does not require any previous installation.<br/>
In this use case we demonstrate the core features of the web-server together with potential biological insights.

### Search for sequence
We start by using the server on an uknown protein sequence, with no mapping to existing databases.

```
>Protein1
MTKLELLVSVMVDGKWYSTDDLVSRVGHRFSATKHVAEKQGYQFEKRREGMRFEYRMVST
TIELAR
```
To obtain a prediction, go to the search panel and choose `Sequence`. The app will run in the background to find the matching
gene identifier in our model. This process might take few minutes :hugs:<br>

After the search is completed, the predicted gene identifier and its corresponding predictions score will be avilable for download.
We will use the predicted gene idetifier: `hypo.clst.15503442` to explore `Protein1`.<br>

### Explore prediction
Go to the search bar and select *KO\Hypo* mode, in the search bat type the identifier name (it should auto-complete).<br>
The highlighted dot on the space markes `hypo.clst.15503442`. The panel will show the following information:
- Gene Prediction
- Trusted prediction
- Neighbors
- Gene prediction
<br>
#### Gene prediction
The predicted class is *Prokaryotic Defense System* and the prediction is *reliable* (trusted prediction is True).<br>
By clicking on `GENE PREDICTIONS` a panel will open showing all scores recived by the model for the different classes. Here, the 
*Prokaryotic Defense System* prediction was unequivocal, with a score closed to 1 (possible scores are between 0 to 1).<br>

#### Analyzing neighbors


