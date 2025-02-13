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

# Build the Django application itself. Python version matches the one in mise.toml and pyproject.toml.
FROM python:3.10.13-bullseye AS libraries
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
WORKDIR /app/libraries
ENV PYTHONPATH=/app:/app/libraries

# Install non-python dependencies, rsync needed to fetch media files
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    rsync \
    && rm -rf /var/lib/apt/lists/*

# Install postgresl-client, needed for
# `kubectl exec pg_dump` and `kubectl django-admin dbshell`
RUN echo "deb http://apt.postgresql.org/pub/repos/apt bullseye-pgdg main" | tee -a /etc/apt/sources.list.d/pgdg.list && \
    curl -sS https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/apt.postgresql.org.gpg && \
    apt-get update -y && \
    apt-get install --no-install-recommends postgresql-client-14 -y \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies into system python
ENV UV_COMPILE_BYTECODE=1
ENV UV_PROJECT_ENVIRONMENT=/usr/local
ENV UV_PYTHON_PREFERENCE=system
COPY pyproject.toml uv.lock /app/
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev --no-install-project
# ? do I need another uv sync after COPY libraries /app/libraries?

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
