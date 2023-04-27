FROM python:3.11-alpine

RUN apk add --update \
    curl \
    && rm -rf /var/cache/apk/*

WORKDIR /usr/src/app

COPY ./requirements.txt .
RUN python3 -m pip install --no-cache-dir --requirement ./requirements.txt

CMD [ "python", "./main.py" ]
