#!/bin/bash
# Railway build script

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running database migrations..."
alembic upgrade head

echo "Build complete!"
