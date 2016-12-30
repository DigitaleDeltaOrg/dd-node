# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.shortcuts import redirect

from dd_node.routers import OrderedDefaultRouter
from dd_node.views import domain, generic, spatial, temporal, SearchViewSet

admin.autodiscover()

#########################
# Django Rest Framework #
#########################

router = OrderedDefaultRouter()

router.register(r'locations', spatial.LocationViewSet, base_name="locations")
router.register(
    r'timeseries', temporal.TimeseriesViewSet, base_name="timeseries")
router.register(r'observationtypes',
                domain.ObservationTypeViewSet,
                base_name='observationtype')

router.register(r'search', SearchViewSet, base_name='search')

router.register(
    r'nodes', generic.NodeViewSet, base_name="node")
router.register(
    r'datasources', domain.DataSourceViewSet, base_name="datasource")
router.register(r'timeseriestypes', temporal.TimeseriesTypeViewset,
                base_name="timeseriestype")

#######################
# DRF Admin endpoints #
#######################

urlpatterns = [
    ###########
    # Generic #
    ###########
    url(r'^$', lambda x: port_redirect(x)),

    url(r'^api-auth/', include('rest_framework.urls',
        namespace='rest_framework')),

    url(r'^api/', include(router.urls)),

]

urlpatterns += staticfiles_urlpatterns()


def port_redirect(request):
    scheme = settings.PROTOCOL
    host = request.get_host().split(':')[0]
    port = settings.CLIENT_PORT
    return redirect('{}://{}:{}'.format(scheme, host, port), request)

if settings.DEBUG:
    from django.views.static import serve
    import debug_toolbar
    urlpatterns += [
        # static files (images, css, javascript, etc.)
        url(r'^media/(?P<path>.*)$', serve,
            {'document_root': settings.MEDIA_ROOT}),
        # explicit setup of django debug toolbar (issue #1455).
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
