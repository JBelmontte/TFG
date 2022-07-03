import streamlit as st
import fitz
import tkinter as tk
from tkinter import N, filedialog

from db_functions import *
from pdf_read import *
from excel import *

button_key = 0
initial_dir = "/home/josebelmonte/Escritorio/TFG/pdfs"

def buttons(root, files, key, file_type, name_table, window_title = None, pos = None, pos_delete = None, ext = "pdf", multiple = False, write_title = True, write = True, info = None, etiqueta = None):
    global button_key, initial_dir

    if window_title is not None and write_title: st.subheader(window_title)

    if info is not None: st.info(info)

    if 'path_base' in st.session_state:
        dirname = st.session_state.path_base
    else:
        dirname = initial_dir

    if pos is None:
        cols = st.columns(6)
        pos = cols[2]

    button_key += 1
    if pos.button("Examinar", button_key):
        if multiple:
            files_tk = filedialog.askopenfilenames(master=root, initialdir = dirname, title = window_title, filetypes=[('type', '*.{}'.format(ext))])
            if len(files_tk) > 0:
                st.session_state[key] = len(files_tk)
                for i in range(len(files_tk)):
                    k = key + str(i)
                    st.session_state[k] = files_tk[i]
        else:
            file_tk = filedialog.askopenfilename(master=root, initialdir = dirname, title = window_title, filetypes=[('type', '*.{}'.format(ext))])
            if isinstance(file_tk, str): 
                st.session_state[key] = file_tk

    if multiple:
        return_files = []
        if key in st.session_state:
            num = st.session_state[key]
            for n in range(num):
                k = key + str(n)
                file = st.session_state[k]
                return_files.append(file)
                if write: st.success(file.split("/")[-1])
            for file in return_files:
                files.append((file, file_type, name_table))
            if pos_delete is None: 
                pos_delete = cols[3]
            if pos_delete.button("Borrar", button_key):
                for file in return_files:
                    files.remove((file, file_type, name_table))
                    if key in st.session_state:
                        deleted = st.session_state[key]
                        del st.session_state[key]
                    st.info("Archivo borrado: {}".format(deleted.split("/")[-1]))
        else:
            if pos_delete is None: 
                pos_delete = cols[3]
            pos_delete.button("Borrar", button_key, disabled = True)
    else:
        if key in st.session_state:
            file = st.session_state[key]
            if write: st.success(file.split("/")[-1])
            files.append((file, file_type, name_table))
            if etiqueta is not None:
                with open(file) as f:
                    et = f.read()
                    st.info(etiqueta.format(et))
            if pos_delete is None: 
                pos_delete = cols[3]
            if pos_delete.button("Borrar", button_key):
                files.remove((file, file_type, name_table))
                if key in st.session_state:
                    deleted = st.session_state[key]
                    del st.session_state[key]
                st.info("Archivo borrado: {}".format(deleted.split("/")[-1]))
        else:
            if pos_delete is None: 
                pos_delete = cols[3]
            pos_delete.button("Borrar", button_key, disabled = True)

st.set_page_config(page_title = "Registrar donación", page_icon = "📥")
st.markdown("<h1 style='text-align: center; color: black;'>Registrar donación</h1>", unsafe_allow_html=True)
st.sidebar.markdown("# Registrar donación")
files = []

root = tk.Tk()
root.withdraw()

# Make folder picker dialog appear on top of other windows
root.wm_attributes('-topmost', 1)

# Folder picker button
st.subheader("Selección de la carpeta raíz")
st.write('Seleccione la carpeta base donde se van a buscar los archivos:')
if st.button('Examinar carpeta'):
    dirname = filedialog.askdirectory(master=root, initialdir = initial_dir)
    if isinstance(dirname, str): 
        st.session_state['path_base'] = dirname
        
if 'path_base' in st.session_state:
    dirname = st.session_state.path_base
else:
    dirname = initial_dir
        
st.success("Carpeta raíz: {}".format(dirname))
        
buttons(root, files, "A1", -1, "Código_Donación", window_title = "1. Código de donación", ext = "txt", write = False)
if 'A1' in st.session_state:
    with open(st.session_state.A1) as f:
        dc = f.read()
    donation_code = st.text_input("Código de donación", dc, disabled = True)
else:
    donation_code = st.text_input("Código de donación", placeholder = "Código de donación")


