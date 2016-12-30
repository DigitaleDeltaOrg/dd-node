# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import uuid

from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _
from json_field import JSONField

from .base import BaseModel
from .base import ForceGeometry3DMixin
from .generic import Node, get_default_node

WGS84 = 4326

logger = logging.getLogger(__name__)


class Location(ForceGeometry3DMixin, BaseModel):
    """Location of a timeseries.

    """

    node = models.ForeignKey(
        Node,
        default=get_default_node,
        on_delete=models.PROTECT,
    )

    uuid = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        help_text=_("Universally unique identifier"),
        verbose_name="UUID"
    )

    # code: this is the ID of the location as given by the
    # organisation (and not the ID of the organisation). For PI XML,
    # this equals the locationId of the time-series header.
    code = models.CharField(
        max_length=80,
        help_text=_("ID of the location assigned by the organisation."),
        db_index=True,
    )

    name = models.CharField(
        max_length=80,
        help_text=_("Name of location"),
    )

    # The real geometry (point, linestring, polygon, etc):
    geometry = models.GeometryField(srid=WGS84, dim=3, null=True, blank=True)

    last_modified = models.DateTimeField(
        _("Date last modified via the API"),
        blank=True,
        null=True)
    last_modified_by = models.CharField(
        _("Last modified by user via the API"),
        max_length=64,
        blank=True)

    extra_metadata = JSONField(_("Extra metadata"), null=True, blank=True)

    def natural_key(self):
        return (self.uuid, )

    def __unicode__(self):
        return self.name or self.uuid

    def get_timeseries(self):
        """
        Gather all timeseries data for this location and return it with a
        unified time dimension.
        """
        timestamps = []
        for timeseries in self.timeseries.all():
            timestamps = timestamps + \
                [instant['datetime']
                    for instant in timeseries.get_events_raw()]

        timestamps = sorted(set(timestamps))

        response = [{
            'name': 'timestamp',
            'type': 'timestamp',
            'quantity': 'time',
            'unit': 'ms',
            'data': timestamps
        }]

        for timeseries in self.timeseries.all():
            data = dict([
                        (instant['datetime'], instant['value'])
                        for instant in timeseries.get_events_raw()
                        ])
            data = [data.get(timestamp, None) for timestamp in timestamps]

            response.append({
                'name': timeseries.name,
                'type': timeseries.get_value_type(),
                'quantity': timeseries.parameter,
                'unit': timeseries.unit,
                'data': data
            })

        return response

    @property
    def number_of_values_per_timestamp(self):
        obj = self.object
        if obj and hasattr(obj, 'number_of_values_per_timestamp'):
            return obj.number_of_values_per_timestamp
        else:
            return 1
