# syntax=docker/dockerfile:1
FROM python:3.7-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# bpy bmesh
# sys os
# csv math
# from mathutils import Vector
# Install server dependencies.
RUN pip install Flask gunicorn google-cloud-storage

ENV PORT 8080

# Run the web server on container startup. Here we use the gunicorn webserver
# For environments with multiple CPU cores, increase the number of workers to be equal to the cores available.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app