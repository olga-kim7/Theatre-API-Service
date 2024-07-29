# Generated by Django 5.0.7 on 2024-07-29 19:33

import theatre.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("theatre", "0003_alter_ticket_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="play",
            name="image",
            field=models.ImageField(
                null=True, upload_to=theatre.models.movie_image_path
            ),
        ),
    ]