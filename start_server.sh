#!/bin/sh

# Decode Firebase credentials from environment variable and save to file
echo "$FIREBASE_CREDENTIALS" | base64 -d > ./firebase_credentials.json

# Start Gunicorn server
gunicorn neplink.wsgi:application --bind 0.0.0.0:8080 