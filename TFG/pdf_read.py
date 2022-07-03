import re
import tabula
import pandas as pd
import fitz
import time
import math

reg_val = re.compile(r'^Resultados validados por')
reg_cel = re.compile(r'.*Cels.*')

prohibidos = ["en blanco", "blanco", "b", ".", ".."]

# Tipo 1
def read_type1(doc):
    start_time = time.time()
    text = ""
    type_info = []
    data_info = []
    type_aux = []
    data_aux = []
    first = True
    firstR = True
    for p in range(doc.page_count):
        text += doc.get_page_text(p)
    idx = -1
    for line in text.split('\n'):
        if "Fecha de la toma:" in line:
            if not first:
                type_info.append(type_aux)
                data_info.append(data_aux)
            idx += 1
            type_aux = []
            data_aux = []
            first = False
            firstR = True
        if ":_" in line:
            if line.split(":")[0] != "Fecha":
                c1 = line.split(":")[0]
                c1 = format_col_name(c1)
                c2 = line.split("_")[1]
                if c1 == "Reticulocitos" and firstR:
                    c1 += "_porc"
                    firstR = False
                if c1 in type_aux:
                    if c2.rstrip(".") != data_aux[type_aux.index(c1)].rstrip("."):
                        #print("Repetido " + c1)
                        c1 += "_"
                        type_aux.append(c1)
                        data_aux.append(c2)
                else:
                    type_aux.append(c1)
                    data_aux.append(c2)
        elif len(data_aux) > 0:
            if "Fecha de la toma" not in line:
                data_aux[-1] = data_aux[-1] + " " + line
    type_info.append(type_aux)
    data_info.append(data_aux)
    #print("\n".join("{} \t|||\t {}".format(x,y) for x, y in zip(type_info[0], data_info[0])))
    #print("--- {:.2f} ---".format(time.time() - start_time))
    loading_time = time.time() - start_time
    if len(type_info) < 2:
        return type_info[0], data_info[0], loading_time
    else:
        return type_info, data_info, loading_time


