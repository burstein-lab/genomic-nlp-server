FROM bschiffthaler/diamond

# https://stackoverflow.com/a/62555259
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY app.py .

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:8080", "app:app", "--timeout", "300"]