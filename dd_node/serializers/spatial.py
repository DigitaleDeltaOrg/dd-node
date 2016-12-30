# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import logging

from rest_framework import serializers
from rest_framework_gis.fields import GeometryField


from dd_node import fields
from dd_node.models import Location
from dd_node.serializers.generic import NodeSerializer

logger = logging.getLogger(__name__)


class GenericObjectSerializer(serializers.Serializer):
    type = serializers.SerializerMethodField()
    id = serializers.ReadOnlyField()
    geometry = GeometryField(read_only=True)
    created = fields.TimestampField()

    def get_type(self, obj):
        return obj.__class__.__name__.lower()


class GenericObjectRelSerializer(serializers.Serializer):
    def get_attribute(self, obj):
        # Pass the entire object through to `to_representation()`,
        # instead of the standard attribute lookup.
        return obj

    def to_representation(self, value):
        # The value is passed down from the `get_attribute` method
        # and therefore contains the entire object.
        if value.object:
            try:
                s = GenericObjectSerializer(instance=value.object)
                return s.data
            except Exception as ex:
                return "(internal error: %s)" % ex.__class__.__name__


class LocationSerializerBase(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        lookup_field='uuid',
        view_name='locations-detail')
    node = NodeSerializer()
    uuid = serializers.UUIDField(read_only=True)
    geometry = GeometryField(allow_null=True)
    extra_metadata = fields.JSONSerializerField(
        allow_null=True, required=False)
    object = GenericObjectRelSerializer(read_only=True)
    created = fields.TimestampField(read_only=True)
    last_modified = serializers.DateTimeField(
        read_only=True,
        default=datetime.datetime.now)
    last_modified_by = serializers.CharField(
        read_only=True)

    class Meta:
        model = Location

    def save(self):
        self.validated_data['last_modified_by'] = \
            self.context['request'].user.username
        return super(LocationSerializerBase, self).save()


class LocationSerializerRelated(LocationSerializerBase):
    class Meta:
        model = Location
        fields = (
            'url',
            'uuid',
            'name',
            'code',
            'geometry',
        )


class LocationSerializerList(LocationSerializerBase):
    class Meta:
        model = Location
        fields = (
            'url',
            'id',
            'node',
            'uuid',
            'name',
            'code',
            'geometry',
            'extra_metadata',
        )


class LocationSerializerDetail(LocationSerializerBase):
    class Meta:
        model = Location
        fields = (
            'url',
            'node',
            'uuid',
            'name',
            'code',
            'geometry',
            'extra_metadata',
            'created',
            'last_modified',
            'last_modified_by',
        )


class LocationSerializerDetailWrite(LocationSerializerBase):
    class Meta:
        model = Location
        fields = (
            'url',
            'uuid',
            'name',
            'code',
            'geometry',
            'extra_metadata',
            'last_modified',
            'last_modified_by',
        )


class LocationPropertiesSerializer(LocationSerializerDetail):
    class Meta:
        model = Location
        fields = (
            'name',
            'timeseries',
        )
