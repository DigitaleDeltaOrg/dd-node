# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import mimetypes

from rest_framework.viewsets import ModelViewSet

from dd_node.mixins import ExceptionMixin
from dd_node.models import Node
from dd_node.serializers import generic

logger = logging.getLogger(__name__)


UNOFFICIAL_MIMETYPES_TO_FILE_EXTENSION = {
    "application/x-netcdf4": ".nc",
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
    ".xlsx"
}


def file_extension(format_=None, media_type=None):
    if media_type is None:
        return format_
    unofficial = UNOFFICIAL_MIMETYPES_TO_FILE_EXTENSION.get(media_type)
    if unofficial:
        return unofficial
    from_mimetype = mimetypes.guess_extension(media_type, strict=True)
    if from_mimetype is None:
        return format_
    return from_mimetype


def file_extension_from_request(request):
    """Finds renderers media type from request and view_func."""
    format_ = request.accepted_renderer.format
    media_type = request.accepted_renderer.media_type
    return file_extension(format_, media_type)


def add_filename_to_response(response, request, filename):
    extension = file_extension_from_request(request)
    if extension and filename:
        filename += extension
        response['Content-Disposition'] = "attachment; filename=" + filename
        response.filename = filename


class NodeViewSet(ExceptionMixin, ModelViewSet):
    lookup_field = 'uuid'
    model = Node
    serializer_class = generic.NodeSerializer

    def get_queryset(self):
        return Node.objects.all()
