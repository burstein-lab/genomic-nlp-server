FROM python:3.10-buster

# Enforces .venv to be in project.
ENV PIPENV_VENV_IN_PROJECT=true
ENV DEBIAN_FRONTEND=noninteractive
# Enforces hot-loading files in docker.
ENV CHOKIDAR_USEPOLLING=true

WORKDIR /app

RUN apt update && apt install -y npm curl docker.io
RUN pip install --upgrade pip
RUN pip install pipenv
RUN sh -c "$(curl -fsSL https://starship.rs/install.sh)" -- --yes
RUN npm install --global yarn
# Required for cv2. https://stackoverflow.com/questions/55313610/importerror-libgl-so-1-cannot-open-shared-object-file-no-such-file-or-directo
RUN apt-get install -y libgl1

RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get install -y nodejs

RUN echo 'eval "$(starship init bash)"' >> /root/.bashrc
