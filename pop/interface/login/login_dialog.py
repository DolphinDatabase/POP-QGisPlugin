import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from PyQt5.QtCore import QSettings
import requests
from qgis.core import QgsProject,QgsRasterLayer

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'login_dialog.ui'))


class loginDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(loginDialog, self).__init__(parent)
        self.setupUi(self)
        self.lbl_email_error.setVisible(False)
        self.lbl_password_error.setVisible(False)
        self.lbl_error.setVisible(False)
        self.btn_login.clicked.connect(self.handle_button)
        self.txt_email.focusInEvent = self.resetEmail
        self.txt_password.focusInEvent = self.resetPassword

    def resetEmail(self, event):
        self.lbl_email_error.setVisible(False)

    def resetPassword(self, event):
        self.lbl_password_error.setVisible(False)
    
    def handle_button(self):
        email = self.txt_email.text()
        senha = self.txt_password.text()
        if email == "" or senha == "":
            if email=="":
                self.lbl_email_error.setVisible(True)
                self.lbl_email_error.setStyleSheet("color: red;")
                self.lbl_email_error.setText("Preencha o email")
            if senha == "":
                self.lbl_password_error.setVisible(True)
                self.lbl_password_error.setStyleSheet("color: red;")
                self.lbl_password_error.setText("Preencha a senha")
            return
        res = requests.post("http://localhost:5050/auth",data={
            'username':email,
            'password':senha
        })
        if res.status_code==200:
            token = res.json()['access_token']
            setting = QSettings('POP','auth')
            setting.setValue('jwt',token)
            if self.chk_map.isChecked():
                url = "type=xyz&url=https://mt1.google.com/vt/lyrs%3Ds%26x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D&zmax=18&zmin=0&http-header:referer="
                r_layer = QgsRasterLayer(url, 'POP-Map', 'wms')
                if r_layer.isValid():
                    QgsProject.instance().addMapLayer(r_layer)
                else:
                    print("layer invalid")
            self.close()
            self.accept()
        else:
            self.lbl_error.setVisible(True)
            self.lbl_error.setStyleSheet("color: red;")
            self.lbl_error.setText("Dados Inválidos!")
            return
        
