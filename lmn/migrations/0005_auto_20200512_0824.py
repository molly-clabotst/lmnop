# Generated by Django 2.1.11 on 2020-05-12 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lmn', '0004_show_rating'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='show',
            name='rating',
        ),
        migrations.AddField(
            model_name='note',
            name='rating',
            field=models.IntegerField(choices=[(1, 'Poor'), (2, 'Average'), (3, 'Good'), (4, 'Very Good'), (5, 'Excellent')], default=3),
        ),
    ]
