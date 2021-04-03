FROM python:3.10 AS build

WORKDIR /opt/certbot/plugin

# Install poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python - && \
    ln -s ~/.poetry/bin/poetry /usr/bin/ && \
    poetry config virtualenvs.create false

# Build plugin
COPY [".", "."]
RUN poetry build


#################################

FROM certbot/certbot

# Install the DNS plugin
COPY --from=build /opt/certbot/plugin/dist/*.whl /opt/certbot/src/plugin/
RUN python tools/pip_install.py --no-cache-dir /opt/certbot/src/plugin/*.whl
