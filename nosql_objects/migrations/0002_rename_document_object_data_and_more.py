# Generated by Django 4.1 on 2022-09-15 16:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("baas_objects", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="object",
            old_name="document",
            new_name="data",
        ),
        migrations.AlterField(
            model_name="object",
            name="object_class",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="objects_in_class",
                to="baas_objects.objectclass",
            ),
        ),
    ]