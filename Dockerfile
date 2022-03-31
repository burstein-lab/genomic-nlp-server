FROM python:3.10-buster

# Enforces .venv to be in project.
ENV PIPENV_VENV_IN_PROJECT=true
ENV DEBIAN_FRONTEND=noninteractive
# Enforces hot-loading files in docker.
ENV CHOKIDAR_USEPOLLING=true

WORKDIR /app

RUN apt update && apt install -y npm curl
RUN pip install --upgrade pip
RUN pip install pipenv
RUN sh -c "$(curl -fsSL https://starship.rs/install.sh)" -- --yes
RUN npm install --global yarn

RUN curl -fsSL https://deb.nodesource.com/setup_17.x | bash -
RUN apt-get install -y nodejs

#WORKDIR /app
#RUN yarn install
