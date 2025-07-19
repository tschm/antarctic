#!/bin/bash
# Script: up.sh
# Description: Safely updates config files from GitHub without branch switching
# Author: Thomas Schmelzer

set -euo pipefail

REPO_URL="https://github.com/tschm/.config-templates"
TEMP_DIR="$(mktemp -d)"

main() {
  echo "📥 Downloading template archive..."
  curl -sSL -o templates.zip "$REPO_URL/archive/refs/heads/main.zip"

  echo "📦 Extracting..."
  unzip -q templates.zip -d "$TEMP_DIR"
  rm -f templates.zip

  EXTRACTED_DIR="${TEMP_DIR}/.config-templates-main"

  echo "🧹 Removing update script from extracted files..."
  rm -f "${EXTRACTED_DIR}/scripts/up.sh"
  rm -f "${EXTRACTED_DIR}/action.yml"

  echo "📂 Copying files to working directory..."
  cp -Rf "${EXTRACTED_DIR}/." .

  echo "✅ Sync complete. Changed files:"
  git status --short
}

trap 'rm -rf "$TEMP_DIR"' EXIT
main "$@"