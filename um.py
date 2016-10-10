self.canvas.setMapTool(self.toolEmit[indToolsShape][indTools])

 @pyqtSlot(QgsGeometry, str)
def on_cadTool(self, geom, command):
    CF.createFeature(self.canvas, geom, command)