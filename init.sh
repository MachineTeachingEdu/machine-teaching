#!/bin/sh

echo $ENVIRONMENT
if [ "$ENVIRONMENT" = "development" ]; then
    echo "Preparing image for development"
    /wait 
    cd /app/machineteaching
    # python manage.py makemigrations --noinput
    echo "Running migrations"
    python manage.py migrate -v 3 --noinput
    export DJANGO_SETTINGS_MODULE=machineteaching.settings
    opentelemetry-bootstrap --action=install
    echo "Starting server on port $PORT"
    python manage.py runserver 0.0.0.0:$PORT

else
    echo "Preparing image for production"
    echo "IP Address:"
    curl curlmyip.org
    # cd /app/machineteaching
    mkdir -p staticfiles
    echo "Will compile messages"
    python manage.py compilemessages
    echo "Will collect static"
    python manage.py collectstatic --noinput
    python manage.py migrate
    python manage.py compilemessages
    if [ -z "${DJANGO_SUPERUSER_USERNAME}" ]; then
        echo "Superuser not set - skipping"
    else
        echo "Will create superuser"
        python manage.py createsuperuser --noinput
    fi
    export DJANGO_SETTINGS_MODULE=machineteaching.settings
    echo "will start"
    opentelemetry-bootstrap --action=install
    gunicorn machineteaching.wsgi --bind 0.0.0.0:$PORT --workers 3
fi

