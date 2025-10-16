# Build frontend assets in separate image
FROM node:24.10.0-slim AS assets
WORKDIR /app

# Copy project files into the docker image
# See https://pnpm.io/cli/fetch#usage-scenario
COPY libraries/libraries/static/ libraries/libraries/static
COPY pnpm-lock.yaml gulpfile.js package.json ./
# stops npm update notifier
ENV CI=true
ENV PNPM_HOME=/pnpm
ENV PATH="$PNPM_HOME:$PATH"
RUN npm install --global corepack@latest && npm cache clean --force
RUN corepack enable
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm fetch --prod && pnpm install -r --offline --prod --frozen-lockfile
# this builds files into /app/libraries/static, see gulpfile
RUN npx gulp build

# Install dependencies with `uv`. Python version must match mise.toml and pyproject.toml.
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder
WORKDIR /app

# Install non-python dependencies, rsync needed to fetch media files
RUN apt-get update && apt-get install -y --no-install-recommends \
    # build-essential & libssl-dev needed to build uWSGI
    build-essential \
    libssl-dev \
    # needed to build psycopg2
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies into system python
# OpenSSL 3.0 compatibility flags for uWSGI
ENV CFLAGS="-Wno-error=deprecated-declarations"
ENV CPPFLAGS="-DOPENSSL_API_COMPAT=0x10100000L -DOPENSSL_NO_DEPRECATED"
ENV LDFLAGS="-lssl -lcrypto"
ENV UV_COMPILE_BYTECODE=1
# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy
COPY pyproject.toml uv.lock /app/
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev --no-install-project

# Runtime image without builder tools like `uv`
# TODO migrate both python images to Trixie Debian python:3.13.9-slim-trixie
FROM python:3.13-slim-bookworm AS runtime
WORKDIR /app/libraries
# Collect our compiled static files from the assets image
COPY --from=assets /app/libraries/static /app/libraries/libraries/static
# Copy our python environment from the uv builder image
COPY --from=builder /app/.venv /app/.venv

# Copy application code. Copy only libraries dir so that changes to docs,
# k8s, config files, etc. don't invalidate the docker cache
# https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#leverage-build-cache
COPY libraries /app/libraries/
# Web server configuration file used in CMD
COPY kubernetes/uwsgi.ini /app/libraries/

# pgsl needed for `pg_dump` and `python manage.py dbshell`
RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Settings environment variable
ENV DJANGO_SETTINGS_MODULE=libraries.settings
# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Collect static files from deps, needs DOCKER_BUILD so base.py settings work
RUN DOCKER_BUILD=true python /app/libraries/manage.py collectstatic --no-input

# Make port 80 available to the world outside this container
EXPOSE 8000

# Start uWSGI web server
CMD ["uwsgi", "--ini", "/app/libraries/uwsgi.ini"]
