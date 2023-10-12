from qgis.gui import QgsMapTool, QgsMapToolIdentify
from qgis.core import QgsMapLayer

class identifyDecorator(QgsMapToolIdentify):
    def __init__(self, map_tool: QgsMapTool):
        self.map_tool = map_tool
        super().__init__(map_tool.canvas())