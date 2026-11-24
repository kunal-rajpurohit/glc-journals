# Dockerfile for the pre-built GLC Mumbai Journals site (Janeway).
# The database (db.sqlite3) already has the press, all 9 journals, sample
# content and the superuser account baked in — this image just runs it.
FROM python:3.12-slim

# System packages needed to build a couple of Python dependencies (lxml, Pillow),
# plus git, since requirements.txt pulls a couple of packages straight from GitHub.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       git build-essential libxml2-dev libxslt1-dev zlib1g-dev libjpeg-dev libmagic1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV JANEWAY_SETTINGS_MODULE=core.settings \
    PYTHONUNBUFFERED=1 \
    DB_NAME=/app/db.sqlite3

WORKDIR /app/src
EXPOSE 8000

COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
