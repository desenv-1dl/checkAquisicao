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

from qgis.gui import *
from qgis.core import *
from PyQt4.QtGui import *
from PyQt4.QtCore import QSettings

# our own fancy cursor
open_hand_px = QPixmap('erro.png')
open_hand_px.setMask(open_hand_px.mask())


CADCursor = QCursor(open_hand_px)


def getQgisDigitizingColor():
    r = QSettings().value("/qgis/digitizing/line_color_red", 255, type=int)
    g = QSettings().value("/qgis/digitizing/line_color_green", 0, type=int)
    b = QSettings().value("/qgis/digitizing/line_color_blue", 0, type=int)
    a = QSettings().value("/qgis/digitizing/line_color_alpha", 200, type=int)

    return QColor(r, g, b, a)


def myRubberDigit(canvas):

    w = QSettings().value("/qgis/digitizing/line_width", 1, type=int)

    rb = QgsRubberBand(canvas, True)
    rb.setColor(getQgisDigitizingColor())
    rb.setWidth(w)

    return rb


def myRubberDim(canvas):

    color = QColor()
    color.setRgba(QSettings().value("/CADDigitize/styles/mLineColorDim",
                                    2097184767, type=int))
    w = QSettings().value("/CADDigitize/styles/mLineWidthDim", 1, type=int)

    rb = QgsRubberBand(canvas, QGis.Line)
    rb.setColor(color)
    rb.setWidth(w)
    return rb


def myRubberPointSnap(canvas):
    color = QColor()
    color.setRgba(QSettings().value("/CADDigitize/styles/mLineColorSnap",
                                    2097184767, type=int))
    w = QSettings().value("/CADDigitize/styles/mMarkerSizeSpinBox",
                          3, type=int)
    s = QSettings().value("/CADDigitize/styles/mMarkerStyleComboBox",
                          2, type=int)

    rb = QgsRubberBand(canvas, QGis.Point)
    rb.setColor(color)
    rb.setWidth(w)
    rb.setIcon(s)
    return rb


def myRubberSegmentSnap(canvas):
    color = QColor()
    color.setRgba(QSettings().value("/CADDigitize/styles/mLineColorSnap",
                                    2097184767, type=int))
    w = QSettings().value("/CADDigitize/styles/mLineWidthSnap", 1, type=int)

    rb = QgsRubberBand(canvas, QGis.Line)
    rb.setColor(color)
    rb.setWidth(w)
    return rb