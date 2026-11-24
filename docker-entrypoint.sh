#!/usr/bin/env bash
# Runs once each time the container starts. The database is already migrated
# and seeded, but this is a cheap, safe no-op check in case the image is
# ever rebuilt against a newer copy of the code.
set -e
cd /app/src
python manage.py migrate --noinput
exec "$@"
