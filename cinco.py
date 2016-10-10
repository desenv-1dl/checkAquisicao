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

from qgis.core import (QgsRectangle, QgsPoint, QgsGeometry)
from CADLine import *
from CADUtils import *
from CADPoint import *
import math


class CADRectangle(object):
    def __init__(self, p1, p2, p3, p4, tolerance=0.1):
        if isinstance(p1, (QgsPoint, CADPoint)) and \
           isinstance(p2, (QgsPoint, CADPoint)) and \
           isinstance(p3, (QgsPoint, CADPoint)) and \
           isinstance(p4, (QgsPoint, CADPoint)):
            self.__points = [CADPoint(p1), CADPoint(p2),
                             CADPoint(p3), CADPoint(p4)]
            if not self.isValid(tolerance):
                self.__points = [CADPoint(0.0, 0.0)]*4
        else:
            self.__points = [CADPoint(0.0, 0.0)]*4
        self.__update()

    def __str__(self):
        s = "Rectangle:\n" + \
            "Height: %.3f" % (self._height) + '\n' + \
            "Width: %.3f" % (self._width) + '\n' + \
            "Angle: %.3f" % (self._angle) + '\n' + \
            "Center: %s" % (self._center) + '\n'

        return s

    def __repr__(self, precision=3):
        s = "CADRectangle("
        i = 0
        while i < 4:
            s += "{}".format(self.__points[i])
            i += 1
            if i <= 3:
                s += ", "
        s += ")"
        return s

    def __eq__(self, other):
        return self.__points == other.__points

    def __iter__(self):
        i = 0
        n = 4
        while i < n:
            yield self.__points[i]
            i += 1

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, h):
        if isinstance(h, (float, int, long)):
            r = self.by2PointsAndHeight(self.__points[0],
                                        self.__points[1],
                                        h)
            self.__points[2:] = r.__points[2:]
            self.__update()

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, w):
        if isinstance(w, (float, int, long)):
            r = self.by2PointsAndWidth(self.__points[0],
                                       self.__points[3],
                                       w)
            self.__points[1:3] = r.__points[1:3]
            self.__update()

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, a):
        if isinstance(a, (float, int, long)):
            self.rotate(self._center, a)

    @property
    def center(self):
        return self._center

    @center.setter
    def center(self, pointC):
        if isinstance(pointC, CADPoint):
            offsetX = pointC.x - self._center.x
            offsetY = pointC.y - self._center.y
            self._center = pointC
            for i, p in enumerate(self.__points):
                self.__points[i] = CADPoint(p.x+offsetX, p.y+offsetY)
            self.__updateMin()
            self.__updateMax

    def __updateHeight(self):
        self._height = self.__ymax - self.__ymin

    def __updateWidth(self):
        self._width = self.__xmax - self.__xmin

    def __updateAngle(self):
        self._angle = self.__points[0].getAngleOfLineBetweenTwoPoints(
            self.__points[1])

    def __updateCenter(self):
        self._center = self.__points[0].midpoint(self.__points[2])

    def __updateMax(self):
        self.__xmax = max([p.x for p in self.__points])
        self.__ymax = max([p.y for p in self.__points])

    def __updateMin(self):
        self.__xmin = min([p.x for p in self.__points])
        self.__ymin = min([p.y for p in self.__points])

    def __update(self):
        self.__updateMax()
        self.__updateMin()
        self.__updateHeight()
        self.__updateWidth()
        self.__updateCenter()
        self.__updateAngle()

    def rotate(self, pr, a):
        """Rotate a CADRectangle with angle `a` and base point `pr`
        D-------C
        |       |
        A-------B
        """
        if not isinstance(pr, (CADPoint, QgsPoint)) \
            or not isinstance(a,
                              (float, long, int)):
                pass
        else:
            pr = CADPoint(pr)

            dist = [pr.distance(i) for i in self.__points]
            angle_exist = [pr.getAngleOfLineBetweenTwoPoints(p)
                           for p in self.__points]
            for i, p in enumerate(self.__points):
                self.__points[i] = pr.pointProjected(dist[i],
                                                     angle_exist[i] + a)
            self.__update()

    def isSquare(self, tolerance=0.00001):
        """Return True if CADRectangle is a square."""
        p1, p2, p3, p4 = self.__points[:]
        return near(p1.distance(p2), p1.distance(p4), tolerance)

    def isValid(self, tolerance=0.1):
        """Return True if is really a rectangle"""
        if not isinstance(tolerance, (float, int, long)):
            tolerance = 0.1

        p1, p2, p3, p4 = self.__points[:]
        p12 = p1.getAngleOfLineBetweenTwoPoints(p2)
        p23 = p2.getAngleOfLineBetweenTwoPoints(p3)
        a1 = p23-p12

        p34 = p3.getAngleOfLineBetweenTwoPoints(p4)
        p41 = p4.getAngleOfLineBetweenTwoPoints(p1)
        a2 = p41-p34

        if self.__points == [CADPoint(0.0, 0.0)]*4:
            return False

        if len(set(self.__points)) != 4:
            return False

        if not near(a1 % 90, 0.0, tolerance) or not near(a2 % 90,
                                                         0.0, tolerance):
            return False

        return True

    @classmethod
    def by2Points(cls, p1, p2):
        """Create a CADRectangle with 2 points (from extent : AC)
        D-------C
        |       |
        A-------B
        """
        if not isinstance(p1, (CADPoint, QgsPoint)) or \
           not isinstance(p2, (CADPoint, QgsPoint)):
            raise AttributeError

        p1 = CADPoint(p1)
        p2 = CADPoint(p2)

        pt0 = p1
        pt1 = CADPoint(p2.x, p1.y)
        pt2 = p2
        pt3 = CADPoint(p1.x, p2.y)

        return cls(pt0, pt1, pt2, pt3)

    @classmethod
    def byExtent(cls, p1, p2):
        """Alias method for CADRectangle.by2Points"""
        return cls.by2Points(p1, p2)

    @classmethod
    def fromCenter(cls, p1, p2):
        """Create a CADRectangle form a central point (X) and a corner (C)
        D-------C
        |   X   |
        A-------B
        """
        if not isinstance(p1, (CADPoint, QgsPoint)) or \
           not isinstance(p2, (CADPoint, QgsPoint)):
            raise AttributeError

        p1 = CADPoint(p1)
        p2 = CADPoint(p2)

        xOffset = abs(p2.x - p1.x)
        yOffset = abs(p2.y - p1.y)
        pt1 = CADPoint(-xOffset, -yOffset)
        pt2 = CADPoint(xOffset, -yOffset)
        pt3 = CADPoint(xOffset, yOffset)
        pt4 = CADPoint(-xOffset, yOffset)
        points = [pt1, pt2, pt3, pt4]
        polygon = [CADPoint(p1.x + i.x, p1.y + i.y) for i in points]
        return cls(polygon[0], polygon[1], polygon[2], polygon[3])

    @classmethod
    def by2PointsAndHeight(cls, p1, p2, h):
        """Create a CADRectangle with 2 points (AB) and the height
        D-------C
        |       |
        A-------B
        """

        if not isinstance(p1, (CADPoint, QgsPoint)) or \
           not isinstance(p2, (CADPoint, QgsPoint)) or \
           not isinstance(h, (float, long, int)):
            raise AttributeError

        p1 = CADPoint(p1)
        p2 = CADPoint(p2)

        angle_exist = p1.getAngleOfLineBetweenTwoPoints(p2)

        pt1 = p1
        pt2 = p2
        pt3 = p2.pointProjected(h, 90 + angle_exist)
        pt4 = p1.pointProjected(h, 90 + angle_exist)

        if CADPoint.isCollinear(pt1, pt2, pt3) == 0:
            pt3 = p2.pointProjected(h, 90 - angle_exist)
            pt4 = p1.pointProjected(h, 90 - angle_exist)

        return cls(pt1, pt2, pt3, pt4)

    @classmethod
    def by2PointsAndWidth(cls, p1, p2, w):
        """Create a CADRectangle with 2 points (AD) and the width
        D-------C
        |       |
        A-------B
        """

        if not isinstance(p1, (CADPoint, QgsPoint)) or \
           not isinstance(p2, (CADPoint, QgsPoint)) or \
           not isinstance(w, (float, long, int)):
            raise AttributeError

        p1 = CADPoint(p1)
        p2 = CADPoint(p2)

        angle_exist = p1.getAngleOfLineBetweenTwoPoints(p2)

        pt1 = p1
        pt2 = p1.pointProjected(w, 90 - angle_exist)
        pt3 = p2.pointProjected(w, 90 - angle_exist)
        pt4 = p2

        l = CADLine(p1, p2)
        if CADPoint.isCollinear(pt1, pt2, pt3) == 0:
            pt2 = p1.pointProjected(w, 90 + angle_exist)
            pt3 = p2.pointProjected(w, 90 + angle_exist)

        return cls(pt1, pt2, pt3, pt4)

    @classmethod
    def by3Points(cls, p1, p2, p3):
        """Create a CADRectangle with 2 points (AD) and a length (X - AD)
        D-------C
        |       X
        A-------B
        """
        if not isinstance(p1, (CADPoint, QgsPoint)) or \
           not isinstance(p2, (CADPoint, QgsPoint)) or \
           not isinstance(p3, (CADPoint, QgsPoint)):
            raise AttributeError

        p1 = CADPoint(p1)
        p2 = CADPoint(p2)
        p3 = CADPoint(p3)

        l = CADLine(p1, p2)
        angle_exist = p1.getAngleOfLineBetweenTwoPoints(p2)
        side = CADPoint.isCollinear(p1, p2, p3)
        if side == 0:
            return None

        pp = CADLine.pointOnALine(CADLine(p1, p2), p3)

        length = p3.distance(pp) * side

        p3 = p2.pointProjected(length, 90 + angle_exist)
        p4 = p1.pointProjected(length, 90 + angle_exist)

        return cls(p1, p2, p3, p4)

    @classmethod
    def byPointHeightWidthAndAngle(cls, p1, h, w, a):
        """Create a CADRectangle with base point (A) and the height, width and an angle
        D-------C
        |       |
        A-------B
        """
        if not isinstance(p1, (CADPoint, QgsPoint)) \
            or not isinstance(h,
                              (float, long, int)) \
            or not isinstance(w,
                              (float, long, int)) \
            or not isinstance(a,
                              (float, long, int)):
            raise AttributeError

        p1 = CADPoint(p1)

        p2 = p1.pointProjected(w, a)
        p3 = p2.pointProjected(h, 90 + a)
        p4 = p1.pointProjected(h, 90 + a)

        return cls(p1, p2, p3, p4)

    @classmethod
    def byPointHeightWidth(cls, p1, h, w):
        """Convenience method for byPointHeightWidthAndAngle without angle
        """
        return cls.byPointHeightWidthAndAngle(p1, h, w, 0.0)

    @classmethod
    def squareFromCenter(cls, p1, p2):
        """Create a CADRectangle (square) with 2 points (from extent : AC)
        D---C
        |   |
        A---B
        """
        if isinstance(p1, (CADPoint, QgsPoint)) and \
           isinstance(p2, (CADPoint, QgsPoint)):
            p1 = CADPoint(p1)
            p2 = CADPoint(p2)

            distance = p2.distance(p1)
            offset = distance / math.sqrt(2)
            pt1 = (-offset, -offset)
            pt2 = (offset, -offset)
            pt3 = (offset, offset)
            pt4 = (-offset, offset)
            points = [pt1, pt2, pt3, pt4]
            polygon = [CADPoint(p1.x + i[0], p1.y + i[1]) for i in points]
            return cls(polygon[0], polygon[1], polygon[2], polygon[3])
        else:
            raise AttributeError("Arguments must be type CADPoint, send : " +
                                 str(type(p1)) + " and " + str(type(p2)))
            return cls()

    @classmethod
    def fromQgsRectangle(cls, r):
        """Create a CADRectangle from a QgsRectangle
        """
        if not isinstance(r, QgsRectangle):
            raise AttributeError("Error:" + cls.__name__ + " - " + __file__)
            return cls()

        return cls.byExtent(CADPoint(r.xMinimum(), r.yMinimum()),
                            CADPoint(r.xMaximum(), r.yMaximum()))

    @classmethod
    def fromQgsGeometry(cls, g):
        """Create a CADRectangle from a QgsGeometry (Bounding Box)
        """
        if not isinstance(g, QgsGeometry):
            return cls()

        return cls.fromQgsRectangle(g.boundingBox)

    def exportToQgsGeometry(self):
        """Export CADRectangle to a QgsGeometry (Polygon)"""
        return QgsGeometry.fromPolygon([[QgsPoint(p.x, p.y)
                                         for p in self.__points]])

    def exportToQgsRectangle(self):
        """Export CADRectangle (Bounding Box) to a QgsRectangle
        Using bounding box method from QgsGeometry
        """
        return self.exportToQgsGeometry().boundingBox()