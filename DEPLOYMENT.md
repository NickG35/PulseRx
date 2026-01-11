# PulseRx Deployment Guide

## Production Data Loading

This application includes a custom Django management command for loading production data without the typical Django fixture limitations.

### Why Use the Management Command?

The standard `loaddata` command has limitations:
- Field length mismatches can cause errors
- Large JSON files can be problematic
- Less control over error handling
- Cannot handle data transformations

### Loading Production Data

#### Automatic Loading (First Deploy)

The `build.sh` script automatically loads `production_data.json` if:
1. The file exists in the project root
2. The database is empty (no existing users)

This happens during the first deployment to Render.

#### Manual Loading

You can manually load data using the management command:

```bash
# Basic usage
python manage.py load_production_data

# Specify a custom file
python manage.py load_production_data --file path/to/data.json

# Clear existing data and reload
python manage.py load_production_data --clear --file production_data.json
```

### Command Features

- **Smart Loading**: Uses `update_or_create` to avoid duplicates
- **Error Handling**: Detailed error messages with model and PK information
- **Transaction Safety**: All-or-nothing loading with database transactions
- **Field Truncation**: Automatically truncates fields to prevent overflow
- **Statistics**: Reports count of loaded objects by type

### Data File Format

The command expects a Django fixture format (JSON array):

```json
[
  {
    "model": "accounts.customaccount",
    "pk": 1,
    "fields": {
      "username": "user1",
      "email": "user@example.com",
      ...
    }
  },
  ...
]
```

### Deployment Process

1. **Push your code** including `production_data.json`
2. **Render deploys** and runs `build.sh`
3. **Migrations run** including the dosage/route field increases
4. **Data loads** automatically via the management command

### Database Schema Notes

The `Drug` model has been updated to support longer field values:
- `dosage`: 2000 characters (was 100) - to accommodate full dosage instructions
- `route`: 255 characters (was 100)

Migration `0016_alter_drug_dosage_alter_drug_route` handles this schema change.

### Troubleshooting

**Data already exists error:**
- The command skips loading if users already exist
- Use `--clear` flag to remove existing data first

**Field too long errors:**
- Check the model field lengths in `pharmacy/models.py`
- Update the migration if needed
- Current limits: dosage=2000, route=255

**File not found:**
- Ensure `production_data.json` is in the project root
- Verify it's committed to git
- Check Render deployment logs

### Running on Render

To run the command on a deployed Render instance:

1. Go to your Render dashboard
2. Select your web service
3. Click "Shell" tab
4. Run: `python manage.py load_production_data --file production_data.json`

Or use Render CLI:
```bash
render shell -s pulserx
python manage.py load_production_data
```
