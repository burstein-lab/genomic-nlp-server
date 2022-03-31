# genomic-nlp-server

# Setup

```bash
docker run -v $PWD:/app --rm -it gnlp bash

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