# Lectura de páginas
# Primera página leo por secciones
def read_type2(file):
    start_time = time.time()
    dfs = []
    type = []
    data = []
    doc = fitz.open(file)
    corte = 780
    if doc.page_count == 1:
        if len(doc[0].search_for("INFORME DEL SERVICIO DE MICROBIOLOGIA")) != 1:
            servicios = doc[0].search_for("Servicio")
            for servicio in servicios:
                if math.trunc(servicio.x0) == 59:
                    corte = math.trunc(servicio.y0)
                    break
            
    secciones = doc[0].search_for("Resultados validados por")
    for idx, seccion in enumerate(secciones):
        extra = 0
        if idx == 0 and len(doc[0].search_for("Hemograma")) == 1:
            extra += 35
        if idx + 1 == len(secciones):
            lista = tabula.read_pdf(file, pages = 1, silent = True, area = [seccion.y1 + extra, 0, corte, 595])
        else:
            lista = tabula.read_pdf(file, pages = 1, silent = True, area = [seccion.y1 + extra, 0, secciones[idx+1].y0, 595])

        if len(lista) > 0:
            if len(lista[0].columns) > 1:
                dfs.append(lista[0])

    # Resto de páginas
    for p in range(1, doc.page_count, 1):
        # Última página (tipo 2, no comienzan con sección)
        # Cortamos donde esté el primer "Servicio" de abajo
        if p+1 == doc.page_count:
            if len(doc[p].search_for("Resultados validados por")) == 0:
                servicios = doc[p].search_for("Servicio")
                for servicio in servicios:
                    if math.trunc(servicio.x0) == 59:
                        corte = math.trunc(servicio.y0)
                        break
                lista = tabula.read_pdf(file, pages = p+1, silent = True, area = [105, 0, corte, 595])
            else:
                lista = tabula.read_pdf(file, pages = p+1, silent = True, area = [110, 0, 780, 595])
        # Página intermedia
        # Dividimos por Secciones (inicio sin sección)
        else:
            secciones = doc[p].search_for("Resultados validados por")
            if len(secciones) > 0:
                lista = tabula.read_pdf(file, pages = p+1, silent = True, area = [110, 0, secciones[0].y0-30, 595])
                dfs.append(lista[0])
                for idx in range(0, len(secciones), 1):
                    if idx + 1 == len(secciones):
                        corte = doc[p].search_for("__")
                        corte = math.trunc(corte[0].y0)
                        lista = tabula.read_pdf(file, pages = p+1, silent = True, area = [secciones[idx].y1, 0, corte, 595])
                    else:
                        lista = tabula.read_pdf(file, pages = p+1, silent = True, area = [secciones[idx].y1, 0, secciones[idx+1].y0, 595])
                    dfs.append(lista[0])
                continue
            else:
                lista = tabula.read_pdf(file, pages = p+1, silent = True, area = [110, 0, 780, 595])
        dfs.append(lista[0])

    # Cogemos las columnas type, data
    for i in range(len(dfs)):
        if len(dfs[i].columns) > 2:
            if find_data_column_1(dfs[i]):
                dfs[i] = dfs[i].iloc[:, [0, 1]]
            else:
                dfs[i] = dfs[i].iloc[:, [0, 2]]
        else:
            dfs[i] = dfs[i].iloc[:, [0, 1]]

    # Extraemos datos
    for df in dfs:
        good = False
        for row in df.iterrows():
            array = row[1].array
            c1 = str(array[0]).replace(" *", '').replace("* ", ''). replace("*", '')
            c2 = str(array[1])
            if c2.endswith('%'):
                c2 = c2[:-2]
            if c2.endswith('Millon/ml'):
                c2 = c2[:-10]
            # a) b) c)
            if not reg_val.match(c1) and c1[0:3] != "___" and c1 not in prohibidos:
                # d)
                if c2 != "nan":
                    # e)
                    if c1 != "nan":
                        good = True
                        c1 = format_col_name(c1)
                        type.append(c1)
                        data.append(c2)
                    elif c2 not in prohibidos and good and not reg_cel.match(c2):
                        # Si no es igual al de arriba *1000
                        if any(char.isdigit() for char in c2):
                            c2a = math.trunc(float(c2))
                            c2b = math.trunc(float(data[-1])*1000)
                            if  c2a != c2b:
                                if len(str(c2a)) > 1 and str(c2a)[:-1] != str(c2b)[:-1]:
                                    data[-1] = data[-1] + " " + c2
                        else:
                            data[-1] = data[-1] + " " + c2
                elif good:
                    type[-1] = type[-1] + " " + c1
                    type[-1] = format_col_name(type[-1])
            else:
                good = False
    doc.close()
    #print("\n".join("{} \t|||\t {}".format(x,y) for x, y in zip(type, data)))
    #print("--- {:.2f} ---".format(time.time() - start_time))
    loading_time = time.time() - start_time
    return type, data, loading_time


def read_type3(file):
    start_time = time.time()
    doc = fitz.open(file)
    type = []
    data = []
    start = 0
    if doc.page_count == 1:
        if len(doc[0].search_for("INFORME DEL SERVICIO DE MICROBIOLOGIA")) == 1:
            text = doc.get_page_text(0)
            text = text.split('\n')
            for idx in range(len(text)):
                #print(text[idx])
                if text[idx] == "TRG" or text[idx] == "Preliminar":
                    start = idx+1
                if text[idx] == "Validado por:":
                    end = idx
            resultado = text[start]
            if end-start > 1:
                for idx in range(start+1, end, 1):
                    resultado += " " + text[idx]
    #print("--- {:.2f} ---".format(time.time() - start_time))
    loading_time = time.time() - start_time
    type.append("Hemocultivo")
    data.append(resultado)
    return type, data, loading_time


def find_data_column_1(df):
    for word in df.iloc[:,1]:
        word = str(word)
        if word != "nan" and word != "*" and word != "**":
            return True
    return False


def format_col_name(c1):
    special_characters = ['!', '#', '$', '&', '@', '[', ']', ',', '(', ')', '^']
    c1 = c1.replace("á", 'a').replace("é", 'e').replace("í", 'i').replace("ó", 'o').replace("ú", 'u').replace("%", 'porc')
    c1 = c1.replace("/", ' ').replace("/ ", ' ')
    c1 = c1.replace("+ ", 'pos ')
    c1 = c1.replace("+", 'pos')
    c1 = c1.replace("- ", 'neg')
    c1 = c1.replace("-", 'neg')
    for i in special_characters:
        c1 = c1.replace(i, ' ').replace("{} ".format(i), '')
    c1 = c1.replace(".", ' ').replace(". ", ' ')
    c1 = re.sub(' +', ' ', c1)
    c1 = c1.rstrip()
    c1 = c1.replace(" ", '_')
    return c1


