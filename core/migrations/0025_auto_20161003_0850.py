# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-10-03 06:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_auto_20161003_0822'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='awpboundarieskeyval',
            name='awp_boundaries',
        ),
        migrations.AlterModelOptions(
            name='awpboundaries',
            options={'ordering': ['-matchday', '-name'], 'verbose_name_plural': 'AWP Boundaries'},
        ),
        migrations.RemoveField(
            model_name='awpboundaries',
            name='id',
        ),
        migrations.AddField(
            model_name='awpboundaries',
            name='dictionary_ptr',
            field=models.OneToOneField(auto_created=True, default=1, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.Dictionary'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='AwpBoundariesKeyVal',
        ),
    ]