with st.expander("Evaluación donante"):

    st.subheader("2. Estudio pre-transplante")
    cols = st.columns(5)
    transplant_type = cols[2].radio("Tipo de trasplante", ('Alogénico', 'Autólogo'))

    if transplant_type == "Alogénico":
        cols = st.columns(3)
        title1 = "Estudio donante sano.pdf"
        title2 = "Estudio pre-trasplante.pdf"
        cols[0].write(title1)
        cols[2].write(title2)
        cols = st.columns(6)
        buttons(root, files, "Aa2", 1, "A2_Estudio_Donante_Sano", window_title = title1, pos = cols[0], pos_delete = cols[1], write_title = False)
        buttons(root, files, "Aa3", 1, "A3_Estudio_Pre_Transplante", window_title = title2, pos = cols[4], pos_delete = cols[5], write_title = False)

    else:
        cols = st.columns(3)
        title = "Estudio pre-trasplante.pdf"
        cols[1].write(title)
        buttons(root, files, "Ab3", 1, "A3_Estudio_Pre_Transplante", window_title = title, write_title = False)


with st.expander("Aféresis"):
    buttons(root, files, "B1", 2, "B1_Contaje_Control_Pre_Aféresis", window_title = "1. Contaje/Control Pre-Aféresis SP", multiple = True, info = "Puede seleccionar un único fichero PDF o, en caso de que haya varios, múltiples archivos.")
    st.subheader("2 y 3. Contajes Tubos SP Control Pre-Aféresis")
    cols = st.columns(3)
    title1 = "Contaje 1er Tubo SP.pdf"
    title2 = "Contaje 2o Tubo SP.pdf"
    cols[0].write(title1)
    cols[2].write(title2)
    cols = st.columns(6)
    buttons(root, files, "B2", 2, "B2_Contaje_1er_Tubo", window_title = title1, pos = cols[0], pos_delete = cols[1], write_title = False)
    buttons(root, files, "B3", 2, "B3_Contaje_2o_Tubo", window_title = title2, pos = cols[4], pos_delete = cols[5], write_title = False)
            

    st.write("")
    if st.checkbox('¿Se han realizado Contajes de controles intermedios de la bolsa de aféresis?', value = True):
        buttons(root, files, "B4", 2, "B4_Contaje_Controles_Intermedios", window_title = "4. Contaje controles intermedios de la bolsa de aféresis")
    
    buttons(root, files, "B51", 2, "B51_Contaje_Producto_Final", window_title = "5.1. Contaje Bolsa Aféresis - Producto Final")
    buttons(root, files, "B52", 3, "B52_Cultivo_Micro_Final", window_title = "5.2. Cultivo Microbiológico - Producto Final")
    buttons(root, files, "B53", 0, "B53_Etiqueta_Aféresis", window_title = "5.3. Etiqueta Aféresis", ext = "txt", write = False, etiqueta = "Etiqueta Aféresis: {}")
    
    if st.checkbox('Congelación'):
        buttons(root, files, "B54", 0, "B54_Etiquetas_Congelación", window_title = "5.4. Etiquetas de Congelación", ext = "txt", write = False, etiqueta = "Etiqueta Aféresis: {}")

        
