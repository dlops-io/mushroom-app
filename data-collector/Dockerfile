# Use the official Debian-hosted Python image
FROM python:3.8-slim-buster

ARG DEBIAN_PACKAGES="build-essential git libopenblas-base libomp-dev"

# Prevent apt from showing prompts
ENV DEBIAN_FRONTEND=noninteractive
# Tell pipenv where the shell is
ENV PYENV_SHELL=/bin/bash

# Tell Python to disable buffering so we don't lose any logs.
ENV PYTHONUNBUFFERED=1

ARG DEBIAN_PACKAGES="build-essential git wget curl unzip gnupg"

# Ensure we have an up to date baseline, install dependencies 
RUN set -ex; \
    for i in $(seq 1 8); do mkdir -p "/usr/share/man/man${i}"; done && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends $DEBIAN_PACKAGES && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip && \
    pip install pipenv && \
    useradd -ms /bin/bash app -d /home/app -u 1000 -p "$(openssl passwd -1 Passw0rd)" && \
    mkdir -p /app && \
    chown app:app /app

# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

# install chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# set display port to avoid crash
ENV DISPLAY=:99

RUN pip install --no-cache-dir --upgrade pip
RUN pip install pipenv

WORKDIR /app

# Install python packages
ADD Pipfile Pipfile.lock /app/
RUN pipenv sync

# Add source code
ADD . /app

# Entry point
ENTRYPOINT ["/bin/bash","./docker-entrypoint.sh"]
