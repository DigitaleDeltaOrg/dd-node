# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import rest_framework_filters as filters
import rest_framework_gis.filters as geofilters

from dd_node.models import Location
from dd_node.filters import UUIDFilterMixin


class LocationFilter(UUIDFilterMixin, filters.FilterSet):
    created = filters.AllLookupsFilter()
    geom_equals = geofilters.GeometryFilter(
        name='geometry', lookup_type='equals')
    geom_isnull = filters.MethodFilter()
    geom_within = geofilters.GeometryFilter(
        name='geometry', lookup_type='within')
    name = filters.AllLookupsFilter()
    code = filters.AllLookupsFilter()
    uuid = filters.MethodFilter()
    uuid__icontains = filters.CharFilter(name='uuid', lookup_expr='icontains')

    # V2 specific:
    organisation_code = filters.AllLookupsFilter(name='code')

    class Meta:
        model = Location
        fields = [
            'extra_metadata',
            'last_modified',
            'last_modified_by',
            'timeseries__uuid',
        ]

    def filter_geom_isnull(self, name, queryset, value):
        if value in ['True', 'true']:
            return queryset.filter(geometry__isnull=True)
        elif value in ['False', 'false']:
            return queryset.filter(geometry__isnull=False)
        else:
            return Location.objects.none()
