# Deployment

Following https://devcenter.heroku.com/articles/container-registry-and-runtime (https://github.com/heroku/alpinehelloworld)

```bash
heroku container:push web -a gnlp-server
heroku container:release web -a gnlp-server
heroku open -a gnlp-server # Or go to https://gnlp-server.herokuapp.com/
heroku logs -a gnlp-server --tail
```

## Local

```bash
docker build . -t gnlp-server
docker run -it -e PORT=80 -p 8000:80 --rm gnlp-server
```

# Plot and pickle

```bash
pipenv run python server/scripts/plot.py --data model_data.pkl --outdir=web/src/assets/map --fmt png --max-zoom 5
```
