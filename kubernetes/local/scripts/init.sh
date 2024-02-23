#!/bin/bash -e

until psql -c '\l' -o /dev/null; do
  echo >&2 "$(date +%Y%m%dt%H%M%S) Postgres is unavailable - sleeping"
  sleep 1
done

cd /app/libraries && python manage.py runserver localhost:8000
