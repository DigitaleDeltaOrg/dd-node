# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.

"""Filters for domain related endpoints.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import rest_framework_filters as filters

from dd_node.models import Domain
from dd_node.models import DomainTable
from dd_node.models import DomainValue
from dd_node.models import ParameterReferencedUnit


class ParameterReferencedUnitFilter(filters.FilterSet):
    code = filters.AllLookupsFilter()
    parameter_short_display_name = filters.AllLookupsFilter(
        name='parameter')
    referenced_unit_short_display_name = filters.AllLookupsFilter(
        name='unit')

    class Meta:
        model = ParameterReferencedUnit
        fields = [
            'parameter_short_display_name',
            'referenced_unit_short_display_name'
        ]


class ObservationTypeFilter(ParameterReferencedUnitFilter):
    parameter = filters.AllLookupsFilter(
        name='parameter')
    unit = filters.AllLookupsFilter(
        name='unit')

    class Meta:
        model = ParameterReferencedUnit
        fields = [
            'parameter',
            'unit'
        ]


class DomainValueFilter(filters.FilterSet):
    code = filters.AllLookupsFilter()
    observation_type = filters.RelatedFilter(
        ParameterReferencedUnitFilter)
    value_category = filters.AllLookupsFilter()

    class Meta:
        model = DomainValue
        fields = []


class DomainTableFilter(filters.FilterSet):
    domain_values = filters.RelatedFilter(DomainValueFilter)
    name = filters.AllLookupsFilter()

    class Meta:
        model = DomainTable
        fields = []


class DomainFilter(filters.FilterSet):
    domain_tables = filters.RelatedFilter(DomainTableFilter)
    name = filters.AllLookupsFilter()

    class Meta:
        model = Domain
        fields = []
