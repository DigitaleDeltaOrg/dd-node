# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.

from __future__ import unicode_literals

import json
import logging

from rest_framework import serializers
from watson.models import SearchEntry

logger = logging.getLogger(__name__)


class WatsonSearchSerializer(serializers.ModelSerializer):
    rank = serializers.FloatField(source='watson_rank')
    entity_name = serializers.SerializerMethodField()
    entity_id = serializers.IntegerField(source='object_id_int')
    entity_uuid = serializers.SerializerMethodField(source='uuid')
    entity_url = serializers.SerializerMethodField(source='url')
    view = serializers.SerializerMethodField()

    class Meta:
        model = SearchEntry
        fields = (
            'id',
            'title',
            'description',
            'rank',
            'entity_name',
            'entity_id',
            'entity_uuid',
            'entity_url',
            'view',
        )

    def get_entity_name(self, obj):
        """Return the name of the model the search entry corresponds to.

        """
        meta = json.loads(obj.meta_encoded)
        content_type_map = {
            'layer': 'wmslayer',
            'rasterstore': 'raster',
        }
        return content_type_map.get(meta.get('model'), meta.get('model'))

    def get_entity_url(self, obj):
        """Return the absolute URL to the endpoint of the model.

        The search index contains relative URLs. To produce a browsable API,
        Django REST framework needs fully-qualified URLs.

        """
        request = self.context.get('request')
        return request.build_absolute_uri(obj.url) if request else obj.request

    def get_entity_uuid(self, obj):
        """Return the UUID of the model.

        """
        meta = json.loads(obj.meta_encoded)
        return meta.get('uuid')

    def get_view(self, obj):
        """Return the [lat, lng, zoom] at which the result is best viewed.

        EPSG:4326 specifically states that the coordinate order should
        be latitude, longitude.

        """
        meta = json.loads(obj.meta_encoded)
        lng = meta.get('x')
        lat = meta.get('y')
        zoom = meta.get('z')
        return [lat, lng, zoom]
