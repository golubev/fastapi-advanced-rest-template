FROM python:3.11-bullseye

RUN apt update && apt install -y \
        nano \
    && rm -rf /var/lib/apt/lists/*

ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ARG DOCKER_BACKEND_UID
RUN groupadd -g $DOCKER_BACKEND_UID -o appuser
RUN useradd -m -u $DOCKER_BACKEND_UID -g $DOCKER_BACKEND_UID -o -s /bin/bash appuser

COPY ./requirements*.txt .
RUN pip install --requirement ./requirements.dev.txt

USER appuser
