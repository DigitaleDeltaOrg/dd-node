# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from rest_framework.exceptions import ParseError
from rest_framework.pagination import PageNumberPagination
from rest_framework.pagination import LimitOffsetPagination


class LimitOffsetAndPageNumberPagination(LimitOffsetPagination,
                                         PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'

    actual_class_to_use = PageNumberPagination

    def paginate_queryset(self, queryset, request, *args, **kwargs):
        """Let the request parameters decide which type of pagination is used.
        If limit and/or offset are in the request parameters the
        LimitOffsetPagination is used.
        If page and/or page_size are in the request parameters
        PageNumberPagination is used.
        """
        self.check_invalid_query_params(request)
        if self.get_limit(request):
            self.actual_class_to_use = LimitOffsetPagination
        elif self.no_pagination(request):
            return None
        return self.actual_class_to_use.paginate_queryset(
            self, queryset, request, *args, **kwargs)

    def get_paginated_response(self, *args, **kwargs):
        return self.actual_class_to_use.get_paginated_response(
            self, *args, **kwargs)

    def get_next_link(self):
        return self.actual_class_to_use.get_next_link(self)

    def get_previous_link(self):
        return self.actual_class_to_use.get_previous_link(self)

    def get_html_context(self):
        return self.actual_class_to_use.get_html_context(self)

    def no_pagination(self, request):
        """Add support for: page_size=0 in the request parameters implies no
        pagination. This used to be a bug that was used as a feature before
        djangorestframework 3.0.
        """
        return (
            getattr(self, 'page_size_query_param', False) and
            request.query_params.get(self.page_size_query_param, 1) == '0'
        )

    def check_invalid_query_params(self, request):
        """ Check the request query parameters for invalid combinations.
        E.g. 'limit' should only be paired with 'offset' and never with 'page'
        or 'page_size'.
        Raise a 400 Bad Request error if invalid combinations are found.
        """
        query_keys = request.query_params.keys()
        page_size = getattr(self, 'page_size_query_param', '')
        params_page_intersect = set(query_keys).intersection(['page',
                                                              page_size])
        params_limit_intersect = set(query_keys).intersection(['limit',
                                                               'offset'])
        if bool(params_page_intersect) and bool(params_limit_intersect):
            raise ParseError(
                "Invalid combination of request parameters: %s and %s." %
                (params_page_intersect, params_limit_intersect))
