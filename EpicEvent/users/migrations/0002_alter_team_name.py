# Generated by Django 4.1.6 on 2023-02-09 23:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='name',
            field=models.CharField(choices=[('MANAGEMENT', 'Management'), ('SALES', 'Sales'), ('SUPPORT', 'Support')], max_length=10),
        ),
    ]
