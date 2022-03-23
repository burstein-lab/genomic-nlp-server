FROM node:lts-buster

WORKDIR /app

# This enforces hot-loading files in docker.
ENV CHOKIDAR_USEPOLLING=true

CMD yarn && yarn serve
