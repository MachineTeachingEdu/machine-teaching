FROM python:3.9.0-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    apt-utils \
    apt-transport-https \
    build-essential \
    unixodbc-dev \
    gcc \
    nginx \
    vim \
    gnupg && \
    echo 'deb http://apt.postgresql.org/pub/repos/apt/ stretch-pgdg main' >> /etc/apt/sources.list.d/pgdg.list && \
    curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y --no-install-recommends \
    libpq-dev \
    postgresql-client-10 

RUN pip3 install Cython

ADD requirements.txt .

RUN pip install -r requirements.txt

COPY machineteaching .

RUN python manage.py collectstatic --noinput

CMD gunicorn machineteaching.wsgi --bind 0.0.0.0:$PORT --workers 3
