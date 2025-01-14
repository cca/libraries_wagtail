#!/bin/bash -e

until psql -c '\l' -o /dev/null; do
  echo >&2 "$(date +%Y%m%dt%H%M%S) Postgres is unavailable - sleeping"
  sleep 1
done

cd /app/libraries || (echo "Unable to enter /app/libraries"  >&2; exit 1)
python manage.py update_index &
python manage.py runserver 127.0.0.1:8000
