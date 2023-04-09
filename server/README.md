# Deployment

Based on https://medium.com/google-developer-experts/building-a-flask-app-using-docker-and-deploy-to-google-cloud-run-8f311ad36040

```bash
pipenv requirements > requirements.txt
docker build . -t us-central1-docker.pkg.dev/genomic-nlp/cloudrun/gnlp-server
docker push us-central1-docker.pkg.dev/genomic-nlp/cloudrun/gnlp-server:latest
```

## Local

```bash
docker build . -t gnlp-server
docker run -it -e PORT=80 -p 8000:80 --rm gnlp-server
```

# Plot and pickle

```bash
pipenv run python plot.py --outdir=../web/public/map --fmt png --max-zoom 5
```
