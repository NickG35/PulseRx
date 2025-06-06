# Generated by Django 5.0.1 on 2025-06-04 11:36

import django.db.models.deletion
import pharmacy.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0002_drug_route'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='pharmacyprofile',
            name='join_code',
            field=models.CharField(default=pharmacy.models.generate_join_code, max_length=6, unique=True),
        ),
        migrations.CreateModel(
            name='PharmacistProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('pharmacy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pharmacists', to='pharmacy.pharmacyprofile')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
