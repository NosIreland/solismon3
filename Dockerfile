FROM python:3-alpine

EXPOSE 18000

LABEL MAINTAINER="Andrius Kozeniauskas"
LABEL NAME=solismon3

RUN mkdir /solismon3
COPY *.py *.txt /solismon3/

WORKDIR /solismon3

RUN pip install --upgrade pip \
  && pip3 install -r requirements.txt

CMD [ "python", "./main.py" ]