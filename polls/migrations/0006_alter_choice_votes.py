# Generated by Django 4.2.4 on 2023-09-17 07:43

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('polls', '0005_remove_choice_votes_choice_votes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='choice',
            name='votes',
            field=models.ManyToManyField(blank=True, related_name='voted_choices', to=settings.AUTH_USER_MODEL),
        ),
    ]