#!/bin/bash

echo "=========================================="
echo "PulseRx Demo Data Seeding Script"
echo "=========================================="
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
fi

# Run the demo scenarios seeding command
echo ""
echo "Seeding demo scenarios..."
python manage.py seed_demo_scenarios

echo ""
echo "=========================================="
echo "Demo data seeding complete!"
echo "=========================================="
