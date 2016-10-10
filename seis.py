# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CADDigitize
                                 A QGIS plugin
 CAD like tools for QGis
 Fork of Rectangles Ovals Digitizing. Inspired by CadTools, LibreCAD/AutoCAD.
                              -------------------
        begin                : 2016-01-25
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Loïc BARTOLETTI
        email                : lbartoletti@tuxfamily.org
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from __future__ import print_function
from __future__ import division

from CADPoint import *
from qgis.core import (QgsPoint, QgsGeometry)


class CADLine(object):
    """Class for 2D Cartesian segment entity"""
    def __init__(self, p1, p2):
        if not all([isinstance(p, (QgsPoint, CADPoint)) for p in [p1, p2]]):
            raise AttributeError
        if p1 == p2:
            # Adapted from SymPy
            # if it makes sense to return a Point, handle in subclass
            raise ValueError(
                "CADLine requires two unique Points.")

        self._p1 = CADPoint(p1)
        self._p2 = CADPoint(p2)

    def __repr__(self):
        return "CADLine({}, {})".format(repr(self._p1), repr(self._p2))

    def __str__(self):
        return "({} {})".format(self._p1, self._p2)

    def __eq__(self, other):
        if isinstance(other, CADLine):
            oPoints = other.points
            oReverse = other.points
            oReverse.reverse()
            return self.points == oPoints or self.points == oReverse
        else:
            return False

    def __getitem__(self, it):
        return self.points[it]

    def __setitem__(self, it, val):
        if not isinstance(val, (CADPoint, QgsPoint)):
            raise AttributeError
        if it == 0:
            self._p1 = val
        elif it == 1:
            self._p2 = val
        else:
            raise ValueError

    def __contains__(self, other):
        if isinstance(other, (QgsPoint, CADPoint)):
            other = CADPoint(other)
            return bool(self.isOnSegment(other) == 2)
        elif isinstance(other, CADLine):
            return self.intersects(other)
        else:
            return False

    @property
    def p1(self):
        """The first defining point of a linear entity.
        """
        return self._p1

    @property
    def p2(self):
        """The second defining point of a linear entity.
        """
        return self._p2

    # Adapted from SymPy
    @property
    def coefficients(self):
        """The coefficients (`a`, `b`, `c`) for `ax + by + c = 0`.
        """
        p1, p2 = self.points
        if p1.x == p2.x:
            return (1, 0, -p1.x)
        elif p1.y == p2.y:
            return (0, 0, -p1.y)
        return tuple([i for i in
                      (self.p1.y - self.p2.y,
                       self.p2.x - self.p1.x,
                       self.p1.x*self.p2.y - self.p1.y*self.p2.x)])

    @property
    def length(self):
        """The length of the line.
        """
        return self.p1.distance(self.p2)

    # Adapted from SymPy
    @property
    def slope(self):
        """The slope of this linear entity, or infinity if vertical.
        """
        d1, d2 = (self.p1.x - self.p2.x, self.p1.y - self.p2.y)
        if d1 == 0:
            return "Infinity"
        return d2 / d1

    @property
    def points(self):
        """The two points used to define this linear entity.
        """
        return [self.p1, self.p2]

    @property
    def pointsXY(self):
        """The XY coordinates of points
        """
        return [self.p1.x, self.p1.y, self.p2.x, self.p2.y]

    @property
    def midpoint(self):
        """Return midpoint of CADLine
        """
        return self.p1.midpoint(self.p2)

    def isOnSegment(self, p):
        """Test if this point is on the segment defined by points a, b.
        Returns
        0 if this point is not on the open ray through a and b,
        1 if point is on open ray a,
        2 if point is within line segment,
        3 if point is on open ray b.
        """
        if not isinstance(p, (QgsPoint, CADPoint)):
            raise AttributeError

        p = CADPoint(p)
        a, b = self.points
        # algorithm from 'graphics GEMS',
        # A. Paeth: 'A Fast 2D Point-on-line test'
        if (abs((b.y - a.y) * (p.x - a.x) -
                (p.y - a.y) * (b.x - a.x)) >=
           max(abs(b.x - a.x), abs(b.y - a.y))):
            return 0
        if ((b.x < a.x and a.x < p.x) or (b.y < a.y and a.y < p.y)):
            return 1
        if ((p.x < a.x and a.x < b.x) or (p.y < a.y and a.y < b.y)):
            return 1
        if ((a.x < b.x and b.x < p.x) or (a.y < b.y and b.y < p.y)):
            return 3
        if ((p.x < b.x and b.x < a.x) or (p.y < b.y and b.y < a.y)):
            return 3

        return 2

    # Adapted from SymPy
    def isParallel(self, other):
        """Are two linear entities parallel?
        """
        if not isinstance(other, CADLine):
            raise AttributeError

        return self.angle_between(other) in (math.pi, 0)

    # Adapted from SymPy
    def isPerpendicular(self, other):
        """Are two linear entities perpendicular?
        """
        if not isinstance(other, CADLine):
            raise AttributeError

        return self.angle_between(other) == (math.pi / 2)

    # Adapted from SymPy
    def angle_between(self, other):
        """The angle formed between the two linear entities.
        """
        if not isinstance(other, CADLine):
            raise AttributeError

        v1 = self.p2 - self.p1
        v2 = other.p2 - other.p1
        return math.acos(v1.dot(v2)/(abs(v1)*abs(v2)))

    # Adapted from SymPy
    def parallel_line(self, p):
        """Create a new Line parallel to this linear entity which passes
        through the point `p`.
        """
        if not isinstance(p, (QgsPoint, CADPoint)):
            raise AttributeError

        p = CADPoint(p)
        d = self.p1 - self.p2
        return CADLine(p, p + d)

    # Adapted from SymPy
    def perpendicular_line(self, p):
        """Create a new Line perpendicular to this linear entity which passes
        through the point `p`.
        """
        if not isinstance(p, (QgsPoint, CADPoint)):
            raise AttributeError

        p = CADPoint(p)
        d1, d2 = (self.p1.x - self.p2.x, self.p1.y - self.p2.y)
        if d2 == 0:  # If a horizontal line
            if p.y == self.p1.y:  # if p is on this linear entity
                return CADLine(p, p + CADPoint(0, 1))
            else:
                p2 = CADPoint(p.x, self.p1.y)
                return CADLine(p, p2)
        else:
            p2 = CADPoint(p.x - d2, p.y + d1)
            return CADLine(p, p2)

    # Adapted from SymPy
    def perpendicular_segment(self, p):
        """Create a perpendicular line segment from `p` to this line.

        The enpoints of the segment are ``p`` and the closest point in
        the line containing self. (If self is not a line, the point might
        not be in self.)
        """
        if not isinstance(p, (QgsPoint, CADPoint)):
            raise AttributeError

        p = CADPoint(p)
        if p in self.points:
            return p
        a, b, c = self.coefficients
        if a == 0:  # horizontal
            p2 = CADPoint(p.x, self.p1.y)
        elif b == 0:  # vertical
            p2 = CADPoint(self.p1.x, p.y)
        else:
            # ax + by + c = 0
            y = (-c - a*p.x)/b
            m = self.slope
            d2 = 1 + m**2
            H = p.y - y
            dx = m*H/d2
            dy = m*dx
            p2 = CADPoint(p.x + dx, y + dy)
        return CADLine(p, p2)

    # Adapted from SymPy
    def perpendicular_bisector(self, p=None):
        """The perpendicular bisector of this segment.

        If no point is specified or the point specified is not on the
        bisector then the bisector is returned as a Line. Otherwise a
        Segment is returned that joins the point specified and the
        intersection of the bisector and the segment.
        """
        if p is None or isinstance(p, (QgsPoint, CADPoint)):
            p = CADPoint(p)
            l = self.perpendicular_line(self.midpoint)
            if p is None or p not in l:
                return l
            else:
                return CADLine(self.midpoint, p)
        else:
            raise AttributeError

    def intersects(self, other):
        if isinstance(other, CADLine):
            return self.exportToQgsGeometry().intersects(
                other.exportToQgsGeometry())
        else:
            raise AttributeError

    def sqrDistToLine(self, pt, precision=0.00001):
        if not isinstance(pt, (QgsPoint, CADPoint)):
            raise AttributeError

        pt = CADPoint(pt)
        ptX = pt.x
        ptY = pt.y
        x1, y1, x2, y2 = self.pointsXY
        # normal vector
        nx = y2 - y1
        ny = -(x2 - x1)

        t = (ptX * ny - ptY * nx - x1 * ny + y1 * nx) / \
            ((x2 - x1) * ny - (y2 - y1) * nx)

        if t < 0.0:
            minDistX = x1
            minDistY = y1
        elif t > 1.0:
            minDistX = x2
            minDistY = y2
        else:
            minDistX = x1 + t * (x2 - x1)
            minDistY = y1 + t * (y2 - y1)

        distX = (minDistX - ptX) * (minDistX - ptX)
        distY = (minDistY - ptY) * (minDistY - ptY)
        dist = distX + distY

        # prevent rounding errors if the point is directly on the segment
        if near(dist, 0.0, precision):
            minDistX = ptX
            minDistY = ptY
            dist = 0.0

        return dist, minDistX, minDistY

    def nearestPoints(self, other):
        if isinstance(other, (QgsPoint, CADPoint)):
            other = CADPoint(other)
            dist = [other.distance(p) for p in self.points]
            neareastDist = min(dist)
            idx = dist.index(neareastDist)
            return (self.points[idx], idx)
        else:
            raise AttributeError

    def intersection(self, other):
        if not isinstance(other, CADLine):
            raise AttributeError

        # public domain function by Darel Rex Finley, 2006
        # http://alienryderflex.com/intersect/
        pt_inter = CADPoint()

        Ax, Ay, Bx, By = self.pointsXY
        Cx, Cy, Dx, Dy = other.pointsXY

        if ((Ax == Bx and Ay == By) or (Cx == Dx and Cy == Dy)):
            return None

        #  (1) Translate the system so that point A is on the origin.
        Bx -= Ax
        By -= Ay
        Cx -= Ax
        Cy -= Ay
        Dx -= Ax
        Dy -= Ay

        #  Discover the length of segment A-B.
        distAB = math.sqrt(Bx*Bx+By*By)

        #  (2) Rotate the system so that point B is on the positive X axis.
        theCos = Bx/distAB
        theSin = By/distAB
        newX = Cx*theCos+Cy*theSin
        Cy = Cy*theCos-Cx*theSin
        Cx = newX
        newX = Dx*theCos+Dy*theSin
        Dy = Dy*theCos-Dx*theSin
        Dx = newX

        #  Fail if the lines are parallel.
        if (Cy == Dy):
            return None

        #  (3) Discover the position of the intersection point along line A-B.
        ABpos = Dx+(Cx-Dx)*Dy/(Dy-Cy)

        #  (4) Apply the discovered position to line A-B
        # in the original coordinate system.
        pt_inter.x = Ax+ABpos*theCos
        pt_inter.y = Ay+ABpos*theSin

        #  Success.
        return pt_inter

    def multiIntersection(self, others, notOnSegment=True, strict=True):
        """ Return the nearests intersection point from a list `others` of CADLine
        A   B  C----D  E   F
        return B and E in CD direction
        """
        if isinstance(others, list):
            liR = []
            liL = []
            li = []
            # Take all intersections
            for o in others:
                if isinstance(o, CADLine):
                    pt_i = self.intersection(o)
                    flag = True
                    flInter = (o in self)

                    if pt_i is None or (notOnSegment and flInter) or \
                                       (strict and pt_i not in o):
                        flag = False

                    if flag:
                        li.append(pt_i)
                    else:
                        li.append(None)
                else:
                    li.append(None)

            for p in li:
                if p is not None:
                    if self.nearestPoints(p)[1] == 0:
                        liL.append(p)
                        liR.append(None)
                    else:
                        liR.append(p)
                        liL.append(None)
                else:
                    liL.append(None)
                    liR.append(None)

            def changeMinusValueToMax(l, n_Val):
                for i, vl in enumerate(l):
                    if near(vl, 0.0, 0.001) or vl == -1:
                        l[i] = n_Val

            dist_liL = [p.distance(self.p1) if p is not None
                        else 0 for p in liL]
            lm = max(dist_liL)
            changeMinusValueToMax(dist_liL, math.ceil(lm)+1)
            dist_liR = [p.distance(self.p2) if p is not None
                        else 0 for p in liR]
            lm = max(dist_liR)
            changeMinusValueToMax(dist_liR, math.ceil(lm)+1)

            min_liL = min(dist_liL)
            min_liR = min(dist_liR)

            return [li[dist_liL.index(min_liL)], li[dist_liR.index(min_liR)]]

    def extended(self, p):
        """Return a CADLine if a point can extend the CADLine
        A----B          p
        will return
        A---------------p
        """
        if isinstance(p, (QgsPoint, CADPoint)):
            if CADPoint.isCollinear(self.p1, self.p2, p) == 0 and \
               self.isOnSegment(p) != 2:
                    dist = [p.distance(pl) for pl in self.points]
                    maxD = self.points[dist.index(max(dist))]
                    return CADLine(p, maxD)
            return self
        else:
            raise AttributeError

    def extension(self, p):
        """Return a CADLine if a point can be an extension of the CADLine
        A----B          p
        will return
             B----------p
        """
        if isinstance(p, (QgsPoint, CADPoint)):
            if CADPoint.isCollinear(self.p1, self.p2, p) == 0 and \
               self.isOnSegment(p) != 2:
                    dist = [p.distance(pl) for pl in self.points]
                    minD = self.points[dist.index(min(dist))]
                    return CADLine(p, minD)
            return self
        else:
            raise AttributeError

    def trim(self, other, p):
        """Return the new CADLine result of intersection with other.
        For segment AB intersected at i and clicked on p, the CADLine returned
        will iB
        A-----i------p---B
        return:
              i----------B
        """
        if isinstance(p, (QgsPoint, CADPoint)) and \
           isinstance(other, CADLine) and \
           self.intersects(other):
            p = CADPoint(p)

            try:
                pt_inter = self.intersection(other)
                p1pi = CADLine(pt_inter, self.p1)
                p2pi = CADLine(self.p2, pt_inter)
                if p1pi.isOnSegment(p) == 2:
                    return p1pi
                elif p2pi.isOnSegment(p) == 2:
                    return p2pi
                else:
                    return None
            except:
                return None

            return None
        else:
            raise AttributeError

    def exportToQgsPolyline(self):
        """Export CADLine to QgsPolyline (list of QgsPoint)
        """
        return [self.p1.toQgsPoint(), self.p2.toQgsPoint()]

    def exportToQgsGeometry(self):
        """Export CADLine to QgsGeometry (Polyline)
        """
        return QgsGeometry.fromPolyline(self.exportToQgsPolyline())

    @staticmethod
    def pointOnALine(line, pp):
        """Return orthogonal point projected (pp) on line
        """
        if not isinstance(pp, (QgsPoint, CADPoint)) or \
           not isinstance(line, CADLine):
            raise AttributeError

        p1, p2 = line.points
        pp = CADPoint(pp)

        # http://stackoverflow.com/a/15187473
        t_num = ((pp.x - p1.x) * (p2.x - p1.x) +
                 (pp.y - p1.y) * (p2.y - p1.y))
        t_denum = ((p2.x - p1.x)**2 + (p2.y - p1.y)**2)
        t = t_num / t_denum

        Dx = p1.x + t * (p2.x - p1.x)
        Dy = p1.y + t * (p2.y - p1.y)

        return CADPoint(Dx, Dy)