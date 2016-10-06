# -*- coding: utf-8 -*-
import os

# Qt imports
from PyQt4 import QtGui, uic, QtCore
import resources 
from PyQt4.QtCore import QSettings, pyqtSignal, pyqtSlot, SIGNAL, QObject
import qgis.utils
from gabarito import teste
from PyQt4.QtGui import QSplitter, QPushButton, QComboBox, QIcon, QMessageBox
from PyQt4.Qt import QWidget

class CheckAquisicao:
    def __init__(self, iface):
	self.iface = iface
	teste(iface)


    def initGui(self):
        pass
  
    def unload(self):
       pass    
    
    
