FROM bschiffthaler/diamond

# https://stackoverflow.com/a/62555259
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY gene2vec_w5_v300_tf24_annotation_extended_2021-10-03.w2v .
COPY gene2vec_w5_v300_tf24_annotation_extended_2021-10-03.w2v.trainables.syn1neg.npy .
COPY gene2vec_w5_v300_tf24_annotation_extended_2021-10-03.w2v.wv.vectors.npy .
COPY app.py .

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:8080", "app:app", "--timeout", "300"]