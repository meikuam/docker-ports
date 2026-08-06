#!/bin/bash

# Switch to docker user
if [ -f "/.dockerenv" ] && ! id -u docker > /dev/null 2>&1; then
    useradd -m -u 1000 docker || true
    chown -R docker:docker /app
    exec sudo -u docker gunicorn main:app --workers 2 --bind 0.0.0.0:8000 --access-logfile -
else
    exec gunicorn main:app --workers 2 --bind 0.0.0.0:8000 --access-logfile -
fi