#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Juan Camilo Vélez
'''
#======================
# imports
#======================
import sys
from PyQt5 import uic, QtWidgets

qtCreatorFile = 'main.ui'   #Archivo creado mediante Designer de PyQt5
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile) #El modulo ui carga el archivo
app = QtWidgets.QApplication(sys.argv)

def service_shutdown(signum, frame):
    '''
    Método para detener el Thread de crearConvertidor mediante el lanzamiento de una excepción
    '''
    raise ServiceExit

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

if __name__ == '__main__':
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())