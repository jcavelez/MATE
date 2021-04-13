
import errno
import ffmpeg
import os
import struct
import subprocess
import sys

class Decoder:
    """ Clase Decoder que es inicializada con la ruta a un archivo .mnf y el formato del archivo de salida.
    El métido a invocar es convert_to"""
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
                return Decoder.get_data_value(data, data_size)


    def get_data_value(self, data, data_size):
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

    def convert_to(self):
        #"Convert raw audio data using ffmpeg and subprocess."
        file_name = os.path.splitext(self.path_to_file)[0]
        
        file_name = file_name.split('\\')
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

        output_ffmpeg = complete_output_path + '\\' + file_name + self.output_format
        streamsList.sort()
        streamsList.reverse()
        input_ffmpeg = "concat:"
        for s in streamsList:
            input_ffmpeg=input_ffmpeg+s+"|"       
        
        complete_stream = ffmpeg.input(input_ffmpeg)
        complete_stream = ffmpeg.output(complete_stream, output_ffmpeg, c='copy')
        ffmpeg.run(complete_stream, overwrite_output=True)
  
        for l in streamsList:
            os.remove(l)

    ### Fin clase Convertidor    
