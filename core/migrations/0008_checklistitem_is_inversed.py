# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-28 08:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20161224_1633'),
    ]

    operations = [
        migrations.AddField(
            model_name='checklistitem',
            name='is_inversed',
            field=models.BooleanField(default=False),
        ),
    ]
