FROM python:3.11-bullseye

WORKDIR /usr/src/app

# Linux packages required in the local dev environment
RUN apt-get update && apt-get install -y \
        locales \
        nano \
    && rm -rf /var/lib/apt/lists/* \
    # fix vscode git pre-commit hook locale warning issue
    && sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
    && dpkg-reconfigure --frontend=noninteractive locales

ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ARG DOCKER_BACKEND_UID
RUN groupadd -g $DOCKER_BACKEND_UID -o appuser
RUN useradd -m -u $DOCKER_BACKEND_UID -g $DOCKER_BACKEND_UID -o -s /bin/bash appuser

ENV POETRY_HOME=/opt/poetry \
    POETRY_VERSION="1.4.2" \
    POETRY_VIRTUALENVS_CREATE=false
RUN curl -sSL https://install.python-poetry.org | python
ENV PATH="$POETRY_HOME/bin:$PATH"

COPY ./pyproject.toml ./poetry.lock ./
RUN poetry install --no-root

USER appuser
