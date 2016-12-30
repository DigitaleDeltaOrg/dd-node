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

from dd_node.models import BaseModel

logger = logging.getLogger(__name__)


class Node(BaseModel):
    """A Node is kinda like a site in the context of a network of sites."""
    uuid = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        help_text=_("Universally unique identifier"),
    )
    name = models.CharField(
        max_length=128,
        null=True,
        help_text=("Node name"),
    )
    description = models.TextField(
        null=True,
        help_text=_("Node description"),
    )
    base_url = models.URLField(
        max_length=200,
        help_text=_("Node base url"),
    )
    master = models.BooleanField(
        default=False,
        help_text=_("Am I master?"),
    )


def get_default_node():
    """Use this callable when you need a default Node object."""
    DEFAULT_PK_FROM_FIXTURE = 1
    return DEFAULT_PK_FROM_FIXTURE
