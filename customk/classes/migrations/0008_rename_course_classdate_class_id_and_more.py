# Generated by Django 5.1 on 2024-08-21 20:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('classes', '0007_alter_class_created_at'),
    ]

    operations = [
        migrations.RenameField(
            model_name='classdate',
            old_name='course',
            new_name='class_id',
        ),
        migrations.RenameField(
            model_name='classimages',
            old_name='course',
            new_name='class_id',
        ),
    ]
