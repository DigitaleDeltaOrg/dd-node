# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-12-30 13:44
from __future__ import unicode_literals

import dd_node.modeldir.base
import dd_node.modeldir.generic
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import json_field.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DataSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, help_text='Universally unique identifier', unique=True)),
                ('name', models.CharField(help_text='Data source name', max_length=128)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, unique=True, verbose_name='Domain')),
                ('description', models.CharField(help_text='Domain description', max_length=1024)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Domain',
                'verbose_name_plural': 'Domains',
            },
        ),
        migrations.CreateModel(
            name='DomainTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Domain table name', max_length=256)),
                ('rest_sync_url', models.URLField(blank=True, default='', help_text='URL to REST API for synching domain', max_length=2048, null=True)),
                ('last_synced', models.DateTimeField(blank=True, help_text='Timestamp of latest sync', null=True)),
                ('domain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='domain_tables', to='dd_node.Domain')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Domain table',
                'verbose_name_plural': 'Domain tables',
            },
        ),
        migrations.CreateModel(
            name='DomainValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(help_text='Value code within domain', max_length=12, unique=True)),
                ('description', models.CharField(max_length=60, unique=True, verbose_name='Description')),
                ('begin_date', models.DateTimeField(blank=True, null=True, verbose_name='Begin timestamp')),
                ('end_date', models.DateTimeField(blank=True, null=True, verbose_name='End timestamp')),
                ('value_category', models.CharField(blank=True, help_text='Optional category of value', max_length=256, null=True)),
                ('domain_table', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='domain_values', to='dd_node.DomainTable')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Domain value',
                'verbose_name_plural': 'Domain values',
            },
        ),
        migrations.CreateModel(
            name='FileSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fullpath', models.CharField(max_length=256, unique=True)),
                ('mtime', models.IntegerField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, help_text='Universally unique identifier', unique=True, verbose_name='UUID')),
                ('code', models.CharField(db_index=True, help_text='ID of the location assigned by the organisation.', max_length=80)),
                ('name', models.CharField(help_text='Name of location', max_length=80)),
                ('geometry', django.contrib.gis.db.models.fields.GeometryField(blank=True, dim=3, null=True, srid=4326)),
                ('last_modified', models.DateTimeField(blank=True, null=True, verbose_name='Date last modified via the API')),
                ('last_modified_by', models.CharField(blank=True, max_length=64, verbose_name='Last modified by user via the API')),
                ('extra_metadata', json_field.fields.JSONField(blank=True, default='null', help_text='Enter a valid JSON object', null=True, verbose_name='Extra metadata')),
            ],
            options={
                'abstract': False,
            },
            bases=(dd_node.modeldir.base.ForceGeometry3DMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, help_text='Universally unique identifier', unique=True)),
                ('name', models.CharField(help_text='Node name', max_length=128, null=True)),
                ('description', models.TextField(help_text='Node description', null=True)),
                ('base_url', models.URLField(help_text='Node base url')),
                ('master', models.BooleanField(default=False, help_text='Am I master?')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ParameterReferencedUnit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=128, unique=True, verbose_name='Code')),
                ('parameter', models.CharField(blank=True, help_text='Short name for parameter', max_length=64)),
                ('unit', models.CharField(blank=True, help_text='Short name for referenced unit', max_length=64)),
                ('reference_frame', models.CharField(blank=True, help_text='Short name for reference frame', max_length=64, null=True)),
                ('compartment', models.CharField(blank=True, help_text='Short name for compartment', max_length=64, null=True)),
                ('description', models.TextField(blank=True, help_text='Optional description for parameter referenced unit')),
                ('scale', models.SmallIntegerField(choices=[(0, 'nominal'), (1, 'ordinal'), (2, 'interval'), (3, 'ratio')], default=2, help_text='On what scale is the data in this observation type. See <a href=http://en.wikipedia.org/wiki/Level_of_measurement>Level of measurement.</a>')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Parameter-referenced-unit',
                'verbose_name_plural': 'Parameter-referenced-units',
            },
        ),
        migrations.CreateModel(
            name='Timeseries',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, help_text='Universally unique identifier', unique=True, verbose_name='UUID')),
                ('name', models.CharField(blank=True, db_index=True, help_text='Optional name for timeseries', max_length=64, null=True)),
                ('description', models.TextField(blank=True, default='', help_text='optional description for timeseries', null=True)),
                ('value_type', models.SmallIntegerField(choices=[(0, 'integer'), (1, 'float'), (4, 'text'), (5, 'image'), (8, 'movie'), (10, 'file'), (12, 'float array')], default=1)),
                ('code', models.CharField(help_text='ID of the timeseries assigned by the organisation.', max_length=128)),
                ('device', models.CharField(blank=True, max_length=128, verbose_name='Device')),
                ('interval', models.IntegerField(blank=True, help_text='interval at which data is collected in seconds', null=True)),
                ('start', models.DateTimeField(blank=True, help_text='Timestamp of first value', null=True)),
                ('last_value_decimal', models.FloatField(blank=True, null=True)),
                ('last_value_text', models.TextField(blank=True, null=True)),
                ('end', models.DateTimeField(blank=True, help_text='Timestamp of latest value', null=True)),
                ('last_modified', models.DateTimeField(blank=True, null=True, verbose_name='Date last modified via the API')),
                ('last_modified_by', models.CharField(blank=True, max_length=64, verbose_name='Last modified by user via the API')),
                ('extra_metadata', json_field.fields.JSONField(default='null', help_text='Enter a valid JSON object', null=True, verbose_name='Extra metadata')),
                ('datasource', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='dd_node.DataSource')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='timeseries', to='dd_node.Location')),
                ('node', models.ForeignKey(default=dd_node.modeldir.generic.get_default_node, on_delete=django.db.models.deletion.PROTECT, to='dd_node.Node')),
                ('observation_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dd_node.ParameterReferencedUnit', verbose_name='observation type')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Timeseries',
                'verbose_name_plural': 'Timeseries',
            },
        ),
        migrations.CreateModel(
            name='TimeseriesType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(help_text='ID of the timeseries type.', max_length=128)),
                ('name', models.CharField(help_text='Type of timeseries', max_length=128)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='timeseries',
            name='timeseries_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='dd_node.TimeseriesType'),
        ),
        migrations.AddField(
            model_name='location',
            name='node',
            field=models.ForeignKey(default=dd_node.modeldir.generic.get_default_node, on_delete=django.db.models.deletion.PROTECT, to='dd_node.Node'),
        ),
        migrations.AddField(
            model_name='domainvalue',
            name='parameter_referenced_unit',
            field=models.ManyToManyField(blank=True, related_name='domain_values', to='dd_node.ParameterReferencedUnit'),
        ),
        migrations.AlterUniqueTogether(
            name='timeseries',
            unique_together=set([('location', 'code')]),
        ),
        migrations.AlterUniqueTogether(
            name='domainvalue',
            unique_together=set([('domain_table', 'code')]),
        ),
        migrations.AlterUniqueTogether(
            name='domaintable',
            unique_together=set([('domain', 'name')]),
        ),
    ]
