# Generated manually for field length increases
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0015_duplicate_drugs_for_pharmacies'),
    ]

    operations = [
        migrations.AlterField(
            model_name='drug',
            name='dosage',
            field=models.CharField(max_length=2000),
        ),
        migrations.AlterField(
            model_name='drug',
            name='route',
            field=models.CharField(max_length=255, blank=True),
        ),
    ]
