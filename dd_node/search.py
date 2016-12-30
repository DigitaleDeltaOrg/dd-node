# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

logger = logging.getLogger(__name__)


class SearchMixin(object):

    def get_title(self, obj):
        """Return the title of this search result.

        This is given high priority in search result ranking.

        """
        name = getattr(obj, 'name', None)
        code = getattr(obj, 'code', None)
        pk = str(obj.pk)  # TODO: something better?
        return name or code or pk

    def get_description(self, obj):
        """Return the description of this search result.

        This is given medium priority in search result ranking.

        """
        description = getattr(obj, 'description', None)
        code = getattr(obj, 'code', None)
        return description or code or ''

    def get_content(self, obj):
        """Return the content of this search result.

        This is given low priority in search result ranking.

        Traversing relationships makes building a search index slow. Stale
        results are preferred over automatically updating the index when
        related objects change. A `buildwatson` will be scheduled at
        convenient times.

        """
        content = [super(SearchMixin, self).get_content(obj)]
        if hasattr(obj, 'locations'):
            for l in obj.locations:
                content.append(l.name or '')
                content.append(l.code or '')
                for t in l.timeseries.all():
                    content.append(t.name or '')
                    content.append(t.description or '')
                    if t.observation_type:
                        pru = t.observation_type
                        content.append(pru.parameter or '')
        return ' '.join(content)

    def get_meta(self, obj):
        """Return meta data of this search result.

        For reasons of performance, this information is not retrieved
        at search time, but stored when building the search index.

        """
        meta = super(SearchMixin, self).get_meta(obj)
        meta['model'] = obj.__class__.__name__.lower()
        if hasattr(obj, 'geometry') and obj.geometry is not None:
            meta['x'] = obj.geometry.centroid.x
            meta['y'] = obj.geometry.centroid.y
            meta['z'] = getattr(self, 'zoom_level', None)
        meta['uuid'] = getattr(obj, 'uuid', None)
        return meta
