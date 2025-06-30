#!/bin/sh

echo "Waiting for Redis..."

while ! nc -z redis 6379; do
  sleep 1
done

echo "Redis started"

python manage.py migrate

python create_superuser.py

echo "Starting Django development server..."
python manage.py runserver 0.0.0.0:8000
