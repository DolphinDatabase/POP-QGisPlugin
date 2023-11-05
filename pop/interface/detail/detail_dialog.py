import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from PyQt5.QtCore import QSettings
import requests
from qgis.core import QgsProject,QgsRasterLayer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd
import numpy as np

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'detail_dialog.ui'))

class detailDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self,opr:int,gleba:int,inicio:str,fim:str, parent=None):
        """Constructor."""
        super(detailDialog, self).__init__(parent)
        self.setupUi(self)
        self.loading()
        jwt = QSettings('POP','auth').value('jwt')
        self.setWindowTitle(f"Operação #{opr}")
        req = requests.get(f"http://localhost:5050/operacao/{opr}",headers={
            "Authorization":f"Bearer {jwt}"
        })
        if req.status_code==200:
            inicio = inicio.addDays(-30)
            fim = fim.addDays(60)
            time_series = requests.get(f'http://localhost:5000/time_series?gleba={gleba}&inicio={inicio.toString("yyyy-MM-dd")}&fim={fim.toString("yyyy-MM-dd")}')
            if time_series.status_code == 200:
                data = time_series.json()['data']
                series = pd.Series(data)
                df_data = series.to_frame(name='NDVI')
                df_data.index = pd.to_datetime(df_data.index, unit='ms').strftime('%Y-%m-%d')
                predict = time_series.json()['predict']
                series = pd.Series(predict)
                df_predict = series.to_frame(name='Predição')
                df_predict.index = pd.to_datetime(df_predict.index, unit='ms').strftime('%Y-%m-%d')
                df = pd.concat([df_data, df_predict], axis=1)

                print(df)

                fig, ax=plt.subplots(figsize=(9, 4))
                df['NDVI'].plot(ax=ax, label='NDVI')
                df['Predição'].plot(ax=ax, label='Predição', color='green')
                canvas = FigureCanvas(fig)
                self.lytChart.addWidget(canvas)
                canvas.draw()
                self.lbl_message_time_series.setVisible(False)
            else:
                self.setMinimumSize(681, 460)
                self.lbl_message_time_series.setStyleSheet("color: red;")
                self.lbl_message_time_series.setText("Nehuma série Temporal disponível")
            self.populate(data=req.json())
        else:
            self.error()

    def loading(self):
        self.setMinimumSize(681, 460)
        self.lbl_message.setVisible(True)
        self.frm_main.setVisible(False)

    def populate(self,data):
        self.lbl_inicio_plantio_2.setText(data['inicio_plantio'])
        self.lbl_fim_plantio_2.setText(data['fim_plantio'])
        self.lbl_inicio_colheita_2.setText(data['inicio_colheita'])
        self.lbl_fim_colheita_2.setText(data['fim_colheita'])
        self.lbl_estado.setText(data['estado']['descricao'])
        self.lbl_municipio.setText(data['municipio']['descricao'])

        self.lbl_tipo_solo_2.setText(data['solo']['descricao'])
        self.lbl_irrigacao_2.setText(data['irrigacao']['descricao'])
        self.lbl_cultivo_2.setText(data['cultivo']['descricao'])
        self.lbl_grao_semente_2.setText(data['grao_semente']['descricao'])
        self.lbl_ciclo_2.setText(data['ciclo']['descricao'])

        self.lbl_cesta_2.setText(data['empreendimento']['cesta'])
        self.lbl_zoneamento_2.setText(data['empreendimento']['zoneamento'])
        self.lbl_variedade_2.setText(data['empreendimento']['variedade'])
        self.lbl_produto_2.setText(data['empreendimento']['produto'])
        self.lbl_modalidade_2.setText(data['empreendimento']['modalidade'])
        self.lbl_atividade_2.setText(data['empreendimento']['atividade'])
        self.lbl_finalidade_2.setText(data['empreendimento']['finalidade'])

        self.lbl_message.setVisible(False)
        self.frm_main.setVisible(True)

    def error(self):
        self.lbl_message_time_series.setVisible(False)
        self.lbl_message.setVisible(True)
        self.lbl_message.setStyleSheet("color: red;")
        self.lbl_message.setText("Erro na operação")
        self.frm_main.setVisible(False)