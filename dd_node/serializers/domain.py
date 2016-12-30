# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from urllib import quote
from urlparse import urlparse

from django.core.urlresolvers import resolve
from rest_framework import serializers

from dd_node import fields
from dd_node.models import ParameterReferencedUnit
from dd_node.models import DataSource
from dd_node.models import Domain
from dd_node.models import DomainTable
from dd_node.models import DomainValue
from dd_node.models import VALUE_SCALE
from dd_node.serializers.generic import NodeSerializer

logger = logging.getLogger(__name__)


class ObservationTypeSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        lookup_field='pk',
        view_name='observationtype-detail'
    )
    parameter = serializers.CharField()
    unit = serializers.CharField(source='referenced_unit')
    scale = fields.DisplayValueChoiceField(choices=VALUE_SCALE)
    domain_values = serializers.SerializerMethodField()

    class Meta:
        model = ParameterReferencedUnit
        fields = (
            'url',
            'code',
            'parameter',
            'unit',
            'scale',
            'description',
            'domain_values',
            'reference_frame',
            'compartment',
        )

    def get_domain_values(self, obj):
        qp = self.context['request'].query_params
        domain = qp.get('domain', None)
        return None if domain is None else obj.domain_values_for_domain(domain)


class DomainSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        lookup_field='name',
        view_name='domains-detail'
    )
    tables_url = serializers.SerializerMethodField('dt_url')

    def dt_url(self, obj):
        """Returns url to related tables for this domain.
        """
        request = self.context['request']
        scheme = request.scheme
        url_name = resolve(request.path).url_name
        if url_name == 'domains-detail':
            # Already includes the object name just append 'domaintables'
            path = urlparse(request.build_absolute_uri()).path
            url = "{}://{}{}domaintables".format(
                scheme, request.get_host(), path)
        else:
            url = "{}://{}{}{}/domaintables/".format(
                scheme, request.get_host(), request.path, quote(obj.name))

        return url

    class Meta:
        model = Domain
        fields = (
            'url',
            'name',
            'description',
            'tables_url'
        )


class DomainTableSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.SerializerMethodField('own_url')
    domain = serializers.HyperlinkedRelatedField(
        lookup_field='name',
        view_name='domains-detail',
        queryset=Domain.objects.all()
    )
    values_url = serializers.SerializerMethodField('dv_url')

    def own_url(self, obj):
        """Returns url to detail view.
        """
        request = self.context['request']
        scheme = request.scheme
        url_name = resolve(request.path).url_name
        if url_name == 'domaintables-detail':
            # Already includes the object name just append 'domaintables'
            path = urlparse(request.build_absolute_uri()).path
            url = "{}://{}{}".format(
                scheme, request.get_host(), path)
        else:
            url = "{}://{}{}{}/".format(
                scheme, request.get_host(), request.path, quote(obj.name))

        return url

    def dv_url(self, obj):
        """Returns url to related values for this table.
        """
        request = self.context['request']
        scheme = request.scheme
        url_name = resolve(request.path).url_name
        if url_name == 'domaintables-detail':
            # Already includes the object name just append 'domaintables'
            path = urlparse(request.build_absolute_uri()).path
            url = "{}://{}{}domainvalues".format(
                scheme, request.get_host(), path)
        else:
            url = "{}://{}{}{}/domainvalues/".format(
                scheme, request.get_host(), request.path, quote(obj.name))

        return url

    class Meta:
        model = DomainTable
        fields = (
            'url',
            'name',
            'rest_sync_url',
            'last_synced',
            'domain',
            'values_url'
        )


class DomainValueSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.SerializerMethodField('own_url')
    table = serializers.SerializerMethodField('dt_url')

    observation_type = serializers.HyperlinkedRelatedField(
        lookup_field='pk',
        view_name='parameterreferencedunit-detail',
        queryset=ParameterReferencedUnit.objects.all()
    )

    def own_url(self, obj):
        """Returns url to detail view.
        """
        request = self.context['request']
        scheme = request.scheme
        url_name = resolve(request.path).url_name
        if url_name == 'domainvalues-detail':
            # Already includes the object name just append 'domaintables'
            path = urlparse(request.build_absolute_uri()).path
            url = "{}://{}{}".format(
                scheme, request.get_host(), path)
        else:
            url = "{}://{}{}{}/".format(
                scheme, request.get_host(), request.path, obj.code)

        return url

    def dt_url(self, obj):
        """Returns url to related tables for this value.
        """
        request = self.context['request']
        scheme = request.scheme
        url_name = resolve(request.path).url_name
        url_path_parts = urlparse(request.build_absolute_uri()).path.split('/')

        if url_name == 'domainvalues-detail':
            path = '/'.join(url_path_parts[0:-3])
        else:
            path = '/'.join(url_path_parts[0:-2])

        url = "{}://{}{}/".format(scheme, request.get_host(), path)

        return url

    class Meta:
        model = DomainValue
        fields = (
            'url',
            'code',
            'description',
            'begin_date',
            'end_date',
            'value_category',
            'table',
            'observation_type'
        )


class DataSourceSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        lookup_field='uuid',
        view_name='datasource-detail'
    )
    node = NodeSerializer()

    class Meta:
        model = DataSource
        fields = ('url', 'node', 'uuid', 'name')
