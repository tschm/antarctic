#!/bin/bash
# Script: up.sh
# Description: Safely updates config files from GitHub without branch switching
# Author: Thomas Schmelzer

set -euo pipefail

REPO_URL="https://github.com/tschm/.config-templates"
TEMP_DIR="$(mktemp -d)"

main() {
  curl -sSL -o templates.zip "$REPO_URL/archive/refs/heads/main.zip"
  unzip -q templates.zip -d "$TEMP_DIR"
  rm -f templates.zip

  EXTRACTED_DIR="${TEMP_DIR}/.config-templates-main"
  #[ -d "$EXTRACTED_DIR" ] || exit 1

  #updated=0
  cp -Rf $EXTRACTED_DIR/. .
  git status

  #while IFS= read -r -d '' file; do
  #  target_file="./${file#$EXTRACTED_DIR/}"
  #  mkdir -p "$(dirname "$target_file")"
  #  #if ! cmp -s "$file" "$target_file"; then
  #  cp -v "$file" "$target_file"
  #  #((updated++))
  #  #fi
  #done < <(find "$EXTRACTED_DIR" -type f -print0)

  #echo "$updated files updated."
}
trap 'rm -rf "$TEMP_DIR"' EXIT
main "$@"
