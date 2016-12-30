# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.

from __future__ import unicode_literals

from django.http import JsonResponse
from django.utils.text import slugify
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer

from dd_node.exceptions import APIException


class ExceptionMixin(object):
    """
    Mixin to be used in Django Rest Framework's APIView.

    Handles authentication exceptions raised in middleware that were put on the
    request. It also wraps every exception into a
    dd_node.exception.APIException such that DRF handles serialization as
    per usual.

    When the original renderer format is not ``html1`` or ``json``, handler
    sets renderer to JSON and content type to ``application/json``.
    """
    def initial(self, request, *args, **kwargs):
        if hasattr(request, 'AUTHENTICATION_EXCEPTION'):
            raise getattr(request, 'AUTHENTICATION_EXCEPTION')
        return super(ExceptionMixin, self).initial(request, *args, **kwargs)

    def handle_exception(self, exc):
        wrapped = APIException(exc)
        response = super(ExceptionMixin, self).handle_exception(wrapped)
        accept = self.request._request.META.get('HTTP_ACCEPT', '').split(',')
        if 'text/html' in accept:
            self.request.accepted_renderer = BrowsableAPIRenderer()
            self.request.accepted_media_type = 'text/html'
            response.content_type = 'text/html'
        else:
            self.request.accepted_renderer = JSONRenderer()
            self.request.accepted_media_type = 'application/json'
            response.content_type = 'application/json'

        return response


class MultiSerializerViewSetMixin(object):
    def get_serializer_class(self):
        """
        Look for serializer class in self.serializer_action_classes, which
        should be a dict mapping action name (key) to serializer class (value),
        i.e.:

        class MyViewSet(MultiSerializerViewSetMixin, ViewSet):
            serializer_class = MyDefaultSerializer
            serializer_action_classes = {
               'list': MyListSerializer,
               'my_action': MyActionSerializer,
            }

            @action
            def my_action:
                ...

        If there's no entry for that action then just fallback to the regular
        get_serializer_class lookup: self.serializer_class, DefaultSerializer.

        Thanks gonz: http://stackoverflow.com/a/22922156/11440

        """
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super(MultiSerializerViewSetMixin,
                         self).get_serializer_class()


class QuerySetMixin(object):
    """
    Mixin to be used with Django REST framework ViewSets. It saves you from
    some repetitive code when working with (Hyperlinked)ModelSerializers.
    """
    def get_queryset(self):
        return self.serializer_class.Meta.model.objects.all()


class SafeDispatchMixin(object):
    """
    Mixin to be used on Django views. Any exception is caught and wrapped. The
    response will only hold a brief message and error codes.
    """
    def dispatch(self, request, *args, **kwargs):
        try:
            return super(SafeDispatchMixin, self).dispatch(
                request, *args, **kwargs)
        except Exception as exc:
            wrapped = APIException(exc)
            return JsonResponse(wrapped.detail, status=wrapped.status_code)
