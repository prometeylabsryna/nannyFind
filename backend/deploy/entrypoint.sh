#!/bin/sh
set -e

python3 manage.py migrate --noinput
if [ "${RUN_SEED_DEMO:-false}" = "true" ]; then
  python3 manage.py seed_demo
fi
python3 manage.py collectstatic --noinput
exec daphne -b 0.0.0.0 -p 8000 config.asgi:application
