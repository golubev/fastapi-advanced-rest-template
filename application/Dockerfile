FROM python:3.11-bullseye

WORKDIR /usr/src/app

COPY ./requirements*.txt .
RUN pip install --requirement ./requirements.dev.txt

ARG DOCKER_BACKEND_UID
RUN groupadd -g $DOCKER_BACKEND_UID -o appuser
RUN useradd -m -u $DOCKER_BACKEND_UID -g $DOCKER_BACKEND_UID -o -s /bin/bash appuser
USER appuser

CMD [ "python", "./main.py" ]
