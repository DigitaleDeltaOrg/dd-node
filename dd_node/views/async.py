# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import os

from celery import states
from celery.result import AsyncResult
from django.conf import settings
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


def _get_domain(request):
    """Return scheme + network location."""
    scheme = request.scheme
    netloc = request.META['HTTP_HOST']
    domain = "{}://{}".format(scheme, netloc)
    return domain


def _reverse(*args, **kwargs):
    """ A version of reverse that does not preserve built-in query parameters.

    DRF's reverse function does preserve built-in query params,
    e.g. ?format=netcdf, which is not always what we want.
    This version strips query parameters.

    """
    url = reverse(*args, **kwargs)
    return url[:url.find('?')]


class Task(APIView):
    """Provide information about an asynchronous task.
    """

    def get(self, request, uuid):

        result = AsyncResult(uuid)

        if result.status == states.SUCCESS:
            relpath = os.path.relpath(result.get(), settings.MEDIA_ROOT)
            url = _get_domain(request) + settings.MEDIA_URL + relpath
        else:
            url = None

        response = {
            'task_id': result.task_id,
            'task_status': result.status,
            'result_url': url,
        }

        return Response(response)


class TaskStart(APIView):

    def get(self, request, task_id=None):
        task_url = _reverse('task', args=[task_id], request=request)
        data = {
            "task_id": task_id,
            "url": task_url
        }
        return Response(data)
