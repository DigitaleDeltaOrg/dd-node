# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from rest_framework.response import Response
from uuid import UUID

from dd_node.utils.conversion import is_uuid


class UUIDFilterMixin(object):
    """Method to filter on multiple uuids.

    Allows for filtering on comma seperated list of uuids
    """
    def filter_uuid(self, name, queryset, value):
        """Filter on UUIDs.

        E.g. ?uuid=<UUID>,<UUID>,...

        """
        # str => UUID => str will give us the canonical format (with hyphens,
        # that is).
        uuids = [str(UUID(uuid)) for uuid in value.split(',') if is_uuid(uuid)]
        if uuids:
            # NB: uuid__iregex is used, because there is no uuid__iin
            # (a case-insensitive __in). UUIDs are not consistently
            # written in lower case.
            regex = '({})'.format('|'.join(uuids))
            kwargs = {name + '__iregex': regex}
            return queryset.filter(**kwargs)
        else:
            return self.Meta.model.objects.none()


class PartialUUIDMixin(object):

    def get_object_from_uuid(self, uuid=None):
        if uuid is None:
            raise Http404(_("Please provide uuid."))
        if len(uuid) < 7:
            raise Http404(_("Requested resource UUID too short."))
        queryset = self.model.objects.all()
        return get_object_or_404(queryset, uuid__startswith=uuid)

    def retrieve(self, request, uuid=None):
        obj = self.get_object_from_uuid(uuid=uuid)
        context = {"request": request}
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(obj, context=context)
        return Response(serializer.data)
