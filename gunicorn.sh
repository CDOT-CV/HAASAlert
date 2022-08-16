#!/bin/sh
gunicorn haas_websocket.wsgi:app --threads 2 -b 0.0.0.0:8080