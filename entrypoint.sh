#!/bin/sh

# Migrate
cd sport_league
python manage.py makemigrations
python manage.py migrate

# Compile messages
#python manage.py compilemessages

exec "$@"
