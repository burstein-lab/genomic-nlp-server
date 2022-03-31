# genomic-nlp-server

# Setup

```bash
docker run -v /var/run/docker.sock:/var/run/docker.sock -v $PWD:/app --rm -it gnlp bash

# Inside the container
pipenv install

cd gnlp-app
yarn dev
```

# Initial Setup

```bash
docker build . -t gnlp

pipenv install
yarn create vite gnlp-app --template vue
```

```
docker tag gnlp notofir/gnlp
docker push notofir/gnlp
```
