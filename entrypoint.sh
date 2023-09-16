#!/bin/sh
#!/bin/bash

#ls -la
#whoami
#sudo ls -la /var/lib/docker/volumes/ip-finder_result/_data
#sudo ls -la /var/lib/docker/volumes/ip-finder_static/_data

# apply database migrations
#python manage.py migrate --no-input

# collect static files
#python manage.py collectstatic --no-input

#DJANGO_SUPERUSER_PASSWORD=$SUPER_USER_PASSWORD python manage.py createsuperuser --username $SUPER_USER_NAME --email $SUPER_USER_EMAIL --noinput

gunicorn config.wsgi:application --bind 0.0.0.0:8247 \
#    --name app \
#    --bind 0.0.0.0:8000 \
    --workers 5 \
    --timeout 300 \
    --max-requests 3
#    --log-level=info \
#    --log-file=/logs/gunicorn.log \
#    --access-logfile=/logs/access.log \
#    "$@"

 #uwsgi --socket :9000 --workers 4 --master --enable-threads --module config.wsgi