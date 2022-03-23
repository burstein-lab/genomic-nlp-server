# genomic-nlp-server

# Setup

```bash
docker run -v $PWD:/app --rm -it gnlp-server bash

# Inside the container
cd gnlp-app
```

# Initial Setup

```bash
docker build . -t gnlp-server

yarn create vite gnlp-app --template vue
```