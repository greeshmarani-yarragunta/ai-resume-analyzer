#!/bin/bash
# start server with gunicorn; Render provides $PORT automatically
gunicorn app:app --bind 0.0.0.0:$PORT
