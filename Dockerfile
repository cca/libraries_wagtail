FROM node:14-alpine AS fe_tools
WORKDIR /app

# Install yarn and other dependencies via apk
RUN apk update && apk add yarn git rsync python g++ make bash vim && rm -rf /var/cache/apk/*


## Copy project files into the docker image
COPY libraries/libraries/static/ libraries/static

WORKDIR /app/libraries/static/


# Build the application itself.
FROM python:3.6-stretch as libraries
WORKDIR /app
ENV PYTHONPATH /app:/app/libraries/apps

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

# Install application code.
COPY . .

# Settings environment variable
ENV DJANGO_SETTINGS_MODULE libraries.libraries.settings

# Collect static files
COPY libraries/libraries/static/ libraries/libraries/static
#RUN if [ "$DEVBUILD" = true ]; then echo "skipping collectstatic..."; else SECRET_KEY=none django-admin.py collectstatic --noinput --clear -v 0; fi

# Make port 80 available to the world outside this container
EXPOSE 8000

# Start Django
CMD ["uwsgi", "--ini", "kubernetes/uwsgi.ini"]
