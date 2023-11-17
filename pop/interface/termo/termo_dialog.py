import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from PyQt5.QtCore import QSettings
import requests
from PyQt5.QtWidgets import QCheckBox,QLabel

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'termo_dialog.ui'))

class termoDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, token, parent=None):
        """Constructor."""
        super(termoDialog, self).__init__(parent)
        self.setupUi(self)
        self.token = token
        res = requests.get('http://localhost:5050/termo',headers={
            "Authorization":f"Bearer {token}"
        })
        if res.status_code == 200:
            termo = res.json()
            conditions = []
            lbl_termo = QLabel(termo['texto'],self)
            self.scrollArea_2.setWidget(lbl_termo)
            self.termo = termo
            self.btn_aceite.clicked.connect(self.handle_button)
            for condicao in termo['condicoes']:
                checkbox = QCheckBox(condicao['texto'],self)
                checkbox.stateChanged.connect(lambda state, id=condicao['id']: self.handle_checkbox(id=id,checkbox=state))
                conditions.append(checkbox)
                self.verticalLayout.addWidget(checkbox)
            self.conditions = conditions
    
    def handle_checkbox(self,id,checkbox):
        for condicao in self.termo['condicoes']:
            if id == condicao['id']:
                condicao['aceite'] = True if checkbox > 0 else False
                return
            
    def handle_button(self):
        self.termo['aceite']=True
        for condicao in self.termo['condicoes']:
            del condicao['termo_id']
        res = requests.put('http://localhost:5050/termo',json=self.termo,headers={
            "Authorization":f"Bearer {self.token}"
        })
        self.close()
        self.accept()
        
