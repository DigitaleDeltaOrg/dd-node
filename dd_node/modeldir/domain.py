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

from .base import BaseModel

logger = logging.getLogger(__name__)


class ValueScale:
    NOMINAL = 0
    ORDINAL = 1
    INTERVAL = 2
    RATIO = 3

VALUE_SCALE = (
    (ValueScale.NOMINAL, 'nominal'),
    (ValueScale.ORDINAL, 'ordinal'),
    (ValueScale.INTERVAL, 'interval'),
    (ValueScale.RATIO, 'ratio'),
)


# TODO: rename all ParameterReferencedUnit things to ObservationType
# Do this later (in another PR)
class ParameterReferencedUnit(BaseModel):
    code = models.CharField(
        _("Code"),
        max_length=128,
        unique=True
    )
    parameter = models.CharField(
        max_length=64,
        blank=True,
        help_text=_("Short name for parameter"),
    )
    unit = models.CharField(
        max_length=64,
        blank=True,
        help_text=_("Short name for referenced unit"),
    )
    reference_frame = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text=_("Short name for reference frame"),
    )
    compartment = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text=_("Short name for compartment"),
    )
    description = models.TextField(
        blank=True,
        help_text=_("Optional description for parameter referenced unit")
    )
    scale = models.SmallIntegerField(
        help_text=(
            "On what scale is the data in this observation type. "
            "See <a href=http://en.wikipedia.org/wiki/Level_of_measurement>"
            "Level of measurement.</a>"),
        default=ValueScale.INTERVAL,
        choices=VALUE_SCALE
    )

    class Meta(BaseModel.Meta):
        verbose_name = _("Parameter-referenced-unit")
        verbose_name_plural = _("Parameter-referenced-units")

    @property
    def referenced_unit(self):
        """Returns referenced unit.
        """
        return "{}{}".format(
            self.unit,
            '' if self.reference_frame is None else self.reference_frame,
        )

    def domain_values_for_domain(self, domain):
        return {
            value.domain_table.name.lower(): value.description for value in
            self.domain_values.filter(domain_table__domain__name=domain)
        }

    def __unicode__(self):
        return "{}: {} ({}) {}".format(
            self.code,
            self.parameter,
            self.referenced_unit,
            "" if self.compartment is None else self.compartment,
        )


class Domain(BaseModel):
    """Domain.
    """
    name = models.CharField(
        _("Domain"),
        max_length=256,
        unique=True
    )
    description = models.CharField(
        max_length=1024, help_text=_("Domain description"))

    class Meta(BaseModel.Meta):
        verbose_name = _("Domain")
        verbose_name_plural = _("Domains")

    def __unicode__(self):
        return self.name


class DomainTable(BaseModel):
    """Domain table.
    """
    name = models.CharField(max_length=256, help_text=_("Domain table name"))
    rest_sync_url = models.URLField(
        max_length=2048,
        default="",
        help_text=_("URL to REST API for synching domain"),
        null=True,
        blank=True
    )
    last_synced = models.DateTimeField(
        help_text=_("Timestamp of latest sync"),
        null=True,
        blank=True
    )
    domain = models.ForeignKey(Domain, related_name='domain_tables')

    class Meta(BaseModel.Meta):
        verbose_name = _("Domain table")
        verbose_name_plural = _("Domain tables")
        unique_together = ('domain', 'name')

    def __unicode__(self):
        return "{}, {}".format(self.domain.name, self.name)


class DomainValue(BaseModel):
    """Domain value.
    """
    code = models.CharField(
        help_text=_("Value code within domain"), max_length=12, unique=True)
    description = models.CharField(
        _("Description"), max_length=60, unique=True)
    begin_date = models.DateTimeField(
        _("Begin timestamp"),
        null=True,
        blank=True
    )
    end_date = models.DateTimeField(
        _("End timestamp"),
        null=True,
        blank=True
    )
    value_category = models.CharField(
        help_text=_("Optional category of value"),
        max_length=256,
        null=True,
        blank=True
    )
    domain_table = models.ForeignKey(DomainTable, related_name='domain_values')
    parameter_referenced_unit = models.ManyToManyField(
        ParameterReferencedUnit,
        blank=True,
        related_name='domain_values'
    )

    class Meta(BaseModel.Meta):
        verbose_name = _("Domain value")
        verbose_name_plural = _("Domain values")
        unique_together = ('domain_table', 'code')

    def __unicode__(self):
        return "{}, {}".format(self.domain_table.name, self.code)


class DataSource(BaseModel):
    """An abstract source of data."""
    uuid = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        help_text=_("Universally unique identifier"),
    )
    name = models.CharField(
        max_length=128,
        help_text=("Data source name"),
    )
