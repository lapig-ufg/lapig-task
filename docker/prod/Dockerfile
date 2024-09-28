FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
ENV URL_TO_APPLICATION_GITHUB='https://github.com/lapig-ufg/tiles.git' \
    BRANCH='main' \
    TILES_ENV='production'
    
LABEL maintainer="Jario Matos da Rocha <jairo@jairomr.com.br>"



RUN apt-get update && apt-get install --no-install-recommends -y curl build-essential git nano

    
RUN useradd -rm -d /home/lapig -s /bin/bash  -g root -G sudo -u 1001 lapig
COPY ./pyproject.toml /home/lapig/pyproject.toml
COPY . .

RUN chown -R lapig:lapig /home/lapig

USER lapig
WORKDIR /home/lapig
RUN uv venv

