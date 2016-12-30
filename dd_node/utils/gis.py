# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.

"""
GIS utils
~~~~~~~~~~~~~~~~~~~~
Miscelaneous GIS utilities
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function

import logging
import math

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import LineString
from django.contrib.gis.geos import Point
from django.contrib.gis.geos import GEOSException
from django.db import connection

logger = logging.getLogger(__name__)


def geometry_force_3D(geometry):
    """Force geometry to 3D.

    Accepts 2D and 3D geos geometry's. Wrapper around PostGIS ST_Force3D:
    http://postgis.net/docs/ST_Force_3D.html

    Args:
      geometry (obj or string): GEOS geometry (2D or 3D) or its (e)wkt.

    Returns:
      3D geos geometry
    """
    sql = "SELECT ST_Force3D('{}')".format(geometry)

    cursor = connection.cursor()
    cursor.execute(sql)
    threed_geometry = GEOSGeometry(cursor.fetchone()[0])

    return threed_geometry


def geometry_force_2D(geometry):
    """Force geometry to 3D.

    Accepts 2D and 3D geometry wkt's. Wrapper around PostGIS ST_Force2D:
    http://postgis.net/docs/ST_Force_2D.html

    Args:
      geometry (obj or string): GEOS geometry (2D or 3D) or its (e)wkt.

    Returns:
      2D geos geometry
    """
    sql = "SELECT ST_Force2D('{}')".format(geometry)

    cursor = connection.cursor()
    cursor.execute(sql)
    twod_geometry = GEOSGeometry(cursor.fetchone()[0])

    return twod_geometry


def closest_point(geom1, geom2):
    """Get the closest point on geometry 1 from geometry 2. Wrapper around
    http://www.postgis.org/docs/ST_ClosestPoint.html

    Args:
        geom1: geometry
        geom2: geometry

    Returns:
        point geometry
    """
    sql = """
    SELECT ST_ClosestPoint(ST_GeomFromText('{}'), ST_GeomFromText('{}'))
    """.format(geom1.ewkt, geom2.ewkt)
    cursor = connection.cursor()
    cursor.execute(sql)
    point = GEOSGeometry(cursor.fetchone()[0])

    return point


def distance_along_line(point, line):
    """Get the distance in meters of the closest point on a given line to a
    given point, on that line.
    http://www.postgis.org/docs/ST_LineLocatePoint.html

    Args:
        point: Point geometry
        line: Linestring geometry

    Returns:
        distance in meters (float)
    """
    sql = """
    SELECT ST_Length(ST_GeomFromText('{}')::geography),
    ST_LineLocatePoint(ST_GeomFromText('{}'), ST_GeomFromText('{}'))
    """.format(line.ewkt, line.ewkt, point.ewkt)
    cursor = connection.cursor()
    cursor.execute(sql)
    (length, fraction) = cursor.fetchone()

    return length * fraction


def calculate_area(geometry):
    """Get the area of a geometry in square meters.

    Args:
        geometry (geometry): Geos geometry.

    Returns:
        (float) Area on the geoid in square meters.
    """
    sql = """
    SELECT ST_Area(ST_GeomFromText('{}')::geography)
    """.format(geometry.ewkt)
    cursor = connection.cursor()
    cursor.execute(sql)
    (area, ) = cursor.fetchone()

    return area


def connect_lines(geom1, geom2):
    """Connect two disjoint line geometries.

    This method always tries to extend the geometry with one of its end points
    closest to the other geometry. That way the shape of both geometries is
    left intact as much as possible. Finds closest point of geom1 on geom2 and
    vice versa. Then checks which of these points is an end point and swaps
    that end point with the closest point on the other geometry, effectively
    connecting the geometries.

    Returns None for geom and changed_geom if no geometry is changed.

    Compare the situation below. This algorithm always tries to extend the end
    point on the left (o) to the closest point on the right (+), thereby
    preserving the shape of the left and right geomtry::

                         |
                         |
           ----------o   +
                         |
                         |

        or
                         |
                         |
           --------------+-o
                         |
                         |

        returns

                         |
                         |
           --------------o
                         |
                         |


    Args:
        geom1 (geometry): geos line geometry
        geom2 (geometry): geos line geometry

    Returns:
        geom, changed_geom: geom edited version of geom1 or geom2,
            changed_geom is number indicating which input geometry has changed.
            None if no geometry is changed.

    """
    point1 = closest_point(geom1, geom2)
    point2 = closest_point(geom2, geom1)

    if point1 == point2:
        # intersecting lines
        distances = {'d1': point1.distance(Point(geom1.coords[0])),
                     'd2': point1.distance(Point(geom1.coords[-1])),
                     'd3': point1.distance(Point(geom2.coords[0])),
                     'd4': point1.distance(Point(geom2.coords[-1]))}
        min_dist = min(distances, key=distances.get)
        if min_dist == 'd1':
            geom = LineString((point2.coords,) + geom1.coords[1:])
            changed_geom = 1
        elif min_dist == 'd2':
            geom = LineString(geom1.coords[:-1] + (point2.coords,))
            changed_geom = 1
        elif min_dist == 'd3':
            geom = LineString((point1.coords,) + geom2.coords[1:])
            changed_geom = 2
        elif min_dist == 'd4':
            geom = LineString(geom2.coords[:-1] + (point1.coords,))
            changed_geom = 2
        else:
            geom = None
            changed_geom = None
    else:
        # non-intersecting lines
        if point1.coords == geom1.coords[0]:
            geom = LineString((point2.coords,) + geom1.coords[1:])
            changed_geom = 1
        elif point1.coords == geom1.coords[-1]:
            geom = LineString(geom1.coords[:-1] + (point2.coords,))
            changed_geom = 1
        elif point2.coords == geom2.coords[0]:
            geom = LineString((point1.coords,) + geom2.coords[1:])
            changed_geom = 2
        elif point2.coords == geom2.coords[-1]:
            geom = LineString(geom2.coords[:-1] + (point1.coords,))
            changed_geom = 2
        else:
            geom = None
            changed_geom = None

    return geom, changed_geom


def orthogonal_lines(line, polygon, buffer_size=0.1):
    """Get orthogonal lines from start and end point to edge of polygon
    of line in polygon.

    See figure below, line `ooo` and `&&&` are returned for line `===` in
    polygon `+----+`. Useful for calculating width of polygons. If line is not
    completely within polygon returns an error.::

        +----------------------+
        |  o      &            |
        |  ========            |
        |  o      &            |
        |  o      &            |
        +----------------------+


    Args:
        line: line geometry
        polygon: polygon geometry
        buffer_size (int): buffer size in projection units

    Returns:
        (list) orthogonal lines at start point and end point of `line`

    """
    if not (polygon.contains(line)):
        raise GEOSException("Error: line is outside polygon")

    mid_point = line.interpolate_normalized(0.5)
    mid_point.set_srid(line.srid)

    sql = """
    SELECT ortho.geom FROM ST_Dump(ST_Intersection(
        ST_Boundary(ST_Buffer(ST_GeomFromText('{}'), {}, 'endcap=flat')),
        ST_GeomFromText('{}'))) ortho
    ORDER BY ST_Distance(ST_GeomFromText('{}'), ortho.geom)
    """.format(line.ewkt, buffer_size, polygon.ewkt, mid_point.ewkt)

    cursor = connection.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    line1 = GEOSGeometry(results[0][0])
    line2 = GEOSGeometry(results[1][0])
    line1.srid = line.srid
    line2.srid = line.srid
    lines = [line2, line2]

    return lines


def point_list_to_point_pairs(point_list):
    """Convert list of points to list of x, y tuples.

    Args:
      point_list (list): list of points

    Returns:
      list of x, y tuples
    """
    return zip(point_list, point_list[1:])


def point_distance(p1, p2):
    """Returns the distance between two points.

    Assumes a projection where coordinates are in meters!, like RD.

    Args:
      p1 (tuple or list): point with x and y coordinate
      p2 (tuple or list): point with x and y coordinate

    Returns:
      Distance in units of input points coordinate system.

    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]

    dist = math.sqrt(dx ** 2 + dy ** 2)
    return dist


