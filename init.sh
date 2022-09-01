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
    # cd /app/machineteaching
    echo "Will collect static"
    python manage.py collectstatic --noinput
    python manage.py createsuperuser --noinput
    export DJANGO_SETTINGS_MODULE=machineteaching.settings
    echo "will start"
    opentelemetry-bootstrap --action=install
    gunicorn machineteaching.wsgi --bind 0.0.0.0:$PORT --workers 3
fi

