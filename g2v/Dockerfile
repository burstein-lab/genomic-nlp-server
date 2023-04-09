FROM python:3.10

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY gene2vec_w5_v300_tf24_annotation_extended_2021-10-03.w2v .
COPY gene2vec_w5_v300_tf24_annotation_extended_2021-10-03.w2v.trainables.syn1neg.npy .
COPY gene2vec_w5_v300_tf24_annotation_extended_2021-10-03.w2v.wv.vectors.npy .
COPY common.py .
COPY app.py .

ENTRYPOINT ["gunicorn"  , "-b", "0.0.0.0:8080", "app:app"]
