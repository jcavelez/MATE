'''

@author: Juan Camilo Vélez
'''
#======================
# imports
#======================

from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
from glob import glob
from pathlib import Path
import os
from os import remove
import sys
import struct
import subprocess
import ffmpeg
import threading
from threading import Thread
import signal
import sqlite3
from sqlite3 import Error
import datetime
import time
import logging
import errno

def service_shutdown(signum, frame):
    '''
    Método para detener el Thread de crearConvertidor mediante el lanzamiento de una excepción
    '''
    raise ServiceExit

class CREED_GUI():
    """ Clase que crear la interface y la funcionalidad de la aplicación de decodificación"""
    def __init__(self):         # Método para inicializar GUI
        # se crea una instancia ventana root
        self.root = Tk()
        self.root.title("Massive Transcoder")
        self.database_name = 'MATE_DB_main.db'
        self.conectorBD = sqlite3.connect(self.database_name)
        self.cursorCREED = self.conectorBD.cursor()
        #Inicializando BD
        try:
            self.cursorCREED.execute('''CREATE TABLE Grabaciones (
                ruta text, 
                estado int)''')
            #self.cursorCREED.commit()
            self.cursorCREED.execute("""CREATE TABLE Estados (
                ID int,
                descripcion text
                )
                """)

            estados = [
                    (1,'No Procesado'),
                    (2,'En Proceso'),
                    (3,'Procesado')    
                    ]
            self.cursorCREED.executemany('INSERT INTO Estados VALUES (?,?)', estados)
            self.conectorBD.commit()
        except:
            pass

        
        self.crearWidgets()


    def clicLabelCarpetaEntrada(self,event):
        if self.carpetaEntradaCheckEstado.get() == False:
            self.carpetaEntradaCheck.select()
            self.activarProcesamientoPorCarpeta()
        elif self.carpetaEntradaCheckEstado.get() == True:
            self.carpetaEntradaCheck.deselect()
            self.activarProcesamientoPorCarpeta()

    def clicLabelArchivoEntrada(self,event):
        if self.archivoEntradaCheckEstado.get() == False:
            self.archivoEntradaCheck.select()
            self.activarProcesamientoPorArchivo()
        elif self.archivoEntradaCheckEstado.get() == True:
            self.archivoEntradaCheck.deselect()
            self.activarProcesamientoPorArchivo()

    def activarProcesamientoPorArchivo(self):
        self.iniciarBoton.config(state=NORMAL)
        if self.archivoEntradaCheckEstado.get() == True:
            self.activarComponentesArchivoEntrada()
            self.desactivarComponentesCarpetaEntrada()
            self.desactivarComponentesRecurrente()
            self.carpetaEntradaCheck.deselect()
        elif self.archivoEntradaCheckEstado.get() == False:
            self.desactivarComponentesArchivoEntrada()
            self.activarComponentesRecurrente()
            self.archivoEntradaCheck.deselect()
        #Verificar sí los dos Check están desactivados
        if self.carpetaEntradaCheckEstado.get() ==False and self.archivoEntradaCheckEstado.get() == False:
            self.iniciarBoton.config(state=DISABLED) 

    def activarProcesamientoPorCarpeta(self):
        self.iniciarBoton.config(state=NORMAL)
        if self.carpetaEntradaCheckEstado.get() == True:
            self.activarComponentesCarpetaEntrada()
            self.desactivarComponentesArchivoEntrada()
            self.activarComponentesRecurrente()
            self.archivoEntradaCheck.deselect()
        elif self.carpetaEntradaCheckEstado.get() == False:
            self.desactivarComponentesCarpetaEntrada()
            self.carpetaEntradaCheck.deselect()
        #Verificar sí los dos Check están desactivados
        if self.carpetaEntradaCheckEstado.get() ==False and self.archivoEntradaCheckEstado.get() == False:
            self.iniciarBoton.config(state=DISABLED) 

    def activarComponentesCarpetaEntrada(self):
        self.carpetaEntradaLabel.config(state=NORMAL)
        self.carpetaEntradaCampo.config(state=NORMAL)
        self.carpetaEntradaBoton.config(state=NORMAL)

    def desactivarComponentesCarpetaEntrada(self):
        self.carpetaEntradaLabel.config(state=DISABLED)
        self.carpetaEntradaCampo.config(state=DISABLED)
        self.carpetaEntradaBoton.config(state=DISABLED)

    def activarComponentesArchivoEntrada(self):
        self.archivoEntradaLabel.config(state=NORMAL)
        self.archivoEntradaCampo.config(state=NORMAL)
        self.archivoEntradaBoton.config(state=NORMAL)

    def desactivarComponentesArchivoEntrada(self):
        self.archivoEntradaLabel.config(state=DISABLED)
        self.archivoEntradaCampo.config(state=DISABLED)
        self.archivoEntradaBoton.config(state=DISABLED)

    def activarComponentesCarpetaSalida(self):
        self.carpetaSalidaLabel.config(state=NORMAL)
        self.carpetaSalidaCampo.config(state=NORMAL)
        self.carpetaSalidaBoton.config(state=NORMAL)

    def desactivarComponentesCarpetaSalida(self):
        self.carpetaSalidaLabel.config(state=DISABLED)
        self.carpetaSalidaCampo.config(state=DISABLED)
        self.carpetaSalidaBoton.config(state=DISABLED)

    def activarComponentesFormatoSalida(self):
        self.formatoSalidaLabel.config(state=NORMAL)
        self.formatoSalidaCombo.config(state="readonly")

    def desactivarComponentesFormatoSalida(self):
        self.formatoSalidaLabel.config(state=DISABLED)
        self.formatoSalidaCombo.config(state=DISABLED)

    def activarComponentesBorrar(self):
        self.borrarArchivosLabel.config(state=NORMAL)
        self.borrarArchivosRadioSi.config(state=NORMAL)
        self.borrarArchivosRadioNo.config(state=NORMAL)

    def desactivarComponentesBorrar(self):
        self.borrarArchivosLabel.config(state=DISABLED)
        self.borrarArchivosRadioSi.config(state=DISABLED)
        self.borrarArchivosRadioNo.config(state=DISABLED)

    def activarComponentesRecurrente(self):
        self.recurrenteLabel.config(state=NORMAL)
        self.recurrenteRadioSi.config(state=NORMAL)
        self.recurrenteRadioNo.config(state=NORMAL)

    def desactivarComponentesRecurrente(self):
        self.recurrenteLabel.config(state=DISABLED)
        self.recurrenteRadioSi.config(state=DISABLED)
        self.recurrenteRadioNo.config(state=DISABLED)

    def reactivarInterface(self):
        self.activarComponentesCarpetaSalida()
        self.activarComponentesFormatoSalida()
        self.activarComponentesBorrar()
        self.activarComponentesRecurrente()
        if self.archivoEntradaCheckEstado.get() == True:
            self.activarComponentesArchivoEntrada()
        elif self.carpetaEntradaCheckEstado.get() == True:
            self.activarComponentesCarpetaEntrada()
        self.iniciarBoton.config(state=NORMAL)
        self.carpetaEntradaCheck.config(state=NORMAL)
        self.archivoEntradaCheck.config(state=NORMAL)

    def desactivarInterface(self):
        self.desactivarComponentesCarpetaEntrada()
        self.desactivarComponentesArchivoEntrada()
        self.desactivarComponentesCarpetaSalida()
        self.desactivarComponentesFormatoSalida()
        self.desactivarComponentesBorrar()
        self.desactivarComponentesRecurrente()
        self.iniciarBoton.config(state=DISABLED)
        self.archivoEntradaCheck.config(state=DISABLED)
        self.carpetaEntradaCheck.config(state=DISABLED)

    def obtenerCarpetaEntrada(self):
        self.carpetaEntradaRuta.set(filedialog.askdirectory(initialdir ="C:\\"))
    

    def obtenerArchivoEntrada(self):
        self.archivoEntradaRuta.set(filedialog.askopenfilename(initialdir ="C:\\",
            filetypes = (("MNF files","*.mnf"),("todos los archivos","*.*"))))

    def obtenerCarpetaSalida(self):
        self.carpetaSalidaRuta.set(filedialog.askdirectory(initialdir ="C:\\"))

    def insertarGrabacion(self,rutaGrab):
        '''
        Metodo para insertar un registro en la tabla llamadas en Estado 1
        :param rutaGrab
        :return null
        '''
        conectorHilo = None

        try:
            conectorHilo = sqlite3.connect(self.database_name)
            cursorHilo = conectorHilo.cursor()
        except Error as e:
            print(e)

        sqlConsulta = "SELECT * FROM Grabaciones WHERE ruta=?"
        sqlInsert = ''' INSERT INTO Grabaciones
              VALUES(?,?) '''
        paramConsulta = (rutaGrab,)
        cursorHilo.execute(sqlConsulta,paramConsulta)
        ruta = cursorHilo.fetchone()

        if ruta == None:
            registroNuevo = (rutaGrab,1)
            cursorHilo.execute(sqlInsert,registroNuevo)
            conectorHilo.commit()

        conectorHilo.close()

    def obtenerNoProcesado(self):
        '''
        Metodo para devolver 1 registro en estado 1 (No Procesado)
        : return string
        '''
        conectorHilo = None
        ruta = ""

        try:
            conectorHilo = sqlite3.connect(self.database_name)
            cursorHilo = conectorHilo.cursor()
        except Error as e:
            print(e)

        sqlInsert = "SELECT ruta FROM Grabaciones WHERE estado=?"
        try:
            cursorHilo.execute(sqlInsert,'1')
            ruta = cursorHilo.fetchone()
            conectorHilo.close()
            return ruta[0]
        except:
            return ruta


    def actualizarEstadoGrabacion(self,ruta,estado):
        '''
        Metodo para actualizar el estado de una grabación
        :param ruta str
        : return null
        '''
        conectorHilo = None

        try:
            conectorHilo = sqlite3.connect(self.database_name)
            cursorHilo = conectorHilo.cursor()
        except Error as e:
            print(e)

        sqlUpdate = "UPDATE Grabaciones SET estado=? WHERE ruta=?"
        sqlParams = (estado,ruta)

        cursorHilo.execute(sqlUpdate,sqlParams)
        conectorHilo.commit()
        conectorHilo.close()

    def verificarCarpeta(self):
        '''
        Metodo para verificar sí hay nuevo contenido en la carpeta procesada. Sí encuentro un nuevo archivo, lo inserta en la BD en 
        Estado 1
        :return null
        '''

        conectorHilo = None

        logging.info("Buscando nuevo contenido en Carpeta Entrada: " + self.carpetaEntradaRuta.get())

        #Se obtienen todos los archivos y se guardan en un arrreglo.
        listaArchivos = Path(self.carpetaEntradaRuta.get()).rglob('*.mnf')

        #Se recorre todo el arreglo para guardar en base de datos todos los registros en Estado 1
        for arch in listaArchivos:
            self.insertarGrabacion(str(arch))

        try:
            conectorHilo = sqlite3.connect(self.database_name)
            cursorHilo = conectorHilo.cursor()
            sqlSelect = "SELECT ruta FROM Grabaciones WHERE estado=?"
            cursorHilo.execute(sqlSelect,'1')
            ruta = cursorHilo.fetchall()
            conectorHilo.close()
            logging.info("Se encontraron " + str(len(ruta)) + " nuevos archivos para procesar")
        except Error as e:
            print(e)


    def crearHilo(self):
        '''
        Metodo iniciar el Thread que llama al método crearConvertidor()
        :return null
        '''
        # Se registran señales para parar el Thread
        signal.signal(signal.SIGTERM, service_shutdown)
        signal.signal(signal.SIGINT, service_shutdown)
        self.shutdown_flag = threading.Event()
        #Se crea un Thread para manejar cada conversión con el método crearConvertidor
        self.run_thread = Thread(target=self.crearConvertidor)
        self.run_thread.setDaemon(True) 
        self.run_thread.start()

    def detect_subfolder(self, complete_path, root_folder):
        print('')
        complete_path = complete_path.split('\\')
        root_folder = root_folder.split('\\')
        print('')
        print('+++++++ Complete path ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print(complete_path)
        print('')
        print('+++++++ root ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print(root_folder)

        if len(complete_path) == len(root_folder):
            return None
        
        subfolder = complete_path[len(root_folder) : -1]
        print('+++++++ sub carpeta ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++%&$#$&#%$&$/&%$&/++++')
        print(subfolder)

        return '\\'.join(subfolder)
        

    def crearConvertidor(self):
        '''
        Metodo para crear instalacia de la clase Convertidor con parametros obtenidos de la interfaz gráfica
        :return null
        '''
        #Desactivar los widgets mientras esté convirtiendo
        self.desactivarInterface()
        #Sí el usuario escogió procesar un único archivo:
        output_path = self.carpetaSalidaRuta.get().replace('/', '\\')
        subfolder = None
        output_format = "." + self.formatoSalidaCombo.get().lower()
        if self.archivoEntradaCheckEstado.get() == True:
            path_to_file = self.archivoEntradaRuta.get().replace('/', '\\')
            conv=Convertidor(path_to_file, output_path, subfolder, output_format)
            conv.convert_to_()
            self.borrarProcesado(self.archivoEntradaRuta.get())
            logging.info("Finaliza conversión de "+ self.archivoEntradaRuta.get() + " a " 
                + self.formatoSalidaCombo.get().lower())

        #Aquí empiezan las funciones de convertir toda una carpeta. 
        elif self.carpetaEntradaCheckEstado.get() == True:
            self.verificarCarpeta()

            while not self.shutdown_flag.is_set():
                path_to_file = self.obtenerNoProcesado()
                subfolder = self.detect_subfolder(path_to_file, self.carpetaEntradaRuta.get()) 
                if path_to_file != None:
                    self.actualizarEstadoGrabacion(path_to_file, 2)
                    conv = Convertidor(path_to_file, output_path, subfolder, output_format)
                    conv.convert_to_()
                    self.actualizarEstadoGrabacion(path_to_file,3)
                    self.borrarProcesado(path_to_file)
                    logging.info("Finaliza conversión de "+ path_to_file + " a " 
                        + self.formatoSalidaCombo.get().lower())
                else:
                    logging.info("No hay archivos pendientes por procesar")
                    if self.recurrenteEstado.get() == False:
                        self.shutdown_flag.set()
                        break
                    time.sleep(10)
                    ######## OJOOOOOOOO VERIFICA TOOOOODA LA CARPETA OTRA VEZ###############################
                    self.verificarCarpeta()

                pass

        # Activar de nuevo toda la interface
        self.reactivarInterface()
    

    def iniciarConversion(self):
        self.crearHilo()

    def detener(self):
        self.shutdown_flag.set()
        logging.info("Deteniendo Servicio. Finalizando proceso pendiente.")
        self.reactivarInterface()
        

    #Verificar sí se terminó usando en el método inicar conversión opcion carpeta entrada
    def listarArchivosMNF(self,ruta):
        archivos=ruta + '/*.mnf'
        return glob(archivos)

    def borrarProcesado(self, archivo):
        if self.borrarArchivosEstado.get() == True:
            remove(archivo)
            logging.info("Borrando archivo procesado: "+ archivo)   


    def crearWidgets(self):
        ############################## Menús parte superior----------------------------------------------
        barraMenu=Menu(self.root)
        self.root.config(menu=barraMenu,width=300,height=300)
        archivoMenu=Menu(barraMenu,tearoff=0)
        archivoMenu.add_command(label="Salir")

        edicionMenu=Menu(barraMenu,tearoff=0)
        edicionMenu.add_command(label="Preferencias")

        ayudaMenu=Menu(barraMenu,tearoff=0)
        ayudaMenu.add_command(label="Acerda de...")

        barraMenu.add_cascade(label="Archivo", menu=archivoMenu)
        barraMenu.add_cascade(label="Edicion", menu=edicionMenu)
        barraMenu.add_cascade(label="Ayuda", menu=ayudaMenu)


        #Frame de la parte superior
        rutasFrame=Frame(self.root)
        rutasFrame.pack(side=TOP)

        #Variables string para almacenar ruta de archivo a convertir
        self.archivoEntradaRuta=StringVar()
        self.archivoEntradaCheckEstado=BooleanVar()

        #Botón de chequeo, etiqueta, campo de entrada y botón para seleccionar archivo de entrada
        self.archivoEntradaCheck=Checkbutton(rutasFrame, 
            variable=self.archivoEntradaCheckEstado, command=self.activarProcesamientoPorArchivo)
        self.archivoEntradaCheck.grid(row=0, column=0, sticky=W, padx=0,pady=0)
        self.archivoEntradaCheck.select()
        self.archivoEntradaLabel=Label(rutasFrame, text="Archivo de Entrada:")
        self.archivoEntradaLabel.bind("<Button-1>", self.clicLabelArchivoEntrada)
        self.archivoEntradaLabel.grid(row=0, column=1,sticky=W,padx=0,pady=1)
        self.archivoEntradaCampo=Entry(rutasFrame, width=40, textvariable=self.archivoEntradaRuta)
        self.archivoEntradaCampo.grid(row=0, column=2,sticky=W)
        self.archivoEntradaBoton=Button(rutasFrame, text="...", command=self.obtenerArchivoEntrada)
        self.archivoEntradaBoton.grid(row=0, column=3, sticky=W,pady=0)


        #Variable string para almacenar ruta de carpeta de entrada
        self.carpetaEntradaRuta=StringVar()
        self.carpetaEntradaCheckEstado=BooleanVar()
        #Botón de chequeo, etiqueta, campo de entrada y botón para seleccionar archivo de entrada
        self.carpetaEntradaCheck=Checkbutton(rutasFrame, 
            variable=self.carpetaEntradaCheckEstado, command=self.activarProcesamientoPorCarpeta)
        self.carpetaEntradaCheck.grid(row=1, column=0, sticky=W)
        self.carpetaEntradaLabel=Label(rutasFrame, text="Carpeta de Entrada:", state=DISABLED)
        self.carpetaEntradaLabel.bind("<Button-1>", self.clicLabelCarpetaEntrada) 
        self.carpetaEntradaLabel.grid(row=1, column=1, sticky=W,padx=0,pady=1)

        self.carpetaEntradaCampo=Entry(rutasFrame, width=40, textvariable=self.carpetaEntradaRuta, state=DISABLED)
        self.carpetaEntradaCampo.grid(row=1, column=2,sticky=W)
        self.carpetaEntradaBoton=Button(rutasFrame, text="...", command=self.obtenerCarpetaEntrada, state=DISABLED)
        self.carpetaEntradaBoton.grid(row=1, column=3, sticky=W,pady=0)


        self.carpetaEntradaRuta.set("D:\\AudiosNice") ###################BORRAR


        #Variable string para almacenar ruta de carpeta de salida
        self.carpetaSalidaRuta = StringVar()
        self.carpetaSalidaRuta.set("C:\\Users\\jcave\\OneDrive\\Escritorio\\Salida")
        #Etiquetatiqueta, campo de entrada y botón para seleccionar archivo de entrada
        self.carpetaSalidaLabel=Label(rutasFrame, text="Carpeta de Salida:")
        self.carpetaSalidaLabel.grid(row=2, column=1,sticky=W,padx=0,pady=1)
        self.carpetaSalidaCampo=Entry(rutasFrame, width=40, textvariable=self.carpetaSalidaRuta)
        self.carpetaSalidaCampo.grid(row=2, column=2,sticky=W)
        self.carpetaSalidaBoton=Button(rutasFrame, text="...", command=self.obtenerCarpetaSalida)
        self.carpetaSalidaBoton.grid(row=2, column=3, sticky=W,pady=0)


        #Etiqueta y combobox de ttk para mostrar formatos de salida posibles
        self.formatoSalidaLabel=Label(rutasFrame, text="Formato de Salida:")
        self.formatoSalidaLabel.grid(row=4, column=1,sticky=W)
        self.formatoSalidaCombo=ttk.Combobox(rutasFrame, width=6, values=["MP3","OPUS","WAV","AAC","M4A"], state="readonly")
        self.formatoSalidaCombo.grid(row=4, column=2,padx=0,pady=1, sticky=W)
        self.formatoSalidaCombo.current(0)

        #Variable booleano para almacenar sí se desea borrar archivos procesados
        self.borrarArchivosEstado=BooleanVar()
        self.borrarArchivosEstado.set(False)
        #Etiqueta y radio button para escoger sí desea borrar los archivos procesados (convertidos)
        self.borrarArchivosLabel=Label(rutasFrame, text="¿Borrar archivos procesados?")
        self.borrarArchivosLabel.grid(row=5, column=1,padx=0,pady=1, sticky=W)
        self.borrarArchivosRadioSi=Radiobutton(rutasFrame, text="Si", variable=self.borrarArchivosEstado, value=True)
        self.borrarArchivosRadioSi.grid(row=5, column=2, sticky=W)
        self.borrarArchivosRadioNo=Radiobutton(rutasFrame, text="No", variable=self.borrarArchivosEstado, value=False)
        self.borrarArchivosRadioNo.grid(row=6, column=2, sticky=W)

        #Variable booleano para almacenar sí se desea procesar la carpeta recurrentemente
        self.recurrenteEstado=BooleanVar()
        self.recurrenteEstado.set(False)
        #Etiqueta y radio button para escoger sí desea procesar la carpeta recurrentemente
        self.recurrenteLabel=Label(rutasFrame, text="¿Procesamiento recurrente?")
        self.recurrenteLabel.grid(row=8, column=1, sticky=W)
        self.recurrenteRadioSi=Radiobutton(rutasFrame, text="Si", variable=self.recurrenteEstado, value=True)
        self.recurrenteRadioSi.grid(row=8, column=2, sticky=W)
        self.recurrenteRadioNo=Radiobutton(rutasFrame, text="No", variable=self.recurrenteEstado, value=False)
        self.recurrenteRadioNo.grid(row=9, column=2, sticky=W)

        #Crear un frame abajo del frame superir para empaquetar los botones y tablero de estado
        botonesFrame=Frame(self.root)
        botonesFrame.pack(side=BOTTOM)
        #Botón iniciar conversión
        self.iniciarBoton=Button(botonesFrame, text="Iniciar", width=18, command=self.iniciarConversion)
        self.iniciarBoton.grid(sticky=E, row=0, column=0, padx=5, pady=5)
        #Botón Detener
        self.detenerBoton=Button(botonesFrame, text="Detener", width=18, command=self.detener)
        self.detenerBoton.grid(sticky=W, row=0, column=1, padx=5, pady=5)
        #Texto donde se muestra el estado del servicio
        self.estadoLabel=Label(botonesFrame, text="Estado del Servicio")
        self.estadoLabel.grid(row=4, column=0, columnspan=2, padx=0, pady=2)
        self.estadoText=Text(botonesFrame, height=12, width =80, 
            background='#ededed', font='Verdada 7')
        self.estadoText.grid(row=5, column=0, columnspan=2, padx=0, pady=10)

        # Create textLogger
        self.text_handler = WidgetLogger(self.estadoText)

        # Logging configuration
        logging.basicConfig(filename='MATE.log',
            level=logging.INFO, 
            format='%(asctime)s - %(levelname)s - %(message)s')       

        # Add the handler to logger
        self.logger = logging.getLogger()        
        self.logger.addHandler(self.text_handler)

        ##################### Fin Crear Widgets clase CREED_GUI #######################################################

    

class Convertidor:
    """ Clase Convertidor que es inicializada con la ruta a un archivo .mnf y el formato del archivo de salida.
    El métido a invocar es convert_to_"""
    codecs = {
                0: "g729",
                1: "adpcm_g726",
                2: "adpcm_g726",
                3: "alaw",
                7: "pcm_mulaw",
                8: "g729",
                9: "g723_1",
                10: "g723_1",
                19: "adpcm_g722"
            }

    def __init__(self, path_to_file, output_path, subfolders, output_format):
        self.path_to_file = path_to_file
        self.output_path = output_path
        self.subfolders = subfolders
        self.output_format = output_format

    
    #Métodos de conversión de audio       
    def get_packet_header(self,data):
        "Get required information from packet header."
        return {
            "packet_type": struct.unpack("b", data[0:1])[0],
            "packet_subtype": struct.unpack("h", data[1:3])[0],
            "stream_id": struct.unpack("b", data[3:4])[0],
            "start_time": struct.unpack("d", data[4:12])[0],
            "end_time": struct.unpack("d", data[12:20])[0],
            "packet_size": struct.unpack("I", data[20:24])[0],
            "parameters_size": struct.unpack("I", data[24:28])[0]
        }


    def get_compression_type(self,data):
        "Get compression type of the audio chunk."
        for i in range(0, len(data), 22):
            type_id = struct.unpack("h", data[i:i + 2])[0]
            data_size = struct.unpack("i", data[i + 2:i + 6])[0]
            data = struct.unpack("16s", data[i + 6:i + 22])[0]
            if type_id == 10:
                return Convertidor.get_data_value(data, data_size)


    def get_data_value(data, data_size):
        '''The helper function to get value of the data
        field from parameters header.'''
        fmt = "{}s".format(data_size)
        data_value = struct.unpack(fmt, data[0:data_size])
        if data_value == 0:
            data_value = struct.unpack(fmt, data[8:data_size])
        data_value = struct.unpack("b", data_value[0])
        return data_value[0]


    def chunks_generator(self):
        "A python generator of the raw audio data."
        try:
            with open(self.path_to_file, "rb") as f:
                data = f.read()
        except IOError:
            sys.exit("No such file")
        packet_header_start = 0
        while True:
            packet_header_end = packet_header_start + 28
            headers = self.get_packet_header(data[packet_header_start:packet_header_end])
            if headers["packet_type"] == 4 and headers["packet_subtype"] == 0:
                chunk_start = packet_header_end + headers["parameters_size"]
                chunk_end = (chunk_start + headers["packet_size"] - headers["parameters_size"])
                chunk_length = chunk_end - chunk_start
                fmt = "{}s".format(chunk_length)
                raw_audio_chunk = struct.unpack(fmt, data[chunk_start:chunk_end])
                yield (self.get_compression_type(data[packet_header_end:packet_header_end +
                       headers["parameters_size"]]),
                       headers["stream_id"],
                       raw_audio_chunk[0])
            packet_header_start += headers["packet_size"] + 28
            if headers["packet_type"] == 7:
                break

    def convert_to_(self):
        #"Convert raw audio data using ffmpeg and subprocess."
        file_name = os.path.splitext(self.path_to_file)[0]
        
        file_name = file_name.split('\\')
        print('*****FILE NAME ***********************************************************************************  :  ')
        print(file_name)
        file_name = file_name[-1]
        previous_stream_id = -1
        processes = {}
        streamsList = []
        for compression, stream_id, raw_audio_chunk in self.chunks_generator():
            if stream_id != previous_stream_id and not processes.get(stream_id):
                self.output_file = file_name + "_stream{}".format(stream_id) + self.output_format
                cmd_args = []
                cmd_args.append("ffmpeg")   #Llamada a ejecutable ffmpeg que debe estar en System32 
                cmd_args.append("-hide_banner") #Oculta consola
                cmd_args.append("-y")   #Sobreescribir si el archivo ya existe
                cmd_args.append("-f")
                cmd_args.append(self.codecs[compression])
                cmd_args.append("-i")
                cmd_args.append("pipe:0")   #nombre archivo de entrada
                cmd_args.append(self.output_file)    #Ej: ffmpeg -hide_banner -y -f codec -i archivo.nmf archivo_Stream.wav
                print(cmd_args)
                processes[stream_id] = subprocess.Popen(cmd_args,stdin=subprocess.PIPE)
                previous_stream_id = stream_id

            processes[stream_id].stdin.write(raw_audio_chunk)

            # Se agrega en stream a una lista para luego concatenarlos
            if (self.output_file in streamsList) == False:
                streamsList.append(self.output_file)

        for key in processes.keys():
            processes[key].stdin.close()
            processes[key].wait()

        #Iniciando concatenación. Ej: ffmpeg.input('concat:arch1mnf|arch2.mnf|arch3.mnf').output('arch.wav', c='copy').run()
        complete_output_path = self.output_path
        if self.subfolders is not None:
            complete_output_path = os.path.join(self.output_path, self.subfolders)
            try:
                if self.subfolders is not None:
                    os.makedirs(complete_output_path)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

        outputFFmpeg = complete_output_path + '\\' + file_name + self.output_format
        streamsList.sort()
        streamsList.reverse()
        inputFfmpeg = "concat:"
        for s in streamsList:
            inputFfmpeg=inputFfmpeg+s+"|"       
        
        completeStream = ffmpeg.input(inputFfmpeg)
        completeStream = ffmpeg.output(completeStream, outputFFmpeg, c='copy')
        ffmpeg.run(completeStream, overwrite_output=True)
  
        for l in streamsList:
            remove(l)

    ### Fin clase Convertidor    



class ServiceExit(Exception):
    """
    Clase Excepción para para el servicio con el botón Detener
    """
    pass

class WidgetLogger(logging.Handler):
    def __init__(self, widget):
        logging.Handler.__init__(self)
        self.setLevel(logging.INFO)
        self.widget = widget
        self.widget.config(state='disabled')

    def emit(self, record):
        self.widget.config(state='normal')
        # Append message (record) to the widget
        if int(self.widget.index('end-1c').split('.')[0]) >=12:
            self.widget.delete("1.0", "2.0")
            pass
        self.widget.insert(END, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " - " + self.format(record) + '\n')
        self.widget.see(END)  # Scroll to the bottom
        self.widget.config(state='disabled')

#======================
# Inicia GUI
#======================

ventana = CREED_GUI()
ventana.root.mainloop()



