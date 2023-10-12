from qgis.gui import QgsMapCanvas, QgsMapTool

class mapTool(QgsMapTool):
    def __init__(self, canvas: QgsMapCanvas, label:str):
        super().__init__(canvas)
        self.label = label