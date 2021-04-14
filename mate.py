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
import logging
from pathlib import Path
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
    
    def check_folder(self):
        '''
        Metodo para verificar sí hay nuevo contenido en la carpeta procesada. Sí encuentro un nuevo archivo, lo inserta en la BD en 
        Estado 1
        :return null
        '''

        conector = None

        logging.info("Buscando nuevo contenido en Carpeta Entrada: " + self.ui.input_folder_text.text)

        #Se obtienen todos los archivos y se guardan en un arrreglo.
        files_list = Path(self.ui.input_folder_text.text).rglob('*.mnf')

        #Se recorre todo el arreglo para guardar en base de datos todos los registros en Estado 1
        for file in files_list:
            self.insert_new_file(str(file))

        try:
            conector = sqlite3.connect(self.database_name)
            cursor = conector.cursor()
            sql_select = "SELECT ruta FROM Grabaciones WHERE estado=?"
            cursor.execute(sql_select,'1')
            path = cursor.fetchall()
            conector.close()
            logging.info("Se encontraron " + str(len(path)) + " nuevos archivos para procesar")
        except sqlite3.Error as e:
            print(e)
        
    def insert_new_file(self, file):
        '''
        Metodo para insertar un registro en la tabla llamadas en Estado 1
        :param rutaGrab
        :return null
        '''
        conector = None

        try:
            conector = sqlite3.connect(self.database_name)
            cursor = conector.cursor()
        except sqlite3.Error as e:
            print(e)

        sql_consulta = "SELECT * FROM Grabaciones WHERE ruta=?"
        sql_insert = ''' INSERT INTO Grabaciones
              VALUES(?,?) '''
        params = (file,)
        cursor.execute(sql_consulta,params)
        ruta = cursor.fetchone()

        if ruta == None:
            new_registry = (file,1)
            cursor.execute(sql_insert,new_registry)
            conector.commit()

        conector.close()


    def create_converter(self):
        '''
        Metodo para crear instalacia de la clase Decoder con parametros obtenidos de la interfaz gráfica
        :return null
        '''
        #Desactivar los widgets mientras esté convirtiendo
        self.disable_widgets()
        self.ui.start_button.setIcon(QIcon('stop.svg'))

        self.check_folder()

        # Activar de nuevo toda la interface
        self.enable_widgets()
        self.ui.start_button.setIcon(QIcon('convert.svg'))

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