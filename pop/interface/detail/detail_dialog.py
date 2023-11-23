import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from PyQt5.QtCore import QSettings
import requests
from qgis.core import QgsProject,QgsRasterLayer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PyQt5.QtWidgets import QFileDialog
from io import BytesIO
from PIL import Image

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
            buffer = BytesIO()
            inicio = inicio.addDays(-30)
            fim = fim.addDays(60)
            time_series = requests.get(f'http://localhost:5050/time_series?gleba={gleba}&inicio={inicio.toString("yyyy-MM-dd")}&fim={fim.toString("yyyy-MM-dd")}')
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
                fig, ax=plt.subplots(figsize=(9, 4))
                df['NDVI'].plot(ax=ax, label='NDVI')
                df['Predição'].plot(ax=ax, label='Predição', color='green')
                ax.legend()
                with open(f'/tmp/{gleba}.png','wb') as img:
                    fig.savefig(buffer, format='png')
                    img.write(buffer.getvalue())
                buffer.seek(0)
                canvas = FigureCanvas(fig)
                self.lytChart.addWidget(canvas)
                canvas.draw()

                weather = time_series.json()['weather']
                weather_df = pd.DataFrame(weather)
                weather_df.index = pd.to_datetime(weather_df.index, unit='ms').strftime('%Y-%m-%d %H:%M:%S')
                fig, ax  = plt.subplots(figsize=(9, 4))
                weather_df['temp'].plot(ax=ax,label='Temperatura')
                weather_df['pressure'].plot(ax=ax,label='Pressão')
                weather_df['humidity'].plot(ax=ax,label='Humidade')
                weather_df['wind_speed'].plot(ax=ax,label='Velocidade do Vento')
                weather_df['clouds'].plot(ax=ax,label='Nuvem')
                ax.legend()
                with open(f'/tmp/{gleba}_weather.png','wb') as img:
                    fig.savefig(buffer, format='png')
                    img.write(buffer.getvalue())
                buffer.seek(0)
                canvas = FigureCanvas(fig)
                self.lytWeather.addWidget(canvas)
                canvas.draw()

                self.lbl_message_time_series.setVisible(False)
            else:
                self.setMinimumSize(681, 460)
                self.lbl_message_time_series.setStyleSheet("color: red;")
                self.lbl_message_time_series.setText("Nehuma série Temporal disponível")
            self.btn_download.clicked.connect(lambda: self.generate_pdf(req.json(),opr,gleba))
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

    def generate_pdf(self,opr:dict,id,gleba):
        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=A4)
        c.drawString(10, 810, f'Gleba: {gleba}')
        c.drawString(10, 798, f'Operação: {id}')
        c.drawString(10, 776, f'Inicio Plantio: {opr["inicio_plantio"]}')
        c.drawString(10, 764, f'Fim Plantio: {opr["fim_plantio"]}')
        c.drawString(10, 752, f'Inicio Colheita: {opr["inicio_colheita"]}')
        c.drawString(10, 740, f'Fim Colheita: {opr["fim_colheita"]}')
        c.drawString(10, 728, f'Estado: {opr["estado"]["descricao"]}')
        c.drawString(10, 716, f'Municipio: {opr["municipio"]["descricao"]}')
        c.drawString(10, 694, 'Sistema de produção Agrícola:')
        c.drawString(10, 682, f'Tipo Solo: {opr["solo"]["descricao"]}')
        c.drawString(10, 670, f'Irrigação: {opr["irrigacao"]["descricao"]}')
        c.drawString(10, 658, f'Tipo Cultivo: {opr["cultivo"]["descricao"]}')
        c.drawString(10, 646, f'Grão/Semente: {opr["grao_semente"]["descricao"]}')
        c.drawString(10, 634, f'Ciclo do Cultivar: {opr["ciclo"]["descricao"]}')
        c.drawString(10, 612, f'Empreendimento')
        c.drawString(10, 600, f'Cesta: {opr["empreendimento"]["cesta"]}')
        c.drawString(10, 588, f'Zoneamento: {opr["empreendimento"]["zoneamento"]}')
        c.drawString(10, 576, f'Variedade: {opr["empreendimento"]["variedade"]}')
        c.drawString(10, 564, f'Produto: {opr["empreendimento"]["produto"]}')
        c.drawString(10, 552, f'Modalidade: {opr["empreendimento"]["modalidade"]}')
        c.drawString(10, 540, f'Atividade: {opr["empreendimento"]["atividade"]}')
        c.drawString(10, 528, f'Finalidade: {opr["empreendimento"]["finalidade"]}')
        
        if os.path.exists(f'/tmp/{gleba}.png') and os.path.exists(f'/tmp/{gleba}_weather.png'):
            c.showPage()
            c.drawImage(f'/tmp/{gleba}.png', 10, 500, width=500, height=300)
            c.drawImage(f'/tmp/{gleba}_weather.png', 10, 180, width=500, height=300)
            os.remove(f'/tmp/{gleba}.png')
            os.remove(f'/tmp/{gleba}_weather.png')
        c.save()
        dir_selected = QFileDialog.getExistingDirectory(None, "Selecionar diretório", "", QFileDialog.ShowDirsOnly)
        if dir_selected:
            print("Diretório selecionado:", dir_selected)
            with open(f'{dir_selected}/Report_glb{gleba}.pdf', 'wb') as f:
                f.write(pdf_buffer.getvalue())