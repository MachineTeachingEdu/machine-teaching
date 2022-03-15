FROM python:3.9.0-slim


# install PostgreSQL drivers
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

COPY nginx.default /etc/nginx/sites-available/default

# install nginx
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

ADD . .


RUN mkdir -p /opt/app
RUN mkdir -p /opt/app/machineteaching
COPY requirements.txt init.sh opt/app/
COPY machineteaching opt/app/machineteaching/
RUN chmod  u+x  opt/app/init.sh
RUN chown  -R www-data:www-data  opt/app

RUN touch /opt/app/machineteaching/machineteaching/mt_dev.log

# start server
EXPOSE 8020
ENTRYPOINT [ "opt/app/init.sh" ]


