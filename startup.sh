#!/bin/bash
# startup.sh

echo "Starting application..."

# Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Start the application with Gunicorn
gunicorn --bind=0.0.0.0:8000 \
         --workers=2 \
         --timeout=300 \
         --access-logfile - \
         --error-logfile - \
         --log-level info \
         app:app