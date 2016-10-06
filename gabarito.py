# -*- coding: utf-8 -*-
from qgis.gui import QgsRubberBand, QgsMapTool, QgsMapToolCapture
from qgis.core import QgsPoint, QGis
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QColor
from PyQt4.QtCore import pyqtSignal
from math import sqrt
import main

class teste(QgsMapToolCapture):
    def __init__(self, iface):
        self.iface = iface

    def cadCanvasReleaseEvent(self, event):
        pass

    def cadCanvasMoveEvent(self, event):
        print dir(event)
        
    def keyReleaseEvent(self,  event):
        pass
   
   
        
