# Generated by Django 5.2 on 2025-06-16 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_customuser_profile_picture"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="profile_picture",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="profile_pics/",
                verbose_name="Profile Picture",
            ),
        ),
    ]
