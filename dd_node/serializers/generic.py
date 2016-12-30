# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.

from __future__ import unicode_literals

import logging

from rest_framework import serializers
from rest_framework.fields import UUIDField

from dd_node.models import Node

logger = logging.getLogger(__name__)


class NodeSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='node-detail',
        lookup_field='uuid')
    uuid = UUIDField(read_only=True)

    class Meta:
        model = Node
        fields = (
            'url',
            'uuid',
            'name',
            'description',
            'base_url',
            'master',
        )
