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
from PyQt5.QtCore import QThread, pyqtSignal
import datetime
from Decoder import *
import logging
from pathlib import Path
import signal
import sqlite3
import sys
import threading
import time


TIME_LIMIT = 100

LOG_FILENAME = datetime.datetime.now().strftime('logfile_%Y_%m_%d.log')

logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO, format='%(asctime)s - %(message)s')


class External(QThread):
    count_changed = pyqtSignal(int)

    def run(self):
        count = 0
        while count < TIME_LIMIT:
            count +=1
            time.sleep(1)
            self.count_changed.emit(count)


class ServiceExit(Exception):
    """
    Clase Excepción para para el servicio con el botón Detener
    """
    pass




class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.database_name = 'MATE_DB.db'

        try:
            os.remove(self.database_name)
        except:
            pass

        self.ui.input_folder_text.setText('C:/Users/jcave/OneDrive/Escritorio/AudiosNice_') #<---- Borrar
        self.ui.output_folder_text.setText('C:/Users/jcave/OneDrive/Escritorio/Salida')

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
        except sqlite3.Error:
            pass

        self.ui.more_options_label.clicked.connect(self.show_more_options)
        self.ui.more_options_button.clicked.connect(self.show_more_options)

        self.hide_more_options()

        self.ui.start_button.clicked.connect(self.start_conversion)
        self.ui.input_folder_button.clicked.connect(self.set_input_folder)
        self.ui.output_folder_button.clicked.connect(self.set_output_folder)

    def get_folder(self):
        file_dialog = QFileDialog()
        folder = file_dialog.getExistingDirectory(self, 'Seleccione carpeta', 'C:/Users/jcave/OneDrive/Escritorio/')

        return folder

    def set_input_folder(self):
        folder = self.get_folder()
        self.ui.input_folder_text.setText(folder)
    
    def set_output_folder(self):
        folder = self.get_folder()
        self.ui.output_folder_text.setText(folder)
    
    def enable_widgets(self):
        self.ui.input_folder_label.setEnabled(True)
        self.ui.input_folder_text.setEnabled(True)
        self.ui.input_folder_button.setEnabled(True)
        self.ui.output_folder_label.setEnabled(True)
        self.ui.output_folder_text.setEnabled(True)
        self.ui.output_folder_button.setEnabled(True)
        self.ui.more_options_label.setEnabled(True)
        self.ui.more_options_button.setEnabled(True)
        self.ui.delete_processed_label.setEnabled(True)
        self.ui.delete_processed_text.setEnabled(True)
        self.ui.recurrence_label.setEnabled(True)
        self.ui.recurrence_text.setEnabled(True)
        self.ui.input_format_label.setEnabled(True)
        self.ui.input_format_text.setEnabled(True)
        self.ui.output_format_label.setEnabled(True)
        self.ui.output_format_text.setEnabled(True)
    
    def disable_widgets(self):
        self.ui.input_folder_label.setEnabled(False)
        self.ui.input_folder_text.setEnabled(False)
        self.ui.input_folder_button.setEnabled(False)
        self.ui.output_folder_label.setEnabled(False)
        self.ui.output_folder_text.setEnabled(False)
        self.ui.output_folder_button.setEnabled(False)
        self.ui.more_options_label.setEnabled(False)
        self.ui.more_options_button.setEnabled(False)
        self.ui.delete_processed_label.setEnabled(False)
        self.ui.delete_processed_text.setEnabled(False)
        self.ui.recurrence_label.setEnabled(False)
        self.ui.recurrence_text.setEnabled(False)
        self.ui.input_format_label.setEnabled(False)
        self.ui.input_format_text.setEnabled(False)
        self.ui.output_format_label.setEnabled(False)
        self.ui.output_format_text.setEnabled(False)        
    
    def show_more_options(self):
        self.move_widgets_down()
        self.ui.more_options_frame.show()
        self.ui.more_options_label.clicked.connect(self.hide_more_options)
        self.ui.more_options_button.clicked.connect(self.hide_more_options)
        self.ui.more_options_button.setIcon(QIcon('up-arrow.svg'))

    def hide_more_options(self):
        self.move_widgets_up()
        self.ui.more_options_frame.hide()
        self.ui.more_options_label.clicked.connect(self.show_more_options)
        self.ui.more_options_button.clicked.connect(self.show_more_options)
        self.ui.more_options_button.setIcon(QIcon('downarrow.svg'))

    def move_widgets_down(self):
        self.ui.down_frame.setGeometry(10, 310, 521, 151)
    
    def move_widgets_up(self):
        self.ui.down_frame.setGeometry(10, 270, 521, 151)
      
    def check_folder(self, format):
        '''
        Metodo para verificar sí hay nuevo contenido en la carpeta procesada. Sí encuentro un nuevo archivo, lo inserta en la BD en 
        Estado 1
        :return null
        '''

        conector = None

        logging.info("Buscando nuevo contenido en Carpeta Entrada: " + self.ui.input_folder_text.text())

        #Se obtienen todos los archivos y se guardan en un arrreglo.
        files_list = Path(self.ui.input_folder_text.text()).rglob(f'*.{format}')

        #Se recorre todo el arreglo para guardar en base de datos todos los registros en Estado 1
        for file in files_list:
            self.insert_new_file(str(file).replace('\\', '/'))

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

    def get_not_processed(self):
        '''
        Metodo para devolver 1 registro en estado 1 (No Procesado)
        : return string
        '''
        conector = None
        path = ""

        try:
            conector = sqlite3.connect(self.database_name)
            cursor = conector.cursor()
        except sqlite3.Error as e:
            print(e)

        sql_insert = "SELECT ruta FROM Grabaciones WHERE estado=?"
        try:
            cursor.execute(sql_insert,'1')
            path = cursor.fetchone()
            conector.close()
            return path[0]
        except:
            return path

    def update_status(self, ruta, estado):
        '''
        Metodo para actualizar el estado de una grabación
        :param ruta str
        : return null
        '''
        conector = None

        try:
            conector = sqlite3.connect(self.database_name)
            cursor = conector.cursor()
        except sqlite3.Error as e:
            print(e)

        sql_update = "UPDATE Grabaciones SET estado=? WHERE ruta=?"
        sql_params = (estado,ruta)

        cursor.execute(sql_update,sql_params)
        conector.commit()
        conector.close()

    def detect_subfolder(self, complete_path, root_folder):
        complete_path = complete_path.split('/')
        root_folder = root_folder.split('/')

        if len(complete_path) == len(root_folder):
            return None
        
        subfolder = complete_path[len(root_folder) : -1]
        
        return '\\'.join(subfolder)

    def delete_processed(self, file):
        if self.ui.delete_processed_text.currentIndex() == 'No':
            os.remove(file)
            logging.info("Archivo borrado: "+ file)   

    def create_converter(self):
        '''
        Metodo para crear instalacia de la clase Decoder con parametros obtenidos de la interfaz gráfica
        :return null
        '''
        #Desactivar los widgets mientras esté convirtiendo
        self.disable_widgets()
        self.ui.start_button.setIcon(QIcon('stop.svg'))

        input_format = self.ui.input_format_text.currentItem().text().lower()
        self.check_folder(input_format)
        output_path = self.ui.output_folder_text.text()
        subfolder = None
        output_format = "." + self.ui.output_format_text.currentItem().text().lower()

        while not self.shutdown_flag.is_set():
            path_to_file = self.get_not_processed()
            if path_to_file != None:
                subfolder = self.detect_subfolder(path_to_file, self.ui.output_folder_text.text())
                self.ui.message_label.setText(str(path_to_file))
                self.update_status(path_to_file, 2)
                deco = Decoder(path_to_file, input_format, output_path, subfolder, output_format)
                deco.convert_to()
                self.update_status(path_to_file,3)
                self.delete_processed(path_to_file)
                logging.info("Finaliza conversión de "+ path_to_file + " a " 
                    + output_format)
            else:
                logging.info(f'No hay archivos {self.ui.input_format_text.currentItem().text()} pendientes por procesar en {self.ui.input_folder_text.text()}')
                self.ui.message_label.setText(f'No hay archivos {self.ui.input_format_text.currentItem().text()} pendientes por procesar')
                if self.ui.recurrence_text.currentText() == 'No':
                    self.shutdown_flag.set()
                    break
                time.sleep(10)
                ######## OJOOOOOOOO VERIFICA TOOOOODA LA CARPETA OTRA VEZ###############################
                self.check_folder(input_format)

        # Activar de nuevo toda la interface
        self.enable_widgets()
        self.ui.start_button.setIcon(QIcon('convert.svg'))
    
    def service_shutdown(self, signum, frame):
        '''
        Método para detener el Thread de crearConvertidor mediante el lanzamiento de una excepción
        '''
        raise ServiceExit

    def start_conversion(self, event):
        '''
        Metodo iniciar el Thread que llama al método create_Converter()
        :return null
        '''
        # Se registran señales para parar el Thread
        signal.signal(signal.SIGTERM, self.service_shutdown)
        signal.signal(signal.SIGINT, self.service_shutdown)
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