FROM python:3.11 AS build

WORKDIR /opt/certbot/plugin

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python - && \
ln -s ~/.local/bin/poetry /usr/bin/ && \
poetry config virtualenvs.create false

# Build plugin
COPY [".", "."]
RUN poetry build


#################################

FROM certbot/certbot

# Install the DNS plugin
COPY --from=build /opt/certbot/plugin/dist/*.whl /opt/certbot/src/plugin/
RUN python tools/pip_install.py --no-cache-dir /opt/certbot/src/plugin/*.whl
