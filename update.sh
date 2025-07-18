#!/bin/bash
# Script: update.sh
# Description: Safely downloads and extracts configuration templates from GitHub repository
# Author: Thomas Schmelzer
# Usage: ./update.sh

set -euo pipefail  # Fail on errors, undefined variables, and pipeline failures

# ---- Configuration ----
REPO_URL="https://github.com/tschm/.config-templates"
TEMP_DIR=".temp_templates"  # Avoid naming conflicts with possible existing dirs
BRANCH_NAME="config-sync"

# ---- Helper Functions ----
die() {
  echo "❌ Error: $*" >&2
  exit 1
}

# ---- Cleanup Function ----
cleanup() {
  # This runs on script exit (normal or error)
  echo "🧹 Cleaning up temporary files..."
  rm -rf "${TEMP_DIR}" templates.zip
}

# ---- Register cleanup trap ----
# trap cleanup EXIT

# ---- Check Dependencies ----
command -v curl >/dev/null || die "curl is not installed."
command -v unzip >/dev/null || die "unzip is not installed."
command -v git >/dev/null || die "git is not installed."

# ---- Download Templates ----
echo "⬇️ Downloading templates from ${REPO_URL}..."
if ! curl -sSL -o templates.zip "${REPO_URL}/archive/refs/heads/main.zip"; then
  die "Failed to download templates."
fi

# ---- Extract Templates ----
echo "📦 Extracting templates..."
if ! unzip -q templates.zip -d "${TEMP_DIR}"; then
  die "Failed to extract templates."
fi

ls ${TEMP_DIR}

# ---- Verify Extraction ----
if [[ ! -d "${TEMP_DIR}/.config-templates-main" ]]; then
  die "Extracted directory structure doesn't match expectations."
fi

# ---- Git Operations ----
echo "🔄 Updating git repository..."

# Stash any existing changes to avoid conflicts
git stash push --quiet --include-untracked --message "update.sh auto-stash"

# Checkout/Create branch
if git show-ref --verify --quiet "refs/heads/${BRANCH_NAME}"; then
  git checkout --quiet "${BRANCH_NAME}"
else
  git checkout --quiet -b "${BRANCH_NAME}"
fi

# Copy new files (preserving existing files with --ignore-existing)
cp -nR "${TEMP_DIR}/.config-templates-main/." . || {
  die "Failed to copy templates. Some files may already exist."
}

# Commit changes if there are any
#if git diff-index --quiet HEAD --; then
#  echo "✅ No changes to commit."
#else
#  git add .
#  if git commit -m "Update configuration templates from ${REPO_URL}"; then
#    echo "✅ Changes committed."
#    # Only push if commit succeeded
#    if git push --quiet origin "${BRANCH_NAME}"; then
#      echo "📤 Pushed changes to ${BRANCH_NAME}."
#    else
#      echo "⚠️ Could not push changes (remote not configured?)."
#    fi
#  else
#    echo "⚠️ Could not commit changes."
#  fi
#fi
#
## Return to original branch
#if git rev-parse --quiet --verify main >/dev/null; then
#  git checkout --quiet main
#else
#  echo "ℹ️ main branch does not exist, staying on ${BRANCH_NAME}"
#fi
#
#echo "✨ Done!"