# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from rest_framework.viewsets import ModelViewSet

from dd_node.filters import LocationFilter
from dd_node.mixins import ExceptionMixin
from dd_node.mixins import MultiSerializerViewSetMixin
from dd_node.models import Location
from dd_node.serializers import spatial as serializers

logger = logging.getLogger(__name__)


class LocationViewSet(ExceptionMixin,
                      MultiSerializerViewSetMixin,
                      ModelViewSet):
    """List of locations.

    Supports `spatial filter`_

    **Parameters:**

    name
        *Optional* text filter on ``name``

    created
        *Optional* temporal filter on ``created``

    geom_isnull
        *Optional* one of ``True`` or ``False`` to select or omit objects
        without geometry respectively.

    **Ordering:** field ``name`` can be used for ordering.

    """
    model = Location
    lookup_field = 'uuid'
    filter_class = LocationFilter
    bbox_filter_field = 'geometry'
    bbox_filter_include_overlapping = True
    distance_filter_field = bbox_filter_field
    distance_filter_convert_meters = True
    ordering_fields = ('name', )
    ordering = ('id', )
    serializer_class = serializers.LocationSerializerDetail
    serializer_action_classes = {
        'list': serializers.LocationSerializerList,
        'retrieve': serializers.LocationSerializerDetail,
    }

    def get_queryset(self):
        return Location.objects.all().select_related('organisation')
