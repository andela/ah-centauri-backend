#!/usr/bin/env bash
echo "Running Release Tasks"

echo "Running Database migrations and migrating the new changes"
python manage.py makemigrations authentication profiles articles comments
python manage.py migrate

echo "Done.."