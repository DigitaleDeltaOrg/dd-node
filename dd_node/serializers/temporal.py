# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime
import logging

from django.utils.dateparse import parse_datetime
from rest_framework import serializers
from rest_framework.fields import CharField
from rest_framework.fields import DateTimeField
from rest_framework.reverse import reverse
import pytz

from dd_node import fields
from dd_node.models import Timeseries
from dd_node.models import TimeseriesType
from dd_node.models import VALUE_SCALE
from dd_node.serializers.domain import ObservationTypeSerializer
from dd_node.serializers.domain import DataSourceSerializer
from dd_node.serializers.generic import NodeSerializer
from dd_node.serializers.spatial import LocationSerializerList
from dd_node.serializers.spatial import LocationSerializerRelated
from dd_node.utils.conversion import datetime_to_milliseconds as ms

logger = logging.getLogger(__name__)


def parse_datetime_param(date_param, return_type='datetime'):
    """ Takes a date(time) parameter in either

    * UNIX Timestamp (in ms) or
    * ISO8601 datetime string with timezone

    and returns a Python datetime object or a UNIX timestamp.

    Note that this function doesn't support the entire ISO8601 standard.
    This function needs a full date and time with a timezone specified.
    """

    if date_param is None or date_param == "":
        return None

    try:
        parsed_as_timestamp = int(date_param)
    except ValueError:
        parsed_as_datetime = parse_datetime(date_param)
        # An invalid datetime (e.g. 2001-01-40T10:10:10Z) will raise an
        # exception
        if parsed_as_datetime is None:
            # It's not a valid input (e.g. 2001-01-AA)
            raise ValueError("Not a valid value: {}.".format(date_param))
        elif not parsed_as_datetime.tzinfo:
            raise ValueError(
                "Not a valid value: {}, missing time zone information.".format(
                    date_param))

        if return_type == 'datetime':
            return parsed_as_datetime
        else:
            return ms(parsed_as_datetime)
    else:
        if return_type == 'datetime':
            return datetime.fromtimestamp(parsed_as_timestamp / 1000, pytz.UTC)
        else:
            return parsed_as_timestamp


class TimeseriesTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TimeseriesType
        fields = ('url', 'code', 'name')


class TimeseriesSerializerBase(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        lookup_field='uuid',
        view_name='timeseries-detail')
    node = NodeSerializer()
    uuid = serializers.UUIDField(read_only=True)
    code = serializers.CharField()
    value_type = fields.DisplayValueChoiceField(choices=Timeseries.VALUE_TYPE)
    observation_type = ObservationTypeSerializer()
    datasource = DataSourceSerializer()
    timeseries_type = CharField(source='timeseries_type.code')
    scale = fields.DisplayValueChoiceField(choices=VALUE_SCALE)
    extra_metadata = fields.JSONSerializerField(
        allow_null=True, required=False)
    start = fields.TimestampField(read_only=True)
    end = fields.TimestampField(read_only=True)
    last_value = fields.LastValue(
        read_only=True, view_name='timeseries-data-detail')
    created = fields.TimestampField(read_only=True)
    last_modified = serializers.DateTimeField(
        read_only=True, default=datetime.now)
    last_modified_by = serializers.CharField(read_only=True)
    events = serializers.SerializerMethodField()

    class Meta:
        model = Timeseries

    def get_events(self, obj):
        params = self.context['request'].query_params
        if 'start' not in params or 'end' not in params:
            return
        events = self._get_events(obj)
        events = self._post_process_events(obj, events)
        return events

    def _get_events(self, obj):
        params = self.context['request'].query_params
        start = parse_datetime_param(params.get('start'), 'timestamp')
        end = parse_datetime_param(params.get('end'), 'timestamp')
        fields = params.getlist('fields')
        window = params.get('window')
        timezone = params.get('timezone')
        points = (int(float(params['min_points']))
                  if 'min_points' in params else None)

        events = obj.get_events(
            start=start,
            end=end,
            fields=fields,
            window=window,
            timezone=timezone,
            min_points=points,
        )

        if obj.is_file:
            response = [{
                'timestamp': event['timestamp'],
                'url': reverse(
                    'timeseries-data-detail',
                    args=[obj.uuid, event['timestamp']],
                    request=self.context['request'],
                ),
            } for event in events]
            return response

        return events


class TimeseriesSerializerList(TimeseriesSerializerBase):
    location = LocationSerializerRelated()

    class Meta:
        model = Timeseries
        fields = (
            'url',
            'id',
            'node',
            'uuid',
            'name',
            'code',
            'value_type',
            'interval',
            'location',
            'observation_type',
            'datasource',
            'timeseries_type',
            'start',
            'end',
            'last_value',
            'events',
        )


class TimeseriesSerializerDetail(TimeseriesSerializerBase):
    location = LocationSerializerList()

    class Meta:
        model = Timeseries
        fields = (
            'url',
            'id',
            'uuid',
            'name',
            'code',
            'description',
            'value_type',
            'interval',
            'location',
            'observation_type',
            'datasource',
            'timeseries_type',
            'device',
            'extra_metadata',
            'start',
            'end',
            'last_value',
            'created',
            'last_modified',
            'last_modified_by',
            'events',
        )


class TimeseriesSerializerRelated(TimeseriesSerializerBase):
    class Meta:
        model = Timeseries
        fields = (
            'url',
            'uuid',
            'name',
            'code',
        )


class TimeseriesSerializerFlat(TimeseriesSerializerBase):
    location = CharField(source='location.name')

    class Meta:
        model = Timeseries
        fields = (
            'uuid',
            'name',
            'parameter',
            'unit',
            'reference_frame',
            'compartment',
            'scale',
            'value_type',
            'location',
            'linked',
        )


class TimeseriesDataListSerializer(serializers.Serializer):

    datetime = DateTimeField()
    value = CharField()

    class Meta:
        pass

    def to_native(self, obj):
        return obj


class MultiTimeseriesDataListSerializer(serializers.Serializer):

    uuid = fields.UUIDField()
    events = TimeseriesDataListSerializer(many=True)

    class Meta:
        pass

    def to_native(self, obj):
        return obj
