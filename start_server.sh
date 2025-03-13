#!/bin/bash

# Decode Firebase credentials from environment variable and save to file
echo "$FIREBASE_CREDENTIALS" | base64 --decode > ./firebase_credentials.json

# Start Gunicorn server
exec gunicorn neplink.wsgi:application --bind 0.0.0.0:8080 