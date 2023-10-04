FROM python:3.11-slim-buster

ENV PYTHONUNBUFFERED=1

WORKDIR /s3purger

COPY ./bin .
COPY ./bin/pip.conf /etc
RUN pip3 install -r requirements.txt

CMD [ "python3", "app.py"]
