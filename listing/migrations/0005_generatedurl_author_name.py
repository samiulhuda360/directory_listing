# Generated by Django 4.2.7 on 2024-02-08 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listing', '0004_postedwebsite'),
    ]

    operations = [
        migrations.AddField(
            model_name='generatedurl',
            name='author_name',
            field=models.TextField(blank=True, null=True),
        ),
    ]
