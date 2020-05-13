# Generated by Django 2.1.11 on 2020-05-12 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lmn', '0003_merge_20200508_0343'),
    ]

    operations = [
        migrations.AddField(
            model_name='show',
            name='rating',
            field=models.IntegerField(choices=[(1, 'Poor'), (2, 'Average'), (3, 'Good'), (4, 'Very Good'), (5, 'Excellent')], default=1),
        ),
    ]