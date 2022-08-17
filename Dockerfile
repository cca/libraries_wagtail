# syntax=docker/dockerfile:1.2
# ^^^ use docker buildkit https://docs.docker.com/develop/develop-images/build_enhancements/
FROM node:16-alpine AS assets
# we build static assets (JS, CSS, application images) in a node container
WORKDIR /app

# Copy project files into the docker image
# See https://pnpm.io/cli/fetch#usage-scenario
COPY libraries/libraries/static/ libraries/libraries/static
COPY pnpm-lock.yaml gulpfile.js package.json ./
RUN --mount=type=cache,target=/root/.npm npm install --location=global pnpm@7.4 gulp-cli@2.3 --no-fund --no-audit
RUN --mount=type=cache,target=/root/.local/share/pnpm/store pnpm fetch --prod
RUN --mount=type=cache,target=/root/.local/share/pnpm/store pnpm install -r --frozen-lockfile --offline --prod
RUN gulp build

# @TODO this would be faster if python build was in a second intermediary image
# so we have node/pnpm, python/pip(env), & apt-get doing work in parallel
# e.g. see https://sourcery.ai/blog/python-docker/
# Build the Django application itself.
FROM python:3.7.13 as libraries
WORKDIR /app
ENV PYTHONPATH /app:/app/libraries

# Install non-python dependencies
# Step 0: add all repos to sources.list
RUN printf "deb http://ftp.debian.org/debian/ stretch main\ndeb-src http://ftp.debian.org/debian/ stretch main\ndeb http://security.debian.org stretch/updates main\ndeb-src http://security.debian.org stretch/updates main" > /etc/apt/sources.list

RUN rm -f /etc/apt/apt.conf.d/docker-clean
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get install -y --no-install-recommends wget ca-certificates && \
    # Step 1: Add the PGDG repo into the sources list
    echo "deb http://apt.postgresql.org/pub/repos/apt/ stretch-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    # Step 2: Install wget and ca-certificates to be able to add a cert for PGDG
    # Step 3: Add the PDGD cert
    wget --no-check-certificate --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && \
    # Step 4: Install dependencies
    apt-get update && apt-get install -y --no-install-recommends \
    # We need postgresql-client to be able to use
    # `kubectl exec pg_dump` and `kubectl djnago-admin dbshell`
    postgresql-client-9.6 \
    # Install rsync to be able to fetch media files
    rsync && \
    # Step 5: Cleanup apt lists
    rm -rf /var/lib/apt/lists/*

# Install python dependencies with caching
ENV PIP_CACHE_DIR="/root/.cache/pip"
ENV PIPENV_CACHE_DIR="/root/.cache/pipenv"
RUN mkdir -p ${PIP_CACHE_DIR} ${PIPENV_CACHE_DIR}
RUN --mount=type=cache,target=/root/.cache pip install pipenv
COPY Pipfile Pipfile.lock /app/
# --system: install deps in system python, --deploy: throw error if lockfile doesn't match Pipfile
RUN --mount=type=cache,target=/root/.cache pipenv install --system --deploy

# Collect our compiled static files from the assets image
COPY --from=assets /app/libraries/libraries/static/ libraries/libraries/static

# Install application code. Copy only libraries dir so that changes to docs,
# k8s, config files, etc. don't invalidate the docker cache
# https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#leverage-build-cache
COPY libraries libraries/
# if collectstatic throws an error during build & this dir doesn't exist, it
# can't be created for some reason, breaks the build
RUN mkdir /app/libraries/logs
COPY kubernetes/uwsgi.ini kubernetes/

# Settings environment variable
ENV DJANGO_SETTINGS_MODULE libraries.settings

RUN python libraries/manage.py collectstatic --no-input

# Make port 80 available to the world outside this container
EXPOSE 8000

# Start Django
CMD ["uwsgi", "--ini", "kubernetes/uwsgi.ini"]
# Use the command below for debugging; it forces the container to run forever
# CMD exec /bin/bash -c "trap : TERM INT; sleep infinity & wait"
