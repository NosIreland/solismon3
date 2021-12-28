FROM python:3.8.0-alpine

EXPOSE 18000

LABEL MAINTAINER="Andrius Kozeniauskas"
LABEL NAME=solismon3

RUN mkdir /solismon3
COPY . /solismon3
WORKDIR /solismon3
RUN apk --update add python py-pip openssl ca-certificates py-openssl wget
RUN apk --update add --virtual build-dependencies libffi-dev openssl-dev python-dev py-pip build-base \
  && pip install --upgrade pip \
  && pip install -r requirements.txt \
  && apk del build-dependencies

CMD [ "python", "./main.py" ]