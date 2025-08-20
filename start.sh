#!/usr/bin/env bash
source .env
exec gunicorn app:app --timeout 120 --workers 1 --threads 1 --bind 0.0.0.0:$PORT