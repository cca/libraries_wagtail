# https://hub.docker.com/_/node
FROM node:20.11.0-slim AS assets
# we build static assets (JS, CSS, application images) in a node container
WORKDIR /app

# Copy project files into the docker image
# See https://pnpm.io/cli/fetch#usage-scenario
COPY libraries/libraries/static/ libraries/libraries/static
COPY pnpm-lock.yaml gulpfile.js package.json ./
# stops npm update notifier
ENV CI=true
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm fetch --prod
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install -r --offline --prod --frozen-lockfile
# this builds files into /app/libraries/static, see gulpfile
RUN npx gulp build

# Build the Django application itself.
FROM python:3.10.13-bullseye as libraries
WORKDIR /app
ENV PYTHONPATH /app:/app/libraries

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
    apt-get install postgresql-client-14 -y \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
ENV PIP_ROOT_USER_ACTION ignore
RUN pip install pipenv
COPY Pipfile Pipfile.lock /app/
# --system: install deps in system python, --deploy: throw error if lockfile doesn't match Pipfile
RUN pipenv install --system --deploy

# Collect our compiled static files from the assets image
COPY --from=assets /app/libraries/libraries/static/ libraries/libraries/static

# Install application code. Copy only libraries dir so that changes to docs,
# k8s, config files, etc. don't invalidate the docker cache
# https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#leverage-build-cache
COPY libraries libraries/
# if collectstatic throws an error during build & this dir doesn't exist, it
# can't be created for some reason, breaks the build
RUN mkdir /app/libraries/logs
COPY kubernetes/uwsgi.ini libraries/

# Settings environment variable
ENV DJANGO_SETTINGS_MODULE libraries.settings

RUN python libraries/manage.py collectstatic --no-input

WORKDIR /app/libraries

# Make port 80 available to the world outside this container
EXPOSE 8000

# Start Django
CMD ["uwsgi", "--ini", "uwsgi.ini"]
# Use the command below for debugging; it forces the container to run forever
# CMD exec /bin/bash -c "trap : TERM INT; sleep infinity & wait"
