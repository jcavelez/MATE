#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Juan Camilo Vélez
'''
#======================
# imports
#======================
import sys
from main import Ui_MainWindow  #importando archivo generado pyuic5 main.ui -o main.py
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
import Decoder
import sqlite3



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
        dir = file_dialog.getExistingDirectory(self, 'Seleccione carpeta')
        return dir

    def set_input_folder(self):
        dir = self.get_folder()
        self.ui.input_folder_text.setText(dir)
    
    def set_output_folder(self):
        dir = self.get_folder()
        self.ui.output_folder_text.setText(dir)
        

    def start_conversion(self, event):
        print('Iniciando conversion')
        pass
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())