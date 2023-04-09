FROM python:3.10

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY common.py .
COPY app.py .

ENTRYPOINT ["gunicorn"  , "-b", "0.0.0.0:8080", "app:app"]
