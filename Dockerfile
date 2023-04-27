# https://hub.docker.com/_/node
FROM node:18.15-alpine3.17 AS assets
# we build static assets (JS, CSS, application images) in a node container
WORKDIR /app

# Copy project files into the docker image
# See https://pnpm.io/cli/fetch#usage-scenario
COPY libraries/libraries/static/ libraries/libraries/static
COPY pnpm-lock.yaml gulpfile.js package.json ./
ENV NPM_CONFIG_UPDATE_NOTIFIER false
RUN npm install --location=global pnpm@8.3 --no-fund --no-audit
RUN pnpm fetch --prod
RUN pnpm install -r --offline --prod
# this builds files into /app/libraries/static, see gulpfile
RUN npx gulp build

# Build the Django application itself.
FROM python:3.7.16-bullseye as libraries
WORKDIR /app
ENV PYTHONPATH /app:/app/libraries

# Install non-python dependencies
# Step 0: add all repos to sources.list
RUN printf "deb http://ftp.debian.org/debian/ stable main\ndeb-src http://ftp.debian.org/debian/ stable main" > /etc/apt/sources.list

RUN apt-get update && apt-get install -y --no-install-recommends wget ca-certificates && \
    # @TODO We need to update the debian dist from the list https://ftp.postgresql.org/pub/repos/apt/dists/
    # when it changes...is there a better way like how we use debian.org's "stable" above?
    # Step 1: Add the PGDG repo into the sources list
    echo "deb https://ftp.postgresql.org/pub/repos/apt/ bullseye-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    # Step 2: Install wget and ca-certificates to be able to add a cert for PGDG
    # Step 3: Add the PDGD cert
    wget --no-check-certificate --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && \
    # Step 4: Install dependencies
    apt-get update && apt-get install -y --no-install-recommends \
    # We need postgresql-client to be able to use
    # `kubectl exec pg_dump` and `kubectl django-admin dbshell`
    postgresql-client-9.6 \
    # Install rsync to be able to fetch media files
    rsync && \
    # Step 5: Cleanup apt cache and lists
    rm -rf /var/cache/apt/* /var/lib/apt/lists/*

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
