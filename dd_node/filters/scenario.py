# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import rest_framework_filters as filters

from dd_node.models import Scenario
from dd_node.filters import OrganisationFilter


class ScenarioFilter(filters.FilterSet):
    organisation = filters.RelatedFilter(OrganisationFilter)
    username = filters.AllLookupsFilter()

    class Meta:
        model = Scenario
        fields = []
