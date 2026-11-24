#!/usr/bin/env bash
cd "$(dirname "$0")"
[ -d .venv ] && . .venv/bin/activate
cd src
python manage.py runserver 0.0.0.0:8000
