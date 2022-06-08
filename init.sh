#!/bin/sh

echo $ENVIRONMENT
if [ "$ENVIRONMENT" = "PROD" ]; then
    echo "Preparing image for production"
    # cd /app/machineteaching
    python manage.py collectstatic --noinput
    python manage.py createsuperuser --noinput
    sw-python run gunicorn machineteaching.wsgi --bind 0.0.0.0:$PORT --workers 3

else
    echo "Preparing image for development"
    /wait 
    cd /app/machineteaching
    # python manage.py makemigrations --noinput
    echo "Running migrations"
    python manage.py migrate -v 3 --noinput
    echo "Starting server on port $PORT"
    sw-python run python manage.py runserver 0.0.0.0:$PORT
fi