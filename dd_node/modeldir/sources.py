# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.


"""Time series to be imported into Lizard NXT come from different sources,
for example a file, a web service, etc. This module contains models
representing those sources.
"""

from django.db import models

from .base import BaseModel


class FileSource(BaseModel):
    """Stores properties about a time series file."""
    fullpath = models.CharField(max_length=256, unique=True)
    mtime = models.IntegerField(null=True)  # modification time
