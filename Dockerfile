FROM python:slim

# for printing version (commit hash) of api in swagger
WORKDIR /
COPY .git/ ./.git/

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./src ./
