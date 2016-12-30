# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from rest_framework.viewsets import ReadOnlyModelViewSet


from dd_node.filters import domain as filters
from dd_node.mixins import ExceptionMixin
from dd_node.models import ParameterReferencedUnit
from dd_node.models import DataSource
from dd_node.models import Domain
from dd_node.models import DomainTable
from dd_node.models import DomainValue
from dd_node.serializers import domain as serializers
from dd_node.serializers import domain_v2 as serializers_v2

logger = logging.getLogger(__name__)


class ParameterReferencedUnitViewSet(ExceptionMixin, ReadOnlyModelViewSet):
    """List of parameter referenced units.

    **Parameters:**

    code
        *Optional* text filter on ``code``

    parameter
        *Optional* text filter on ``parameter``

    unit
        *Optional* text filter on ``unit``

    """
    model = ParameterReferencedUnit
    serializer_class = serializers_v2.ParameterReferencedUnitSerializer
    lookup_field = 'pk'
    filter_class = filters.ParameterReferencedUnitFilter

    def get_queryset(self):
        return ParameterReferencedUnit.objects.all()


class ObservationTypeViewSet(ParameterReferencedUnitViewSet):
    """For the V3 API ParameterReferencedUnit must be renamed to
    ObservationType, hence this viewset."""
    serializer_class = serializers.ObservationTypeSerializer
    filter_class = filters.ObservationTypeFilter


class DomainViewSet(ExceptionMixin, ReadOnlyModelViewSet):
    """List of domains.

    **Parameters:**

    name
        *Optional* text filter on ``name``

    domain_tables
        *Optional*`related filter`_ on `Domaintables`_.

    """
    model = Domain
    serializer_class = serializers.DomainSerializer
    lookup_field = 'name'
    filter_class = filters.DomainFilter

    def get_queryset(self):
        return Domain.objects.all()


class DomainTableViewSet(ExceptionMixin, ReadOnlyModelViewSet):
    """List of domain tables.

    **Parameters:**

    name
        *Optional* filter on ``name``

    domain_values
        *Optional* `related filter`_ on `Domainvalues`_

    """
    model = DomainTable
    serializer_class = serializers.DomainTableSerializer
    lookup_field = 'name'
    filter_class = filters.DomainTableFilter

    def get_queryset(self):
        """Filtered queryset on case insensitive domain name.
        """
        return DomainTable.objects.filter(
            domain__name__iexact=self.kwargs.get('domain_name'))


class DomainValueViewSet(ExceptionMixin, ReadOnlyModelViewSet):
    """List of domain values.

    Available filters:

    * code:
    * value_category:
    * observation_type: `related filter`_ on
      `Parameter referenced units`_

    """
    model = DomainValue
    serializer_class = serializers.DomainValueSerializer
    lookup_field = 'code'
    filter_class = filters.DomainValueFilter

    def get_queryset(self):
        """Filtered queryset on case insensitive domain name and domain table
        code.
        """
        return DomainValue.objects.filter(
            domain_table__domain__name__iexact=self.kwargs.get('domain_name'),
            domain_table__name__iexact=self.kwargs.get('domaintable_name'))


class DataSourceViewSet(ExceptionMixin, ReadOnlyModelViewSet):
    model = DataSource
    serializer_class = serializers.DataSourceSerializer
    lookup_field = 'uuid'

    def get_queryset(self):
        return DataSource.objects.all()
