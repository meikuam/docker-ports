#!/bin/bash

# Switch to docker user
if [ -f "/.dockerenv" ] && ! id -u docker > /dev/null 2>&1; then
    useradd -m -u 1000 docker || true
    chown -R docker:docker /app
    exec sudo -u docker uvicorn main:app --host 0.0.0.0 --port 8000
else
    exec uvicorn main:app --host 0.0.0.0 --port 8000
fi