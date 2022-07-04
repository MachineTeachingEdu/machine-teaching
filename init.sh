#!/bin/sh

echo $ENVIRONMENT
if [ "$ENVIRONMENT" = "PROD" ]; then
    echo "Preparing image for production"
    # cd /app/machineteaching
    python manage.py collectstatic --noinput
    python manage.py createsuperuser --noinput
    export DJANGO_SETTINGS_MODULE=machineteaching.settings
    opentelemetry-bootstrap --action=install
    OTEL_RESOURCE_ATTRIBUTES=service.name=machine_teaching OTEL_EXPORTER_OTLP_ENDPOINT="http://35.226.60.104:4318" opentelemetry-instrument --traces_exporter otlp_proto_http gunicorn machineteaching.wsgi --bind 0.0.0.0:$PORT --workers 3

else
    echo "Preparing image for development"
    /wait 
    cd /app/machineteaching
    # python manage.py makemigrations --noinput
    echo "Running migrations"
    python manage.py migrate -v 3 --noinput
    export DJANGO_SETTINGS_MODULE=machineteaching.settings
    opentelemetry-bootstrap --action=install
    echo "Starting server on port $PORT"
    OTEL_RESOURCE_ATTRIBUTES=service.name=machine_teaching OTEL_EXPORTER_OTLP_ENDPOINT="http://35.226.60.104:4318" opentelemetry-instrument --traces_exporter otlp_proto_http python manage.py runserver 0.0.0.0:$PORT
fi

