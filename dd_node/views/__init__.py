# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from rest_framework.viewsets import ReadOnlyModelViewSet

from .messages import InboxViewSet  # NOQA
from .search import SearchViewSet  # NOQA
from dd_node import serializers
from dd_node.mixins import ExceptionMixin
from dd_node.mixins import QuerySetMixin


def as_view_set(model):
    """Factory method for creating ViewSet classes.

    Args:
        model (str):

    Returns:
        A type object: a subclass of ReadOnlyModelViewSet.

    """
    name = str("{}ViewSet".format(model))
    bases = (ExceptionMixin, QuerySetMixin, ReadOnlyModelViewSet)
    serializer_class = getattr(serializers, "{}Serializer".format(model))
    attrs = dict(serializer_class=serializer_class)
    if hasattr(serializer_class.Meta.model, "geometry"):
        attrs["__doc__"] = _("Supports spatial filtering.")
        attrs["bbox_filter_field"] = "geometry"
        attrs["bbox_filter_include_overlapping"] = True
        attrs["distance_filter_field"] = "geometry"
        attrs["distance_filter_convert_meters"] = True
    return type(name, bases, attrs)
