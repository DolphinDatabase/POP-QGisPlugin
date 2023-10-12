from .map_tool import mapTool
from .identify_decorator import identifyDecorator
from qgis.gui import QgsMapCanvas
from qgis.core import QgsMapLayer
from ..interface.detail.detail_dialog import detailDialog

class identifyGleba(mapTool):

    def __init__(self, canvas: QgsMapCanvas,layer:QgsMapLayer,label: str):
        super().__init__(canvas, label)
        self.layer = layer
        self.map_tool = identifyDecorator(self)

    def canvasPressEvent(self, event):
        x, y = event.pos().x(), event.pos().y()
        results = self.map_tool.identify(x,y,[self.layer],True)
        for item in results:
            feature = item.mFeature
            dlg = detailDialog(opr=feature[1])
            dlg.show()
            result = dlg.exec_()
            