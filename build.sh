#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies and build TailwindCSS
npm install
npm run build

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Create superuser if it doesn't exist (optional - for demo)
# python manage.py shell -c "from accounts.models import CustomAccount; CustomAccount.objects.create_superuser('admin@pulserx.com', 'admin', 'password123') if not CustomAccount.objects.filter(username='admin').exists() else None"
