#!/usr/bin/env bash
set -euo pipefail

VENV_DIR=".venv"
SCRIPT="main.py"

if [[ ! -d "$VENV_DIR" ]]; then
  echo "Виртуальное окружение не найдено. Сначала выполните: ./setup.sh"
  exit 1
fi

if [[ ! -f "$SCRIPT" ]]; then
  echo "Файл ${SCRIPT} не найден."
  exit 1
fi

# shellcheck source=/dev/null
source "${VENV_DIR}/bin/activate"
python "$SCRIPT" "$@"
