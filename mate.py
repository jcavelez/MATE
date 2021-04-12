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

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

if __name__ == '__main__':
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())