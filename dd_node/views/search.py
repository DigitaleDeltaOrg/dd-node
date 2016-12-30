# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.contrib.contenttypes.models import ContentType
from django.db.models import FloatField, Q, Value
from rest_framework.viewsets import ReadOnlyModelViewSet
from watson import search as watson
from watson.models import SearchEntry

from dd_node.mixins import ExceptionMixin
from dd_node.serializers import WatsonSearchSerializer

logger = logging.getLogger(__name__)

# A `normal` search is defined as one without `type` query string parameter(s).

MODELS_EXCLUDED_IN_NORMAL_SEARCH = set([
])

# Registering a so-called live_queryset will not obey authorisation:
# https://github.com/etianen/django-watson/wiki/registering-models.

CONDITIONS = dict(
    # Exclude rasters associated with a scenario:
    rasterstore=Q(result__isnull=True),
)


def build_model_list(types):
    model_list = []
    models = watson.get_registered_models()
    if not types:
        models = set(models).difference(MODELS_EXCLUDED_IN_NORMAL_SEARCH)
    for model in models:
        ct = ContentType.objects.get_for_model(model)
        if not types or ct.model in types:
            condition = CONDITIONS.get(ct.model, Q())
            model_list.append(model.objects.filter(condition))
    return model_list


class SearchViewSet(ExceptionMixin, ReadOnlyModelViewSet):
    """A full-text search ViewSet.

    * Example: `</api/v2/search/?q=water>`_

    **Parameters:**

    q
        *Optional* full-text search filter. A search query filter should at
        least contain two characters.

    """
    serializer_class = WatsonSearchSerializer

    def get_queryset(self):

        # These 2 ways of searching are equal:
        # - search/?q=riool%20plantsoen
        # - search/?q=riool&q=plantsoen

        query = " ".join(self.request.GET.getlist('q'))

        # These 2 ways of searching are equal:
        # - search/?type=rasterstore,scenario
        # - search/?type=rasterstore&type=scenario

        types = ",".join(self.request.GET.getlist('type'))
        types = [] if types == "" else types.split(",")

        # Idem for `exclude`:

        exclude = ",".join(self.request.GET.getlist('exclude'))
        exclude = [] if exclude == "" else exclude.split(",")

        if not query and len(types) == 0:
            return []

        models = build_model_list(types)

        if not models:
            return []

        # If `search` is called with a queryset instead of just the model,
        # authorisation is obeyed. Search results are instances of
        # watson.models.SearchEntry.

        if query:
            # Perform a search based on ranking.
            results = watson.search(query, models=models)
        else:
            # Return all entries in scope (is not really a search).
            # The serializer still expects a rank: set it to None.
            se = watson.default_search_engine
            results = SearchEntry.objects.filter(
                engine_slug=se._engine_slug
            ).filter(
                se._create_model_filter(se._get_included_models(models))
            ).annotate(
                watson_rank=Value(None, output_field=FloatField())
            ).order_by('title')

        for ex in exclude:
            results = results.exclude(url__contains="/{}".format(ex))

        return results
