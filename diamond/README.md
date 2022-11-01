# Deployment

Based on https://medium.com/google-developer-experts/building-a-flask-app-using-docker-and-deploy-to-google-cloud-run-8f311ad36040

```bash
docker build . -t us-central1-docker.pkg.dev/genomic-nlp/cloudrun/diamond
docker push us-central1-docker.pkg.dev/genomic-nlp/cloudrun/diamond:latest
```