def sec_type1(doc):
    nhc = None
    text = doc.get_page_text(0)
    text = text.split('\n')
    start = 0
    end = 0
    for idx in range(len(text)):
        if text[idx] == "NHC":
            nhc = text[idx+1]
        if text[idx] == "Paciente":
            start = idx+1
        if text[idx] == "Sexo":
            end = idx
    nombre = text[start]
    if end-start > 1:        
        for idx in range(start+1, end, 1):
            nombre += " " + text[idx]
    return nhc, nombre


def sec_type2(file):
    nhc = None
    nombre = ""
    apellidos = ""
    doc = fitz.open(file)
    text = doc.get_page_text(0)
    text = text.split('\n')
    for idx in range(len(text)):
        if text[idx] == "Nº de Historia:":
            if text[idx+1] != "Centro de Extracción:":
                nhc = text[idx+1]
        if text[idx] == "Nombre:":
                nombre = text[idx+1]
        if text[idx] == "Apellidos:":
                apellidos = text[idx+1]
    nombre += " " + apellidos
    doc.close()
    return nhc, nombre


def sec_type3(file):
    nhc = None
    nombre = None
    doc = fitz.open(file)
    text = doc.get_page_text(0)
    text = text.split('\n')
    for idx in range(len(text)):
        if text[idx] == "Nº Historia:":
            nombre = text[idx+1]
        if text[idx] == "Nº Petición":
            nhc = text[idx+1]
    doc.close()
    if nombre is None:
        return None, None
    else:
        return nhc, nombre


def date_type1(doc):
    text = ""
    dates = []
    for p in range(doc.page_count):
        text += doc.get_page_text(p)

    text = text.split('\n')
    for idx in range(len(text)):
        if "Fecha de la toma:" in text[idx]:
            dates.append(text[idx].split(": ")[1].split((" "))[0])
    if len(dates) == 0:
        return None
    if len(dates) < 2:
        return dates[0]
    else:
        return dates


def date_type2(file):
    doc = fitz.open(file)
    text = doc.get_page_text(0)
    text = text.split('\n')
    for idx in range(len(text)):
        if "Fecha Solicitud" in text[idx]:
            doc.close()
            return text[idx].split(":")[1]
    return None


def date_type3(file):
    doc = fitz.open(file)
    text = doc.get_page_text(0)
    text = text.split('\n')
    for idx in range(len(text)):
        if "F.Extracción" in text[idx]:
            doc.close()
            return text[idx].split(" ")[1]
    return None


def data_type1(file):
    doc = fitz.open(file)
    text = doc.get_page_text(0)
    text = text.split('\n')
    for idx in range(len(text)):
        if "Nombre/Identificación" in text[idx]:
            sano = text[idx].split("_")[1].split(": ")[1].split(".")[0].split(" - ")
            sano_apellido = sano[1].split(",")[0]
            sano_nombre = sano[1].split(", ")[1]
            nhc_sano = sano[0]
        if "RECEPTORA" in text[idx]:
            receptor = text[idx].split(": ")[1].split(".")[0].split(" - ")
            receptor_apellido = receptor[1].split(",")[0]
            receptor_nombre = receptor[1].split(", ")[1]
            nhc_receptor = receptor[0]
    doc.close()
    return nhc_sano, sano_nombre.title(), sano_apellido.title(), nhc_receptor, receptor_nombre.title(), receptor_apellido.title()


def data_type2(file):
    nhc = ""
    nombre = ""
    apellidos = ""
    fecha_nac = ""
    doc = fitz.open(file)
    text = doc.get_page_text(0)
    text = text.split('\n')
    for idx in range(len(text)):
        if text[idx] == "Nº de Historia:":
            if text[idx+1] != "Centro de Extracción:":
                nhc = text[idx+1]
        if text[idx] == "Nombre:":
            nombre = text[idx+1]
        if text[idx] == "Apellidos:":
            apellidos = text[idx+1]
        if text[idx] == "Fecha de Nacimiento:":
            fecha_nac = text[idx+1]
    doc.close()
    return nhc, nombre.title(), apellidos.title(), fecha_nac