# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from rest_framework import serializers

from dd_node.models import ParameterReferencedUnit
from dd_node.serializers.domain import ObservationTypeSerializer

logger = logging.getLogger(__name__)


class ParameterReferencedUnitSerializer(ObservationTypeSerializer):
    url = serializers.HyperlinkedIdentityField(
        lookup_field='pk',
        view_name='parameterreferencedunit-detail'
    )
    parameter_short_display_name = serializers.CharField(
        source='parameter')
    referenced_unit_short_display_name = serializers.CharField(
        source='referenced_unit')

    class Meta:
        model = ParameterReferencedUnit
        fields = (
            'url',
            'code',
            'parameter_short_display_name',
            'referenced_unit_short_display_name',
            'scale',
            'description',
            'domain_values',
            'reference_frame',
            'compartment',
        )
