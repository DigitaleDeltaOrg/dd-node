# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import mimetypes

import pytz

from django.http import HttpResponse
from django.utils.text import slugify

from rest_framework.exceptions import MethodNotAllowed
from rest_framework.mixins import CreateModelMixin
from rest_framework.parsers import FormParser, JSONParser
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from dd_node.filters import TimeseriesFilter
from dd_node.mixins import ExceptionMixin
from dd_node.mixins import MultiSerializerViewSetMixin
from dd_node.models import Timeseries, TimeseriesType
from dd_node.parsers import CSVParser
from dd_node.parsers import MultiPartCSVParser
from dd_node.parsers import SimpleFileUploadParser
from dd_node.serializers import temporal as serializers
from dd_node.serializers.temporal import parse_datetime_param
from dd_node.utils.conversion import is_uuid
from dd_node.views.generic import add_filename_to_response

logger = logging.getLogger(__name__)

COLNAME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
COLNAME_FORMAT_MS = '%Y-%m-%dT%H:%M:%S.%fZ'  # supports milliseconds
FILENAME_FORMAT = '%Y-%m-%dT%H.%M.%S.%fZ'
GEOSERVER_FORMAT = COLNAME_FORMAT  # used in geoserver
PERMISSION_CHANGE = 'change'
DEFAULT_CONTENT_RENDERERS = (JSONRenderer.format, BrowsableAPIRenderer.format)


class TimeseriesViewSet(
        MultiSerializerViewSetMixin, ExceptionMixin, ModelViewSet):
    """Returns list of timeseries with nested location and events.

    **Parameters:**

    start
        *Optional* temporal filter on ``start``

    end
        *Optional* temporal filter on ``end``

    min_points
        *Optional* returns as few as possible but at least ``min_points``
        number of events when used in combination with ``start`` and ``end``.
        Used to limit the number of events returned for large ratios of (end -
        start) / interval. Useful eg when drawing graphs.

    window
        *Optional* temporal aggregation window when used in combination with
        ``start`` and ``end``. One of ``raw``, ``second``, ``minute``, ``5min``
        , ``hour``, ``day``, ``week``, ``month``, ``year``. Takes precedence
        over ``min_points``.

    name
        *Optional* text filter on ``name``

    code
        *Optional* text filter on ``code``

    location
        *Optional* `related filter`_ on `Locations`_

    last_value
        *Optional* text filter on ``last_value``

    search
        *Optional* case insensitive partial search on timeseries ``name`` and
        location ``name``.

    **Ordering:** fields ``name`` and ``last_modified`` can be used for
    ordering.

    Timeseries events can be limited by ``start`` and ``end``.

    Both unix epoch timestamps (ms) and iso-formatted datetimes are supported.

    Example::

        timeseries/?start=1371816000000&end=1371818100000

    Note that if ``start`` and ``end`` filters are not provided, the API will
    return ``null`` instead of all the events of each timeseries to prevent
    overloading.
    """
    model = Timeseries
    lookup_field = 'uuid'
    filter_class = TimeseriesFilter
    search_fields = ('name', 'location__name')
    ordering_fields = ('name', 'last_modified')
    ordering = ('-last_modified', )
    serializer_class = serializers.TimeseriesSerializerDetail
    serializer_action_classes = {
        'list': serializers.TimeseriesSerializerList,
        'retrieve': serializers.TimeseriesSerializerDetail,
    }

    def get_queryset(self):
        return Timeseries.objects.all()

    def filter_queryset(self, queryset):
        result = (super(TimeseriesViewSet, self)
                  .filter_queryset(queryset)
                  .exclude(name='')
                  .filter(name__isnull=False))
        return result


class MultiTimeseriesDataList(ExceptionMixin, APIView):
    """
    Used to read data from / write data to multiple time series at once.
    """
    parser_classes = JSONParser, FormParser, CSVParser, MultiPartCSVParser
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    def get(self, request):
        # The `uuid` query parameter represents the UUID of a single time
        # series or the comma-separated UUIDs of multiple time series.
        # TODO: deal with browser and server software limits on the
        # maximum length of URLs.
        uuid = request.query_params.get('uuid', '')
        uuids = [x for x in uuid.split(',') if is_uuid(x)]
        start = request.query_params.get('start')
        end = request.query_params.get('end')

        if not uuids or start is None or end is None:
            raise ValueError("Invalid request parameters.")
        data = {'uuids': uuids, 'start': start, 'end': end}
        response = Response(data)
        if request.accepted_renderer.format not in DEFAULT_CONTENT_RENDERERS:
            add_filename_to_response(response, request, "multi_timeseries")
        return response


class TimeseriesDataList(ExceptionMixin, CreateModelMixin, APIView):
    """
    Used to read data from / write data to a timeseries in json or csv format.
    """
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

    def get(self, request, uuid=None):
        """
        Request parameters:

        * start: not-specified or a timestamp or datetime;
        * end: not-specified or a timestamp or datetime;
        * format: not-specified or 'csv';
        * combine_with: not-specified or a timeseries UUID.
        """
        ts = Timeseries.objects.get(uuid=uuid)

        # grab GET parameters
        params = request.query_params
        start = parse_datetime_param(params.get('start'), 'float')
        end = parse_datetime_param(params.get('end'), 'float')
        window = params.get('window')
        timezone = params.get('timezone')
        if timezone is not None:
            timezone = pytz.timezone(timezone)
        points = long(params['min_points']) if 'min_points' in params else None
        fields = params.getlist('fields')

        if ts.is_file:
            events = ts.get_events(start=start, end=end)
            data = [{
                'timestamp': event['timestamp'],
                'url': reverse(
                    'timeseries-data-detail',
                    args=[ts.uuid, event['timestamp']],
                    request=request),
            } for event in events]
            filename = None
        else:
            filename = "{} - {}".format(
                slugify(ts.location.name), slugify(ts.name))
            data = ts.get_events(
                start=start,
                end=end,
                fields=fields,
                window=window,
                timezone=timezone,
                min_points=points,
            )
        response = Response(data)
        if request.accepted_renderer.format not in DEFAULT_CONTENT_RENDERERS:
            add_filename_to_response(response, request, filename)
        return response


class TimeseriesDataDetail(ExceptionMixin, APIView):
    """
    Get a single data point of a timeseries.

    This only works / makes sense for timeseries that look like fileseries.
    """

    parser_classes = (SimpleFileUploadParser, )

    def get(self, request, uuid=None, dt=None):
        ts = Timeseries.objects.get(uuid=uuid)
        if not ts.is_file:
            raise MethodNotAllowed(
                "Cannot GET single event detail of non-file timeseries.")
        timestamp = serializers.parse_datetime_param(dt)
        (file_data, file_mime, file_size) = ts.get_file(timestamp)
        response = HttpResponse(file_data, content_type=file_mime)
        if file_mime is not None:
            response['Content-Type'] = file_mime
        if (ts.value_type == Timeseries.ValueType.FILE):
            file_ext = mimetypes.guess_extension(file_mime)
            file_name = "{!s}-{!s}{!s}".format(ts.uuid, dt, file_ext)
            response['Content-Disposition'] = 'attachment; filename={}'.format(
                file_name)
            response.filename = file_name
        if (file_size > 0):
            response['Content-Length'] = file_size
        return response


class TimeseriesTypeViewset(ExceptionMixin, ModelViewSet):
    model = TimeseriesType
    serializer_class = serializers.TimeseriesTypeSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return TimeseriesType.objects.all()
