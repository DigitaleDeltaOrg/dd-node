# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.contrib.gis.db import models

from dd_node.utils.gis import geometry_force_3D

APP_LABEL = "dd_node"


class BaseModel(models.Model):
    """Super class of dd_node models.

    """
    class Meta:
        """Instead of having a single models.py, dd_node models have been
        split over multiple modules. This approach, however, has some issues
        with South, which have been solved by explicitly setting the
        app_label.

        NB: children of abstract base classes don’t automatically become
        abstract classes themselves, see:
        https://docs.djangoproject.com/en/dev/topics/db/models/#meta-
        inheritance

        """
        abstract = True
        app_label = APP_LABEL


class ForceGeometry3DMixin(object):
    """Inherit this class if you want to force 3D geometries.

    Allows for posting, saving 2D geometries, this mixins checks dimensionality
    of geometry and converts to 3D if needed. Works for all geometry types.
    """
    def save(self, *args, **kwargs):
        """Convert geometry to 3D if needed.

        Checks is geometry has z value, if not, forces geometry to 3D.
        """
        if hasattr(self, 'geometry'):
            if self.geometry is not None and not self.geometry.hasz:
                self.geometry = geometry_force_3D(self.geometry)

        return super(ForceGeometry3DMixin, self).save(*args, **kwargs)
