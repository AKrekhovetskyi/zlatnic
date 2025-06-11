#!/usr/bin/env bash
# exit on error
set -o errexit

git submodule update --init

# Install uv with our official standalone installer.
curl -LsSf https://astral.sh/uv/install.sh | sh

# Export environment variables only if the ".env" file exists.
[ -f .env ] && export $(grep -v '^#' .env | xargs)
export DEBUG=False
export PATH="$HOME/.local/bin:$PATH"

uv run manage.py collectstatic --no-input
uv run manage.py migrate
uv run manage.py loaddata zlatnic_db_data.json
