# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.


"""Utility functions related to conversion."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ciso8601 import parse_datetime
from datetime import datetime
import logging

import importlib
import pytz
import uuid

from pyproj import Geod
from math import sqrt
from osgeo.ogr import osr

logger = logging.getLogger(__name__)

EPOCH_NAIVE = datetime.utcfromtimestamp(0)
EPOCH_AWARE = EPOCH_NAIVE.replace(tzinfo=pytz.UTC)

WGS84 = 4326

CSV_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
"""string: template for MS Excel readable datetime string format
"""


def distances_in_meters(distances, coords):
    """
    distances from degrees to meters for

    :param distances: numpy array of distances as calculated by raster store
    :param coords: 2 coordinate pairs that make up a line.
    :returns: numpy array of distances in meters not degrees
    """
    start, end = coords  # in ((lon, lat), (lon, lat))

    geod = Geod(ellps="WGS84")
    angle1, angle2, distance = geod.inv(start[0], start[1], end[0], end[1])

    pyth_dist = sqrt(((start[0] - end[0]) ** 2) +
                     ((start[1] - end[1]) ** 2))

    d_in_m = distances * distance / pyth_dist
    return d_in_m


def get_wgs84_transform(geometry):
    """Return CoordinateTransformation object for geometry to WGS84.

    :param geometry: ogr geometry
    :returns: CoordinateTransformation
    """
    source_srs = geometry.GetSpatialReference()
    target_srs = osr.SpatialReference()
    target_srs.ImportFromEPSG(WGS84)
    coord_transformation = osr.CoordinateTransformation(source_srs, target_srs)

    return coord_transformation


def class_for_name(fqcn):
    """Get class from fully qualified class name.

    Args:
      fqcn (str): Fully qualified class name.

    Returns:
      A class - not a class instance.

    """
    module_name, class_name = fqcn.rsplit(".", 1)
    module = importlib.import_module(module_name)

    return getattr(module, class_name)


def timestamp_ms_as_datetime(timestamp):
    """Returns timestamp in ms as Python datetime object.

    Args:
        timestamp (int): timestamp in ms.

    Returns:
        Python datetime object
    """
    return datetime.utcfromtimestamp(timestamp / 1000.)


def datetime_as_csv_string(datetime):
    """Returns timestamp in ms as formatted string.

    Args:
        datetime (int): timestamp in ms

    Returns:
        date string formatted according to `CSV_DATETIME_FORMAT`
    """
    amsterdam = pytz.timezone('Europe/Amsterdam')

    return pytz.UTC.localize(timestamp_ms_as_datetime(datetime)).astimezone(
        amsterdam).strftime(CSV_DATETIME_FORMAT)


def is_uuid(value):
    """Test if a UUID can be created from value.

    Args:
      value (str, unicode): a representation of a UUID.

    Returns:
      bool: True if a UUID representation, False otherwise.

    """
    if isinstance(value, uuid.UUID):
        logger.debug("UUID instance")
        return True

    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


def to_numeric(lit):
    """Return value of numeric literal string or ValueError exception.

    http://rosettacode.org/wiki/Determine_if_a_string_is_numeric#Python

    Args:
      lit (str): a string literal, e.g. '1', '1.2', etc.

    Returns:
      The return type will vary depending on the input, for example:
        '1' returns 1 (an int).
        '1.2' returns 1.2 (a float).
        '4.08E+02' returns (a float).
        '1j' returns 1j (a complex number).

    Raises:
      ValueError: if the literal does not represent a number.

    """
    # Handle '0'
    if lit == '0':
        return 0

    # Hex/Binary
    litneg = lit[1:] if lit[0] == '-' else lit
    if litneg[0] == '0':
        if litneg[1] in 'xX':
            return int(lit, 16)
        elif litneg[1] in 'bB':
            return int(lit, 2)
        else:
            try:
                return int(lit, 8)
            except ValueError:
                pass

    # Int/Float/Complex
    try:
        return int(lit)
    except ValueError:
        pass
    try:
        return float(lit)
    except ValueError:
        pass
    return complex(lit)


def datetime_to_milliseconds(dt):
    """Convert a datetime to milliseconds since the epoch.

    Args:
        dt: either a naive datetime in UTC or a time-zone aware datetime
    Returns:
        milliseconds since the epoch (an integer)

    """
    if dt.tzinfo is None:
        delta = dt - EPOCH_NAIVE
    else:
        delta = dt - EPOCH_AWARE
    return int(delta.total_seconds() * 1000)


def string_to_milliseconds(dt):
    """Convert an ISO 8601 datetime string to milliseconds since the epoch.

    Args:
        dt: an ISO 8601 datetime string, e.g. '2013-08-29T08:07:44Z'
    Returns:
        milliseconds since the epoch (a float)

    """
    return datetime_to_milliseconds(parse_datetime(dt))
