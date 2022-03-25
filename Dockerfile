FROM node:14-alpine AS assets
# we build static assets (JS, CSS, application images) in a node container
WORKDIR /app

## Copy project files into the docker image
COPY libraries/libraries/static/ libraries/libraries/static
COPY package.json package-lock.json gulpfile.js ./

RUN npm install --no-fund
RUN npx gulp build

# Build the Django application itself.
FROM python:3.6-stretch as libraries
WORKDIR /app
ENV PYTHONPATH /app:/app/libraries

# Install non-python dependencies
# Step 0: add all repos to sources.list
RUN printf "deb http://ftp.debian.org/debian/ stretch main\ndeb-src http://ftp.debian.org/debian/ stretch main\ndeb http://security.debian.org stretch/updates main\ndeb-src http://security.debian.org stretch/updates main" > /etc/apt/sources.list

RUN apt-get update && apt-get install -y --no-install-recommends wget ca-certificates && \
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
    # Step 5: Cleanup apt cache and lists
    rm -rf /var/cache/apt/* /var/lib/apt/lists/*

# Install requirements - done in a separate step so Docker can cache it.
COPY libraries/requirements.txt requirements/requirements.txt
RUN pip install -r requirements/requirements.txt

# Collect our compiled static files from the assets image
COPY --from=assets /app/libraries/libraries/static/ libraries/libraries/static

# Install application code. Copy only libraries dir so that changes to docs,
# k8s, config files, etc. don't invalidate the docker cache
# https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#leverage-build-cache
COPY libraries libraries/
# if collectstatic throw an error during build & this dir doesn't exist, it
# can't be created for some reason, breaks the build
RUN mkdir /app/libraries/logs

# Settings environment variable
ENV DJANGO_SETTINGS_MODULE libraries.settings

RUN python libraries/manage.py collectstatic --no-input

# Make port 80 available to the world outside this container
EXPOSE 8000

# Start Django
CMD ["uwsgi", "--ini", "kubernetes/uwsgi.ini"]
# Use the command below for debugging; it forces the container to run forever
# CMD exec /bin/bash -c "trap : TERM INT; sleep infinity & wait"
