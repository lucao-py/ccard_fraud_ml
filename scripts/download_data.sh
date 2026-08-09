#!/usr/bin/env bash

set -euo pipefail

# Este script deve ficar em:
# <raiz_do_projeto>/scripts/download_data.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

RAW_DIR="${PROJECT_ROOT}/raw"
ZIP_PATH="${RAW_DIR}/fraud-detection.zip"

DATASET_URL="https://www.kaggle.com/api/v1/datasets/download/kartik2112/fraud-detection"

echo "Raiz do projeto: ${PROJECT_ROOT}"
echo "Pasta de destino: ${RAW_DIR}"

command -v curl >/dev/null 2>&1 || {
    echo "Erro: o comando 'curl' não está instalado."
    exit 1
}

command -v unzip >/dev/null 2>&1 || {
    echo "Erro: o comando 'unzip' não está instalado."
    exit 1
}

mkdir -p "${RAW_DIR}"

echo "Baixando o dataset Sparkov..."

curl \
    --location \
    --fail \
    --show-error \
    --retry 3 \
    --output "${ZIP_PATH}" \
    "${DATASET_URL}"

echo "Extraindo os arquivos em ${RAW_DIR}..."

unzip -o "${ZIP_PATH}" -d "${RAW_DIR}"

echo "Removendo o arquivo ZIP..."

rm -f "${ZIP_PATH}"

echo
echo "Download concluído."
echo "Arquivos disponíveis em: ${RAW_DIR}"

find "${RAW_DIR}" -maxdepth 1 -type f -printf " - %f\n" 2>/dev/null \
    || ls -1 "${RAW_DIR}"