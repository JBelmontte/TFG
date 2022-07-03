import streamlit as st
import pandas as pd
import tkinter as tk
from tkinter import N, filedialog

from db_functions import *
from pdf_read import *
from excel import *

button_key = 0

def buttons(root, files, key, file_type, name_table, window_title = None, pos = None, pos_delete = None, ext = "pdf", multiple = False, write_title = True, write = True, info = None, etiqueta = None):
    global button_key

    if window_title is not None and write_title: st.subheader(window_title)

    if info is not None: st.info(info)

    if 'path_base' in st.session_state:
        dirname = st.session_state.path_base
    else:
        dirname = "/home/josebelmonte/Escritorio/TFG/pdfs/"

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

st.set_page_config(page_title = "Visualizar DB", page_icon = "📊")
st.markdown("<h1 style='text-align: center; color: black;'>Visualizar DB</h1>", unsafe_allow_html=True)
files = []

root = tk.Tk()
root.withdraw()

# Make folder picker dialog appear on top of other windows
root.wm_attributes('-topmost', 1)

title = "1. Código de donación"
st.subheader(title)
st.info("Puede examinar el archivo .txt con el código de donación, introducirlo manualmente o buscarlo entre los códigos existentes.")

donation_code1 = None

buttons(root, files, "Buscar_T", -1, "Código_Donación", window_title = "1. Código de donación", ext = "txt", write = False)
if 'Buscar_T' in st.session_state:
    with open(st.session_state.Buscar_T) as f:
        dc = f.read()
    donation_code1 = st.text_input("Código de donación", dc, disabled = True)
else:
    donation_code2 = st.text_input("Código de donación", placeholder = "Código de donación")

dcs = []
dcs.append("Todos los códigos")
tables = view_all_tables()
for table in tables:
    table = table[0]
    dc = view_donation_code(table)
    if dc not in dcs: dcs.append(dc)
        
donation_code3 = st.selectbox("Lista de Códigos de donación", dcs)

if donation_code1 is not None:
    donation_code = donation_code1
elif donation_code2 != "":
    donation_code = donation_code2
else:
    donation_code = donation_code3
st.markdown("***")

tables = view_all_tables()
if len(tables) == 0:
    st.info("No se encuentra información que mostrar.")
else:
    for table in tables:
        table = table[0]
        if donation_code == "Todos los códigos":
            cols = view_all_columns(table)
            data = view_all_data(table)
            if len(data) > 0:
                with st.expander(' '.join(table.split("_")[1:])):
                    clean_df = pd.DataFrame(data, columns = cols)
                    st.dataframe(clean_df)
        else:
            cols = view_all_columns(table, donation_code)
            data = view_all_data(table, donation_code)
            if len(data) > 0:
                with st.expander(' '.join(table.split("_")[1:])):
                    clean_df = pd.DataFrame(data, columns = cols)
                    st.dataframe(clean_df)