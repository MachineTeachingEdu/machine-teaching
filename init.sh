#!/usr/bin/env bash

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] ; then
    (cd machineteaching; python manage.py createsuperuser --no-input)
fi
(cd machineteaching; gunicorn machineteaching.wsgi --user www-data --bind 0.0.0.0:8010 --workers 3) &
nginx -g "daemon off;"