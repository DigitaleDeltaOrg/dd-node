# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import time
import uuid

from django.contrib.gis.db import models
from django.core.cache import cache
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from json_field import JSONField
from tls import request

from dd_node.exceptions import EnhanceYourCalm
from dd_node.models import BaseModel
from dd_node.models import Location
from dd_node.models import Node, get_default_node
from dd_node.models import ParameterReferencedUnit, DataSource


logger = logging.getLogger(__name__)

PRU_PREFIXES = ['WNS', 'HCT', 'FCT', 'GWm']


class TimeseriesType(BaseModel):
    code = models.CharField(
        max_length=128,
        help_text=_("ID of the timeseries type."),
    )
    name = models.CharField(
        max_length=128,
        help_text=("Type of timeseries"),
    )


# TODO: fixtures aanpassen?
class Timeseries(BaseModel):

    _lock_key = None
    _now = None

    class ValueType:
        INTEGER = 0
        FLOAT = 1
        TEXT = 4
        IMAGE = 5
        MOVIE = 8
        FILE = 10
        FLOAT_ARRAY = 12

    VALUE_TYPE = (
        (ValueType.INTEGER, 'integer'),
        (ValueType.FLOAT, 'float'),
        (ValueType.TEXT, 'text'),
        (ValueType.IMAGE, 'image'),
        (ValueType.MOVIE, 'movie'),
        (ValueType.FILE, 'file'),
        (ValueType.FLOAT_ARRAY, 'float array'),
    )

    class QualityFlag:
        NONE = -1
        RELIABLE = 0
        DOUBTFUL = 3
        UNRELIABLE = 6
        # NB: DDSC is using str not int.
        # Validation relies on this:
        assert RELIABLE < DOUBTFUL < UNRELIABLE

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

    name = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text=_("Optional name for timeseries"),
        db_index=True,
    )

    description = models.TextField(
        default="",
        blank=True,
        null=True,
        help_text=_("optional description for timeseries")
    )

    value_type = models.SmallIntegerField(default=1, choices=VALUE_TYPE)

    location = models.ForeignKey(
        Location,
        related_name='timeseries'
    )

    # code: this is the organisation's ID of the timeseries
    # (and not the organisation's ID).
    code = models.CharField(
        max_length=128,
        help_text=_("ID of the timeseries assigned by the organisation."),
    )

    observation_type = models.ForeignKey(
        ParameterReferencedUnit,
        verbose_name=_("observation type"),
        null=True,
    )

    datasource = models.ForeignKey(
        DataSource,
        null=True,
        on_delete=models.SET_NULL,
    )

    timeseries_type = models.ForeignKey(
        TimeseriesType,
        null=True,
        on_delete=models.SET_NULL,
    )

    device = models.CharField(_("Device"), max_length=128, blank=True)

    interval = models.IntegerField(
        blank=True,
        help_text="interval at which data is collected in seconds",
        null=True,
    )

    start = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Timestamp of first value")
    )

    last_value_decimal = models.FloatField(null=True, blank=True)
    last_value_text = models.TextField(null=True, blank=True)

    end = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Timestamp of latest value")
    )

    last_modified = models.DateTimeField(
        _("Date last modified via the API"),
        blank=True,
        null=True)

    last_modified_by = models.CharField(
        _("Last modified by user via the API"),
        max_length=64,
        blank=True)

    extra_metadata = JSONField(_("Extra metadata"), null=True)

    class Meta(BaseModel.Meta):
        unique_together = (("location", "code"))
        verbose_name = _("Timeseries")
        verbose_name_plural = _("Timeseries")

    def __unicode__(self):
        return "{}".format(self.name)

    def natural_key(self):
        return (self.uuid, )

    def save(self, *args, **kwargs):
        """Update num_timeseries of object on save.
        """
        super(Timeseries, self).save(*args, **kwargs)
        try:
            self.location.object.update_num_timeseries()
        except AttributeError:
            pass

    def get_value_type(self):
        value_type = dict(self.VALUE_TYPE)
        return value_type[self.value_type]

    @property
    def last_value(self):
        if self.is_numeric:
            # TODO: explain next line. This tests for NaN?
            # Shouldn't +inf and -inf return None too?
            return None if self.last_value_decimal != self.last_value_decimal \
                else self.last_value_decimal
        return self.last_value_text

    @cached_property
    def is_numeric(self):
        return self.value_type in (
            Timeseries.ValueType.INTEGER,
            Timeseries.ValueType.FLOAT,
        )

    @cached_property
    def number_of_values_per_timestamp(self):
        return (1 if self.value_type != Timeseries.ValueType.FLOAT_ARRAY
                else self.location.number_of_values_per_timestamp)

    @cached_property
    def is_file(self):
        return self.value_type in (
            Timeseries.ValueType.IMAGE,
            Timeseries.ValueType.MOVIE,
            Timeseries.ValueType.FILE
        )

    @property
    def parameter(self):
        return getattr(
            self.observation_type, 'parameter', None)

    @property
    def unit(self):
        return getattr(
            self.observation_type, 'unit', None)

    @property
    def reference_frame(self):
        return getattr(self.observation_type, 'reference_frame', None)

    @property
    def compartment(self):
        return getattr(self.observation_type, 'compartment', None)

    @property
    def scale(self):
        return getattr(self.observation_type, 'scale', None)

    @property
    def linked(self):
        return self.extra_metadata.get('linked', False)

    def lock(self):
        if hasattr(request, 'session'):
            session = request.session.session_key
            self._lock_key = 'lock_{}_timeseries_{}'.format(session, self.uuid)
            self._now = time.time()
            cache.set(self._lock_key, self._now, 120)

    @property
    def has_lock(self):
        if self._lock_key is None:
            return True
        elif cache.get(self._lock_key) <= self._now:
            return True
        raise EnhanceYourCalm("Aborted, in favour of a younger request.")

    @staticmethod
    def __can_validate(thresholds):
        """Check validation thresholds.

        Args:
          thresholds: an iterable of validation thresholds (floats).

        Returns:
          bool: True if validation is required/possible, False otherwise.

        """
        thresholds = [x for x in thresholds if x is not None]

        if not thresholds:
            return False  # Nothing to do.
        elif not all(x < y for x, y in zip(thresholds, thresholds[1:])):
            logger.error("Insane validation thresholds.")
            return False
        else:
            return True

    def __update_first_and_last(self, first_value_timestamp,
                                last_value_timestamp, last_value):
        changed = False

        if self.start is None or first_value_timestamp < self.start:
            self.start = first_value_timestamp
            changed = True

        if self.end is None or last_value_timestamp >= self.end:
            self.end = last_value_timestamp
            if self.value_type in (Timeseries.ValueType.INTEGER,
                                   Timeseries.ValueType.FLOAT):
                self.last_value_decimal = last_value
            else:
                self.last_value_text = last_value
            changed = True

        if changed:
            self.save()
