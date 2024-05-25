#!/bin/sh
export PATH="$HOME/.local/bin:$PATH"

PORT=8989

poetry install
# source .venv/bin/activate

if ! grep -q "$PATH" /home/user/.bashrc; then
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> /home/user/.bashrc
fi

poetry run python -m flask --app src/main run -p $PORT --debug