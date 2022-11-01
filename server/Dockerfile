FROM python:3.10

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY app.py .
COPY coords.py .
COPY model_data.pkl .
COPY label_to_word.pkl .
COPY data_embeddings_gene2vec_w5_v300_tf24_annotation_extended_2021-10-03.w2v .
COPY data_embeddings_gene2vec_w5_v300_tf24_annotation_extended_2021-10-03.w2v.wv.vectors.npy .
COPY data_embeddings_gene2vec_w5_v300_tf24_annotation_extended_2021-10-03.w2v.trainables.syn1neg.npy .
COPY data_gene_names_to_ko.pkl .

ENTRYPOINT ["gunicorn"  , "-b", "0.0.0.0:8080", "app:app"]
