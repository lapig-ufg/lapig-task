FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
ENV URL_TO_APPLICATION_GITHUB='https://github.com/lapig-ufg/tiles.git' \
    BRANCH='main' \
    TILES_ENV='production'
    
LABEL maintainer="Jario Matos da Rocha <jairo@jairomr.com.br>"

WORKDIR /home/suporte


RUN apt-get update && apt-get install --no-install-recommends -y curl build-essential git nano

RUN useradd -rm -d /home/suporte -s /bin/bash  -g root -G sudo -u 1001 suporte
COPY . .

RUN chown -R suporte:1001 /home/suporte

USER suporte


RUN uv venv

