#!/bin/bash
set -e

# Activate Python virtual environment
. .venv/bin/activate

# Run the command passed by the user
exec "$@"
