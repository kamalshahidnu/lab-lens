#!/bin/bash
# Setup script to configure your fork

echo "=" | head -c 70; echo ""
echo "Setting Up Your Fork"
echo "=" | head -c 70; echo ""
echo ""

# Get GitHub username
read -p "Enter your GitHub username: " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    echo "❌ GitHub username is required!"
    exit 1
fi

echo ""
echo "Setting up remotes..."
echo ""

# Check if upstream exists
if git remote | grep -q upstream; then
    echo "✓ Upstream remote already exists"
else
    # Rename origin to upstream if it points to main repo
    CURRENT_ORIGIN=$(git remote get-url origin 2>/dev/null || echo "")
    if [[ "$CURRENT_ORIGIN" == *"asad-waraich/lab-lens"* ]]; then
        echo "Renaming origin to upstream..."
        git remote rename origin upstream
        echo "✓ Renamed origin to upstream"
    else
        echo "Adding upstream remote..."
        git remote add upstream https://github.com/asad-waraich/lab-lens.git
        echo "✓ Added upstream remote"
    fi
fi

# Set your fork as origin
echo "Setting your fork as origin..."
git remote set-url origin https://github.com/${GITHUB_USERNAME}/lab-lens.git 2>/dev/null || \
git remote add origin https://github.com/${GITHUB_USERNAME}/lab-lens.git

echo "✓ Set origin to your fork"
echo ""

# Verify
echo "Current remotes:"
git remote -v
echo ""

echo "=" | head -c 70; echo ""
echo "✓ Setup complete!"
echo "=" | head -c 70; echo ""
echo ""
echo "Next steps:"
echo "  1. Make sure you've forked the repo on GitHub:"
echo "     https://github.com/asad-waraich/lab-lens"
echo ""
echo "  2. Push your current branch:"
echo "     git push -u origin main"
echo ""
echo "  3. To sync with main repo later, run:"
echo "     ./scripts/sync_with_upstream.sh"
echo ""