def points_to_intervals(points, length):
    """Divide the length into intervals with one measurement point per
    interval.

    If we have a fiber of length, say, 100, and measurement points at 20.0,
    30.0 and 50.0, intervals (0.0, 25.0), (25.0, 40.0) and (40.0, 100.0) will
    be returned.

    Points are turned into floats and sorted, and values < 0 or >
    length are ignored.

    Args:
      points (list): list of points
      length (float): length to divide points

    Returns:
      sorted list of point tuples with x and y
    """

    points = sorted(float(point) for point in points)
    points = [point for point in points if 0 <= point <= length]

    result = []
    start = 0.0

    while len(points) > 1:
        end = (points[0] + points[1]) / 2
        result.append((start, end))
        points.pop(0)
        start = end

    if len(points) == 1:
        result.append((start, length))

    return result


def linestring_intervals(linestring, intervals):
    """Chop a linestring into smaller linestrings based on the intervals.

    Intervals is a list of (pos1, pos2) pairs, where pos1 and pos2 are
    in meters from the start of the linestring. 0 <= pos1, pos2 <=
    linestring.length segments.

    Args:
      linestring (list): list of coordinate tuples with x and y
      intervals (list): list of (pos1, pos2) pairs

    Returns:
      list of point tuples with x and y coordinate
    """

    for interval in intervals:
        yield find_linestring_interval(linestring, interval)


def find_linestring_interval(linestring, interval):
    """Cut interval from linestring.

    Args:
      linestring (list): list of coordinate tuples with x and y
      interval (tuple): tuple of pos1, pos2

    Returns:
      list of point tuples

    """
    start, end = interval

    point_pairs = point_list_to_point_pairs(linestring)

    i1, p1 = find_position_in_point_pairs(point_pairs, start)
    i2, p2 = find_position_in_point_pairs(point_pairs, end)

    return [p1] + linestring[i1 + 1:i2] + [p2]


def position_in_point_pair(p1, p2, pos):
    """Return interpolation of p1 and p2.

    Pos is relative position beteween p1 and p2 where pos=0.0 is p1 and
    pos=1.0 is p2.

    Args:
      p1 (tuple or list): point with x and y coordinate
      p2 (tuple or list): point with x and y coordinate
      pos (float): relative position between p1 and p2

    Returns:
      tuple of (x, y z) where z is always `0`

    """

    assert 0.0 <= pos <= 1.0

    delta = (p2[0] - p1[0], p2[1] - p1[1])

    return (p1[0] + pos * delta[0], p1[1] + pos * delta[1], 0)


def find_position_in_point_pairs(point_pairs, pos):
    """Returns index of the point pair that contains pos, and the point
    itself.

    Args:
      point_pairs (list): list of point tuples (x, y)
      pos (float): relative position between points

    Returns:
      None, None

    """

    for i, (p1, p2) in enumerate(point_pairs):
        distance = point_distance(p1, p2)

        if pos <= distance:
            return i, position_in_point_pair(p1, p2, pos/distance)

        pos -= distance

    return None, None
