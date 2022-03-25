#!/bin/bash -e

until psql -c '\l' -o /dev/null; do
  echo >&2 "$(date +%Y%m%dt%H%M%S) Postgres is unavailable - sleeping"
  sleep 1
done

python /app/libraries/manage.py runserver 0.0.0.0:8000
