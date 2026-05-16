#!/usr/bin/env bash
set -euo pipefail

VENV_DIR=".venv"
REQUIREMENTS="requirements.txt"
SECRETS_DIR="secrets"
ENV_FILE="${SECRETS_DIR}/.env"

if command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON=python
else
  echo "Python не найден. Установите Python 3 (например, brew install python) и убедитесь, что он в PATH."
  exit 1
fi

if [[ ! -d "$SECRETS_DIR" ]]; then
  echo "Создание папки ${SECRETS_DIR}..."
  mkdir "$SECRETS_DIR"
fi

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Создание файла ${ENV_FILE} с настройками по умолчанию..."
  cat >"$ENV_FILE" <<'EOF'
LOGIN=your_login
PASSWORD=your_password
CITY=your_city
GAME_ID=your_game_id
DOCUMENT_ID=your_document_id
FOLDER_ID=your_folder_id
EOF
  echo "Файл ${ENV_FILE} создан. Отредактируйте его перед запуском скрипта."
else
  echo "Файл ${ENV_FILE} уже существует. Пропускаем создание."
fi

if [[ ! -d "$VENV_DIR" ]]; then
  echo "Создание виртуального окружения в папке ${VENV_DIR}..."
  "$PYTHON" -m venv "$VENV_DIR"
else
  echo "Виртуальное окружение уже существует."
fi

echo "Активация виртуального окружения и установка зависимостей..."
# shellcheck source=/dev/null
source "${VENV_DIR}/bin/activate"

if [[ -f "$REQUIREMENTS" ]]; then
  echo "Установка зависимостей из ${REQUIREMENTS}..."
  pip install -r "$REQUIREMENTS"
else
  echo "Файл ${REQUIREMENTS} не найден. Установка зависимостей пропущена."
fi

deactivate || true

echo "Готово."
