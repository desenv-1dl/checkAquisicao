# -*- coding: utf-8 -*-
import os

# Qt imports
from PyQt4 import QtGui, uic, QtCore
import resources 
from PyQt4.QtCore import QSettings, pyqtSignal, pyqtSlot, SIGNAL, QObject
import qgis.utils
from qgis.core import QgsPoint
from PyQt4.QtGui import QSplitter, QPushButton, QComboBox, QIcon, QMessageBox
from PyQt4.Qt import QWidget

class Main:
    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.canvas.xyCoordinates.connect(self.showXY)
        self.iface.layerTreeView().clicked.connect(self.verificarCamada)
        self.iface.actionAddFeature().toggled.connect(self.verificarCamada)
        
    def initGui(self):
        pass
  
    def unload(self):
        pass  
      
    def verificarCamada(self):
        print self.iface.activeLayer().name()
          
    def showXY(self, a):
        print a.x(), a.y()
