# Certbot image to build on (e.g. certbot/certbot:amd64-v0.35.0)
ARG BASE_IMAGE
FROM ${BASE_IMAGE}

# Copy Certbot DNS plugin code
ARG CERTBOT_DNS_CLOUDNS_VERSION
COPY dist/certbot_dns_cloudns-${CERTBOT_DNS_CLOUDNS_VERSION}-py3-none-any.whl /opt/certbot/src/plugin/

# Install the DNS plugin
RUN python tools/pip_install.py --no-cache-dir /opt/certbot/src/plugin/*.whl
