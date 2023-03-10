#!/bin/sh

# Migrate
python manage.py makemigrations
python manage.py migrate

# Compile messages
python manage.py compilemessages

exec "$@"
