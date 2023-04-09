FROM python:3.10

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY model_data.pkl .
COPY gene_names_to_ko.pkl .
COPY label_to_word.pkl .
COPY app.py .
COPY common.py .

ENTRYPOINT ["gunicorn"  , "-b", "0.0.0.0:8080", "app:app"]
