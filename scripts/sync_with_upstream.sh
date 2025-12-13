#!/bin/bash
# Sync your fork with the main repository

set -e

echo "=" | head -c 70; echo ""
echo "Syncing with Main Repository (asad-waraich/lab-lens)"
echo "=" | head -c 70; echo ""
echo ""

# Check if upstream remote exists
if ! git remote | grep -q upstream; then
  echo "⚠️ Upstream remote not found!"
  echo ""
  echo "Setting up upstream remote..."
  git remote add upstream https://github.com/asad-waraich/lab-lens.git
  echo " Added upstream remote"
  echo ""
fi

# Fetch latest changes
echo "📥 Fetching latest changes from upstream..."
git fetch upstream

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"
echo ""

# Check if there are uncommitted changes
if ! git diff-index --quiet HEAD --; then
  echo "⚠️ You have uncommitted changes!"
  echo "Please commit or stash them before syncing."
  echo ""
  read -p "Stash changes and continue? (y/n): " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    git stash
    STASHED=true
  else
    echo "Aborted."
    exit 1
  fi
fi

# Switch to main branch
if [ "$CURRENT_BRANCH" != "main" ]; then
  echo "Switching to main branch..."
  git checkout main
fi

# Merge upstream changes
echo ""
echo "🔄 Merging upstream/main into local main..."
git merge upstream/main --no-edit

# Push to your fork
echo ""
echo "📤 Pushing to your fork (origin)..."
git push origin main

# Restore stashed changes if any
if [ "$STASHED" = true ]; then
  echo ""
  echo "📦 Restoring stashed changes..."
  git stash pop
fi

echo ""
echo "=" | head -c 70; echo ""
echo " Successfully synced with main repository!"
echo "=" | head -c 70; echo ""
echo ""
echo "Your fork is now up to date with asad-waraich/lab-lens"







