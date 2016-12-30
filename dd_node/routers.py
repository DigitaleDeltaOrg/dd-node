# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.


# Taken from answer on stackoverflow
# http://stackoverflow.com/questions/24311893/
#   ordering-items-on-the-root-api-view-for-defaultrouter

from rest_framework import routers
from rest_framework import views
from rest_framework.response import Response
from rest_framework.reverse import reverse
import operator
import collections


class OrderedDefaultRouter(routers.DefaultRouter):

    def get_api_root_view(self):
        """
        Return a view to use as the API root but do it with ordered links.
        """
        api_root_dict = {}
        list_name = self.routes[0].name
        for prefix, viewset, basename in self.registry:
            api_root_dict[prefix] = list_name.format(basename=basename)

        class APIRoot(views.APIView):
            _ignore_model_permissions = True

            def get(self, request, format=None):
                ret = {}
                for key, url_name in api_root_dict.items():
                    ret[key] = reverse(
                        url_name, request=request, format=format)
                sorted_ret = collections.OrderedDict(
                    sorted(ret.items(), key=operator.itemgetter(0)))
                return Response(sorted_ret)

        return APIRoot.as_view()
