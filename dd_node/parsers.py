# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from rest_framework.parsers import BaseParser, DataAndFiles, MultiPartParser

logger = logging.getLogger(__name__)


class SimpleFileUploadParser(BaseParser):
    """
    A naive raw file upload parser. Used for file POSTs.
    """
    media_type = '*/*'  # Accept anything

    def parse(self, stream, media_type=None, parser_context=None):
        logger.debug("Parsing file")
        content = stream.read()

        return DataAndFiles({}, {'file': content})


class CSVParser(BaseParser):
    """
    A csv file upload parser.
    """
    media_type = 'text/csv'

    def parse(self, stream, media_type=None, parser_context=None, uuid=None):
        logger.debug("Parsing CSV file")
        try:
            content = [line.strip().split(',')
                       for line in stream.read().split('\n') if line.strip()]
        except AttributeError:
            content = stream

        data = [{'uuid': uuid or row[1].strip('"'),
                 'events': [{'datetime': row[0].strip('"'),
                             'value': row[2].strip('"')}]}
                for row in content]

        return DataAndFiles(data, None)


class MultiPartCSVParser(MultiPartParser):
    """A CSV parser for uploads done via the DDSC management interface.

    The DDSC management interface is implemented in SmartClient and
    sends CSV as multipart/form-data.

    It appears that this parser is only invoked if your settings
    contain the following lines:

    REST_FRAMEWORK = {
        'FORM_METHOD_OVERRIDE': None,
        'FORM_CONTENT_OVERRIDE': None,
        ...
    }

    See this GitHub issue:

    https://github.com/tomchristie/django-rest-framework/issues/1346

    """
    def parse(self, stream, media_type=None, parser_context=None):
        logger.debug("Parsing %s", media_type or self.media_type)
        # `files` will be a `MultiValueDict` containing all the form files.
        # Each key can be assigned multiple values, which can be retreived
        # via getlist(). In practice, the DDSC management interface posts
        # only one key, which is assigned a single value...
        files = super(MultiPartCSVParser, self).parse(
            stream, media_type, parser_context).files
        data = []
        parser = CSVParser()
        for key in files.viewkeys():
            for item in files.getlist(key):
                data.extend(parser.parse(item).data)
        return DataAndFiles(data, None)
