import os

from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal
from PyQt5.QtWidgets import QToolButton
from ...tools.map_tool import mapTool

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'tool_base.ui'))


class toolWidget(QtWidgets.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()
    customTool = pyqtSignal(mapTool)

    def __init__(self, custom_tools:[mapTool], parent=None):
        super(toolWidget, self).__init__(parent)
        self.setupUi(self)
        self.custom_tools = custom_tools
        for i,tool in enumerate(custom_tools):
            tool_button = QToolButton()
            tool_button.setText(tool.label)
            tool_button.clicked.connect(lambda: self.handleChoosetool(custom_tool=tool))
            grid_layout = self.verticalLayout
            grid_layout.addWidget(tool_button)


    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

    def handleChoosetool(self,custom_tool:mapTool):
        self.customTool.emit(custom_tool)