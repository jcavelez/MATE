#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Juan Camilo Vélez
'''
#======================
# imports
#======================
from PyQt5.QtGui import QIcon
from main import Ui_MainWindow  #importando archivo generado pyuic5 main.ui -o main.py
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
import Decoder
import signal
import sqlite3
import sys
import threading



class ServiceExit(Exception):
    """
    Clase Excepción para para el servicio con el botón Detener
    """
    pass

def service_shutdown(signum, frame):
    '''
    Método para detener el Thread de crearConvertidor mediante el lanzamiento de una excepción
    '''
    raise ServiceExit


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.database_name = 'MATE_DB.db'
        self.conector_BD = sqlite3.connect(self.database_name)
        self.cursor_main = self.conector_BD.cursor()
        #Inicializando BD
        try:
            self.cursor_main.execute('''CREATE TABLE Grabaciones (
                ruta text, 
                estado int)''')
            self.cursor_main.execute("""CREATE TABLE Estados (
                ID int,
                descripcion text
                )
                """)

            estados = [
                    (1,'No Procesado'),
                    (2,'En Proceso'),
                    (3,'Procesado')    
                    ]
            self.cursor_main.executemany('INSERT INTO Estados VALUES (?,?)', estados)
            self.conector_BD.commit()
        except:
            pass

        self.ui.start_button.clicked.connect(self.start_conversion)
        self.ui.input_folder_button.clicked.connect(self.set_input_folder)
        self.ui.output_folder_button.clicked.connect(self.set_output_folder)

    def get_folder(self):
        file_dialog = QFileDialog()
        folder = file_dialog.getExistingDirectory(self, 'Seleccione carpeta')

        return folder

    def set_input_folder(self):
        folder = self.get_folder()
        self.ui.input_folder_text.setText(folder)
    
    def set_output_folder(self):
        folder = self.get_folder()
        self.ui.output_folder_text.setText(folder)
    
    def disable_widgets(self):
        print('deshabilitando widgets')
        self.ui.input_folder_label.setEnabled(False)
        self.ui.input_folder_text.setEnabled(False)
        self.ui.input_folder_button.setEnabled(False)
        self.ui.output_folder_label.setEnabled(False)
        self.ui.output_folder_text.setEnabled(False)
        self.ui.output_folder_button.setEnabled(False)
        self.ui.more_option_label.setEnabled(False)
        self.ui.more_options_button.setEnabled(False)
        self.ui.delete_processed_label.setEnabled(False)
        self.ui.delete_processed_text.setEnabled(False)
        self.ui.recurrence_label.setEnabled(False)
        self.ui.recurrence_text.setEnabled(False)
        self.ui.input_format_label.setEnabled(False)
        self.ui.input_format_text.setEnabled(False)
        self.ui.output_format_label.setEnabled(False)
        self.ui.output_format_text.setEnabled(False)        
    
    def enable_widgets(self):
        print('habilitando widgets')
        self.ui.input_folder_label.setEnabled(True)
        self.ui.input_folder_text.setEnabled(True)
        self.ui.input_folder_button.setEnabled(True)
        self.ui.output_folder_label.setEnabled(True)
        self.ui.output_folder_text.setEnabled(True)
        self.ui.output_folder_button.setEnabled(True)
        self.ui.more_option_label.setEnabled(True)
        self.ui.more_options_button.setEnabled(True)
        self.ui.delete_processed_label.setEnabled(True)
        self.ui.delete_processed_text.setEnabled(True)
        self.ui.recurrence_label.setEnabled(True)
        self.ui.recurrence_text.setEnabled(True)
        self.ui.input_format_label.setEnabled(True)
        self.ui.input_format_text.setEnabled(True)
        self.ui.output_format_label.setEnabled(True)
        self.ui.output_format_text.setEnabled(True) 

    def create_converter(self):
        '''
        Metodo para crear instalacia de la clase Decoder con parametros obtenidos de la interfaz gráfica
        :return null
        '''
        #Desactivar los widgets mientras esté convirtiendo
        self.disable_widgets()
        self.ui.start_button.setIcon(QIcon('stop.svg'))

        # Activar de nuevo toda la interface
        # self.enable_widgets()
        # self.ui.start_button.setIcon(QIcon('convert.svg'))

    def start_conversion(self, event):
        print('Iniciando conversion')
        '''
        Metodo iniciar el Thread que llama al método create_Converter()
        :return null
        '''
        # Se registran señales para parar el Thread
        signal.signal(signal.SIGTERM, service_shutdown)
        signal.signal(signal.SIGINT, service_shutdown)
        self.shutdown_flag = threading.Event()
        #Se crea un Thread para manejar cada conversión con el método crearConvertidor
        self.run_thread = threading.Thread(target=self.create_converter)
        self.run_thread.setDaemon(True) 
        self.run_thread.start()
        
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())