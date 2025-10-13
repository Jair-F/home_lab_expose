# FROM mcr.microsoft.com/vscode/devcontainers/base:ubuntu-22.04
FROM ubuntu:22.04
# FROM python:3.10.19-alpine3.22
# FROM mcr.microsoft.com/devcontainers/base:alpine-3.18
USER root

RUN mkdir /app
WORKDIR /app
EXPOSE 80

RUN apt update
RUN apt upgrade -y
RUN apt install -y python3 python3-pip sudo

COPY . .
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

RUN chmod -R +x *
RUN env/install_cloudflare.sh

ENTRYPOINT ["python3", "main.py", " ; $@"]
