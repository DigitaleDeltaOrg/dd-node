# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import rest_framework_filters as filters

from dd_node.models import Timeseries

from dd_node.filters import LocationFilter
from dd_node.filters import UUIDFilterMixin


class TimeseriesFilter(UUIDFilterMixin, filters.FilterSet):
    """Timeseries filter.
    """
    # TODO: we can't use 'start' and 'end' as filterable fields, since they
    # are already being filtered using another way.
    last_value_decimal = filters.AllLookupsFilter()
    last_value_text = filters.AllLookupsFilter()
    location = filters.RelatedFilter(LocationFilter)
    name = filters.AllLookupsFilter()
    code = filters.AllLookupsFilter()
    uuid = filters.MethodFilter()
    uuid__icontains = filters.CharFilter(name='uuid', lookup_expr='icontains')
    value_type = filters.AllLookupsFilter()

    class Meta:
        model = Timeseries
        fields = []
