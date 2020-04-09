FROM python:3.8-slim-buster

RUN /bin/mkdir /app

COPY . /app

WORKDIR /app

RUN python ./setup.py install

CMD ["snptk"]
