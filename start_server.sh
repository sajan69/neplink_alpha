#!/bin/sh

# Start Gunicorn server
gunicorn neplink.wsgi:application --bind 0.0.0.0:8080 