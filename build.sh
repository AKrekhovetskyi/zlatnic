#!/usr/bin/env bash
# exit on error
set -o errexit

curl -LsSf https://astral.sh/uv/install.sh | sh

uv run manage.py collectstatic --no-input
uv run manage.py migrate
uv run manage.py loaddata zlatnic_db_data.json
