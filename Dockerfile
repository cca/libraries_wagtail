# https://hub.docker.com/_/node
FROM node:20.18.1-slim AS assets
# we build static assets (JS, CSS, application images) in a node container
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
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm fetch --prod
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install -r --offline --prod --frozen-lockfile
# this builds files into /app/libraries/static, see gulpfile
RUN npx gulp build

# Build the Django application itself. Python version must match mise.toml and pyproject.toml.
FROM python:3.13.7-bookworm AS libraries
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
WORKDIR /app/libraries
ENV PYTHONPATH=/app:/app/libraries

# Install non-python dependencies, rsync needed to fetch media files
RUN apt-get update && apt-get install -y --no-install-recommends \
    # build-essential & libssl-dev needed to build uWSGI
    build-essential \
    ca-certificates \
    libssl-dev \
    # needed for `pg_dump` and `python manage.py dbshell`
    postgresql-client \
    rsync \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies into system python
# OpenSSL 3.0 compatibility flags for uWSGI
ENV CFLAGS="-Wno-error=deprecated-declarations"
ENV CPPFLAGS="-DOPENSSL_API_COMPAT=0x10100000L -DOPENSSL_NO_DEPRECATED"
ENV LDFLAGS="-lssl -lcrypto"
ENV UV_COMPILE_BYTECODE=1
ENV UV_PROJECT_ENVIRONMENT=/usr/local
ENV UV_PYTHON_PREFERENCE=system
COPY pyproject.toml uv.lock /app/
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev --no-install-project

# Collect our compiled static files from the assets image
COPY --from=assets /app/libraries/static /app/libraries/libraries/static

# Install application code. Copy only libraries dir so that changes to docs,
# k8s, config files, etc. don't invalidate the docker cache
# https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#leverage-build-cache
COPY libraries /app/libraries/
COPY kubernetes/uwsgi.ini /app/libraries/

# Settings environment variable
ENV DJANGO_SETTINGS_MODULE=libraries.settings

RUN DOCKER_BUILD=true python /app/libraries/manage.py collectstatic --no-input

# Make port 80 available to the world outside this container
EXPOSE 8000

# Start Django
CMD ["uwsgi", "--ini", "/app/libraries/uwsgi.ini"]
