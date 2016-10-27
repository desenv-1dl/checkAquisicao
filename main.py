# -*- coding: utf-8 -*-
import os

# Qt imports
import matplotlib.path as mplPath
import numpy as np
import psycopg2
from PyQt4 import QtGui, uic, QtCore
from qgis.core import QgsPoint , QgsDataSourceURI, QgsVectorLayer, QgsMapLayerRegistry
from qgis.gui import QgsMessageBar, QgsMapTool
from PyQt4.QtCore import QSettings, pyqtSignal, pyqtSlot, SIGNAL, QObject
import qgis.utils
from PyQt4.QtGui import QSplitter, QPushButton, QComboBox, QIcon, QMessageBox, QApplication, QCursor, QPixmap
from PyQt4.Qt import QWidget

class Main(QgsMapTool):
    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        super(Main, self).__init__(self.canvas)
        self.testDB = None
        self.testMessage = True
        self.moldura = None
        self.stdCursor = None
        self.canvas.xyCoordinates.connect(self.showXY)
        self.iface.layerTreeView().clicked.connect(self.verificarCamada)
        self.iface.actionAddFeature().toggled.connect(self.verificarCamada)
       
        
    def initGui(self):
        pass
  
    def unload(self):
        pass  
      
    def verificarCamada(self):
        if self.iface.activeLayer() :
            database = self.iface.activeLayer().styleURI().split(" ")[0][8:-1]
            if not database == self.testDB:
                self.testDB = database
                db = self.listConnections(database)
                self.setMoldura(db)
    
    def setMoldura(self, db):
        cursor = self.setDatabase(db)
        cursor.execute("select f_table_name from public.geometry_columns where f_table_schema ~ 'MOLDURA' and f_table_name ~ '^E';")
        layer = cursor.fetchall()[0][0]
        cursor.execute("SELECT array_agg( ST_x(geom)||' '||ST_y(geom))  FROM \
                        (SELECT (ST_dumppoints(geom)).geom FROM \"MOLDURA\".\"EPSG_31982\" ) AS foo_1;")
        self.moldura = cursor.fetchall()[0][0]
            
    def getMoldura(self):
        return self.moldura       
    
    def setDatabase(self, db):
        s = QSettings()
        s.beginGroup("PostgreSQL/connections")
        a=db+"/host"
        b=db+"/port"
        c=db+"/database"
        d=db+'/username'
        e=db+'/password'
        conn_string = "host="+s.value(a)+" dbname="+s.value(c)+" user="+s.value(d)+" password="+s.value(e)+" port="+s.value(b)
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        return cursor
        
    def listConnections(self, database):
        connects = {}
        s = QSettings()
        s.beginGroup("PostgreSQL/connections")
        for x in s.allKeys():
            if x[-9:] == "/username":
                db = x[:-9]
                key = s.value(db+"/database")
                connects[key] = db
        return connects[database]
    
    def point_inside_polygon(self, x,y,poly):
        n = len(poly)
        inside =False    
        p1x = float(poly[0].split(" ")[0])
        p1y = float(poly[0].split(" ")[1])
        for i in range(n):
            p2x = float(poly[i].split(" ")[0])
            p2y = float(poly[i].split(" ")[1])
            if y >= min(p1y,p2y):
                if y <= max(p1y,p2y):
                    if x <= max(p1x,p2x):
                        if p1y != p2y:
                            xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x,p1y = p2x,p2y    
        return inside
 
    def showXY(self, a):
        if self.moldura:
            point = QgsPoint(a.x(), a.y())
            if self.point_inside_polygon(float(point.x()), float(point.y()), self.moldura):
                self.testMessage = True               
            else:             
                if self.testMessage:
                    self.iface.messageBar().pushMessage(u"Atenção", u"Fora da área de aquisição!",
                                                                        level=QgsMessageBar.CRITICAL, duration=100)
                    self.testMessage = False
       