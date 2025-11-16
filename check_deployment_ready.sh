#!/bin/bash
echo "=================================================="
echo "VERCEL DEPLOYMENT READINESS CHECK"
echo "=================================================="
echo ""

# Check required files
echo "[1/5] Required Files"
echo "--------------------------------------------------"
files=(
    "vercel.json:Vercel config"
    ".vercelignore:Vercel ignore"
    "web/index.html:Main HTML"
    "web/config-loader.js:Config loader"
    "package.json:Package config"
)

for item in "${files[@]}"; do
    IFS=':' read -r file desc <<< "$item"
    if [ -f "$file" ]; then
        echo "✓ $desc"
    else
        echo "✗ $desc MISSING"
    fi
done

echo ""
echo "[2/5] Web Assets"
echo "--------------------------------------------------"
if [ -d "web" ]; then
    html_count=$(find web -name "*.html" | wc -l)
    js_count=$(find web -name "*.js" | wc -l)
    echo "✓ Web directory exists"
    echo "  - $html_count HTML file(s)"
    echo "  - $js_count JavaScript file(s)"
else
    echo "✗ Web directory missing"
fi

echo ""
echo "[3/5] Configuration Examples"
echo "--------------------------------------------------"
if [ -f "config.example.json" ]; then
    echo "✓ config.example.json exists"
fi
if [ -f "web/config.example.js" ]; then
    echo "✓ web/config.example.js exists"
fi

echo ""
echo "[4/5] Documentation"
echo "--------------------------------------------------"
docs=(
    "README.md"
    "VERCEL_DEPLOYMENT.md"
    "API_ACCESS_EXPLAINED.md"
    "TROUBLESHOOTING.md"
)

for doc in "${docs[@]}"; do
    if [ -f "$doc" ]; then
        echo "✓ $doc"
    else
        echo "✗ $doc"
    fi
done

echo ""
echo "[5/5] Git Status"
echo "--------------------------------------------------"
if [ -d ".git" ]; then
    echo "✓ Git repository initialized"
    branch=$(git branch --show-current)
    echo "  Current branch: $branch"
    
    # Check if there are uncommitted changes
    if git diff-index --quiet HEAD --; then
        echo "✓ No uncommitted changes"
    else
        echo "⚠ Uncommitted changes present"
    fi
else
    echo "✗ Not a git repository"
fi

echo ""
echo "=================================================="
echo "DEPLOYMENT CHECKLIST"
echo "=================================================="
echo ""
echo "Before deploying to Vercel, ensure you have:"
echo ""
echo "□ Mapbox account created"
echo "□ Mapbox public token (pk.*)"
echo "□ Mapbox username"
echo "□ Crown Land data uploaded to Mapbox as tileset(s)"
echo "□ Vercel account created"
echo "□ Repository pushed to GitHub"
echo ""
echo "Then:"
echo "1. Go to https://vercel.com/dashboard"
echo "2. Click 'Add New Project'"
echo "3. Import your GitHub repository"
echo "4. Add environment variables:"
echo "   - MAPBOX_PUBLIC_TOKEN"
echo "   - MAPBOX_USERNAME"
echo "5. Deploy!"
echo ""
echo "Or use CLI: vercel --prod"
echo ""
