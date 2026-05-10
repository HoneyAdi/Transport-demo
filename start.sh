#!/bin/bash
export PYTHONPATH=$PYTHONPATH:$PWD
cd /opt/render/project/src
gunicorn --workers 3 --bind 0.0.0.0:$PORT wsgi:application