with st.expander("Tipo de trasplante"):
    #seleccion = st.selectbox("Tipo", ["Depleción CD3+", "Depleción CD19+CD3+", "Depleción CD19+CD3TCR", "Depleción CD45RA", "Descongelación e Infusión", "FEC online", "Ficoll", "Harvest", "Infusión directa", "Lavado e infusión", "Sangría y Buffy coat", "Selección CD34+", "Selección CD56+", "SelecciónCD133+"])
    seleccion = st.selectbox("Tipo", ["Selección CD34+", "Depleción CD19+ CD3+ab", "Descongelación y Lavado"])
    
    if seleccion == "Selección CD34+" or seleccion == "Depleción CD19+ CD3+ab":
        buttons(root, files, "Ca1", 0, "C1_Etiqueta_Producto_Inicial", window_title = "1. Etiqueta producto inicial", ext = "txt", write = False, etiqueta = "Etiqueta producto inicial: {}")
        buttons(root, files, "Ca21", 2, "C21_Contaje_Post_Sepax", window_title = "2.1. Contaje Post-Sepax")
        buttons(root, files, "Ca22", 3, "C22_Cultivo_Microbiologico_Post_Sepax", window_title = "2.2. Cultivo Microbiológico Post-Sepax")
        buttons(root, files, "Ca31", 2, "C31_Contaje_Frac_Deplec", window_title = "3.1. Contaje Fracción Deplecionada")
        buttons(root, files, "Ca32", 3, "C32_Cultivo_Microbiologico_Frac_Deplec", window_title = "3.2. Cultivo Microbiológico Fracción Deplecionada")
        buttons(root, files, "Ca41", 2, "C41_Contaje_Frac_Pos", window_title = "4.1. Contaje Fracción Positiva")
        buttons(root, files, "Ca42", 3, "C42_Cultivo_Microbiologico_Frac_Pos", window_title = "4.2. Cultivo Microbiológico Fracción Positiva")
        buttons(root, files, "Ca5", 0, "C5_Etiqueta_Infusión", window_title = "5. Etiqueta Infusión", ext = "txt", write = False, etiqueta = "Etiqueta Infusión: {}")
    if seleccion == "Descongelación y Lavado":
        buttons(root, files, "Cb11", 2, "C11_Contaje_Control_NUNC", window_title = "1.1. Contaje Control NUNC")
        buttons(root, files, "Cb12", 3, "C12_Cultivo_Microbiológico_NUNC", window_title = "1.2. Cultivo Microbiológico NUNC")
        buttons(root, files, "Cb2", 2, "C2_Contajes_Bolsas_Descong_sin_lavar", window_title = "2. Descongelación", multiple = True, info = "Puede seleccionar un único fichero PDF o, en caso de que haya varios, múltiples archivos.")
        buttons(root, files, "Cb31", 2, "C31_Contajes_Bolsas_Descong_lavadas", window_title = "3.1. Lavado", multiple = True, info = "Puede seleccionar un único fichero PDF o, en caso de que haya varios, múltiples archivos.")
        buttons(root, files, "Cb32", 0, "C32_Etiquetas_Descongelación", window_title = "3.2. Etiquetas de Descongelación y Lavado", ext = "txt", write = False, etiqueta = "Etiqueta/s Descongelación y Lavado: {}")

        ############################### FILES ###############################

