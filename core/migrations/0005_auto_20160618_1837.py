# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-06-18 16:37
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20160618_1638'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='matchday',
            options={'ordering': ['season', '-number']},
        ),
        migrations.AlterModelOptions(
            name='season',
            options={'ordering': ['-number']},
        ),
    ]
