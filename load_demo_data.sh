#!/usr/bin/env bash
# Script to load demo data into production database
# Run this in Render Shell

echo "Loading demo data into production database..."
echo "This will add:"
echo "  - 136 user accounts"
echo "  - 106 patient profiles"
echo "  - 726 medications"
echo "  - 61 prescriptions"
echo "  - And more..."
echo ""

python manage.py loaddata production_data.json

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Demo data loaded successfully!"
    echo ""
    echo "You can now log in with your existing credentials"
else
    echo ""
    echo "❌ Failed to load demo data"
    echo "Check the error messages above"
fi