st.markdown("***")
cols = st.columns(3)
if cols[1].button("Registrar donación"):
    with st.spinner("Leyendo documentos..."):
        nhcs = []
        names = []
        valid = True
        for file in files:
            file_path = file[0]
            file_type = file[1]

            if file_type == 1:
                doc = fitz.open(file_path)
                nhc, nombre = sec_type1(doc)
                if nhc is not None: nhcs.append(nhc)
                names.append(nombre)
                doc.close()
            elif file_type == 2:
                nhc, nombre = sec_type2(file_path)
                if nhc is not None: nhcs.append(nhc)
                names.append(nombre)
            elif file_type == 3:
                nhc, nombre = sec_type3(file_path)
                if nhc is not None: nhcs.append(nhc)
                if nhc is not None: names.append(nombre)

        nhcs = list(dict.fromkeys(nhcs))
        names = list(dict.fromkeys(names))

        if transplant_type == "Alogénico":
            if len(nhcs) > 2 or len(names) > 2:
                st.error("Subida de archivos incorrecta, se encuentran archivos de otro paciente.")
                st.error(nhcs)
                st.error(names)
                valid = False
        elif transplant_type == "Autólogo":
            if len(nhcs) > 1 or len(names) > 1:
                st.error("Subida de archivos incorrecta, se encuentran archivos de otro paciente.")
                valid = False

        if donation_code == "":
            st.error("Error: El código de donación no puede estar vacío.")
            valid = False
                
        if valid:
            progress_bar = st.sidebar.progress(0)
            status_text = st.sidebar.empty()
            steps = math.trunc(100/len(files))
            steps = math.trunc(steps)
            total_time = "0"
            p = -1
            for file in files:
                p += 1
                i = p*steps
                progress_bar.progress(i)
                status_text.text("{}% Completado".format(i))

                file_path = file[0]
                file_type = file[1]
                name_table = file[2]

                loading_time = "0"

                if file_type != -1:
                    if file_type == 0:
                        create_table0(name_table)
                    else:
                        create_table(name_table)

                if file_type == 0:
                    with open(file_path) as f:
                        info = f.read()
                    info = info.split("\n")
                    if len(info) > 0:
                        for i in range(len(info)):
                            add_donation_code0(name_table, donation_code)
                            tabla = "Etiqueta_" + str(i)
                            if not column_exists(name_table, tabla):
                                create_columns(name_table, tabla)
                            add_data0(name_table, donation_code, tabla, info[i])

                elif file_type == 1:
                    doc = fitz.open(file_path)
                    type_info, data_info, loading_time = read_type1(doc)
                    dates = date_type1(doc)
                    if dates is None: 
                        st.error("Archivo no válido: {}".format(file_path.split("/")[-1]))
                        continue
                    doc.close()
                    if isinstance(type_info[0], str):
                        # Solo hay un informe
                        add_donation_code(name_table, donation_code, dates)
                        for idx in range(len(type_info)):
                            type_single = type_info[idx]
                            data_single = data_info[idx]
                            if not column_exists(name_table, type_single):
                                create_columns(name_table, type_single)
                            add_data(name_table, donation_code, dates, type_single, data_single)
                    else:
                        # Hay más de un informe, actualizamos con los valores del último
                        add_donation_code(name_table, donation_code, dates[-1])
                        for idx in range(len(type_info[0])):
                            type_single = type_info[0][idx]
                            data_single = data_info[0][idx]
                            if not column_exists(name_table, type_single):
                                create_columns(name_table, type_single)
                            add_data(name_table, donation_code, dates[-1], type_single, data_single)
                        for i in range(1, len(type_info), 1):
                            for idx in range(len(type_info[i])):
                                type_single = type_info[i][idx]
                                data_single = data_info[i][idx]
                                if not column_exists(name_table, type_single):
                                    create_columns(name_table, type_single)
                                add_data(name_table, donation_code, dates[-1], type_single, data_single)
                elif file_type == 2:
                    dates = date_type2(file_path)
                    if dates is None: 
                        st.error("Archivo no válido: {}".format(file_path.split("/")[-1]))
                        continue
                    type_info, data_info, loading_time = read_type2(file_path)
                            
                    add_donation_code(name_table, donation_code, dates)
                    for idx in range(len(type_info)):
                        type_single = type_info[idx]
                        data_single = data_info[idx]
                        if not column_exists(name_table, type_single):
                            create_columns(name_table, type_single)
                        add_data(name_table, donation_code, dates, type_single, data_single)
                elif file_type == 3:
                    dates = date_type3(file_path)
                    if dates is None: 
                        st.error("Archivo no válido: {}".format(file_path.split("/")[-1]))
                        continue
                    type_info, data_info, loading_time = read_type3(file_path)
                            
                    add_donation_code(name_table, donation_code, dates)
                    for idx in range(len(type_info)):
                        type_single = type_info[idx]
                        data_single = data_info[idx]
                        if not column_exists(name_table, type_single):
                            create_columns(name_table, type_single)
                        add_data(name_table, donation_code, dates, type_single, data_single)
                total_time = str(float(loading_time)+float(total_time))
                st.info(file_path.split("/")[-1] + ' leído correctamente en {:.2} segundos.'.format(loading_time))
            progress_bar.progress(100)
            status_text.text("100% Completado")
            st.success("Finalizado! Tiempo: {:.2} segundos.".format(total_time))

st.markdown("***")
f1 = None
f2 = None
for file in files:
    if "A2_Estudio_Donante_Sano" in file:
        f1 = file[0]
    if "B51_Contaje_Producto_Final" in file:
        f2 = file[0]
cols = st.columns(4)

if transplant_type == "Alogénico":
    disabled1 = True
    disabled2 = False
else:
    disabled1 = False
    disabled2 = True

if cols[1].button("Crear Informe Aféresis", disabled = disabled1):
#if cols[1].button("Crear Informe Aféresis"):
    if f2 is not None:
        if dirname == initial_dir:
            dst = "./db/Informe_Aferesis_" + donation_code + ".xlsx"
        else:
            dst = "{}/Informe_Aferesis_".format(dirname) + donation_code + ".xlsx"
        informe_aferesis(donation_code, f2, dst)
        st.success("Informe creado con éxito en {}".format(dst))

if cols[2].button("Crear Informe Infusión", disabled = disabled2):
#if cols[2].button("Crear Informe Infusión"):
    if f1 is not None:
        if dirname == initial_dir:
            dst = "./db/Informe_Infusión_" + donation_code + ".xlsx"
        else:
            dst = "{}/Informe_Infusión_".format(dirname) + donation_code + ".xlsx"
        informe_infusion(donation_code, f1, dst)
        st.success("Informe creado con éxito en {}".format(dst))
