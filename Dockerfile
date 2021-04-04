FROM python:3-slim
ARG req
COPY ./requirements /requirements
RUN pip install --upgrade pip
RUN pip install -r /requirements/${req}.txt
COPY . /app
WORKDIR /app
