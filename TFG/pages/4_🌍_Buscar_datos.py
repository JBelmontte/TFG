import streamlit as st
import pandas as pd
import tkinter as tk
from tkinter import N, filedialog
from difflib import SequenceMatcher

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

st.set_page_config(page_title = "Buscar datos", page_icon = "🌍")
st.markdown("<h1 style='text-align: center; color: black;'>Buscar datos</h1>", unsafe_allow_html=True)
files = []

root = tk.Tk()
root.withdraw()

# Make folder picker dialog appear on top of other windows
root.wm_attributes('-topmost', 1)

title = "1. Código de donación"
st.subheader(title)
st.info("Puede examinar el archivo .txt con el código de donación, introducirlo manualmente o buscarlo entre los códigos existentes.")

donation_code1 = None
        
buttons(root, files, "Buscar_DC", -1, "Código_Donación", window_title = "1. Código de donación", ext = "txt", write = False)
if 'Buscar_DC' in st.session_state:
    with open(st.session_state.Buscar_DC) as f:
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

search = st.text_input("Introduce campo a buscar")

searchs = []
        
st.markdown("***")
middle = st.columns(5)
if middle[2].button("Buscar"):
    if search != "":
        search_form = format_col_name(search)
        for table in tables:
            table = table[0]
            if donation_code == "Todos los códigos":
                data = view_search(table, search_form)
                if data is not None:
                    for d in data:
                        searchs.append([d[0], d[1], table, search_form, d[2]])
            else:
                data = view_search(table, search_form, donation_code)
                if data is not None: 
                    for d in data:
                        searchs.append([donation_code, d[0], table, search_form, d[1]])
        if len(searchs) > 0:
            with st.expander("Datos encontrados"):
                clean_df = pd.DataFrame(searchs, columns = ["Código Donación", "Fecha", "Tabla", "Tipo", "Búsqueda"])
                st.dataframe(clean_df)
                columns_alike = []
            searchs2 = []
            for table in tables:
                columns = []
                table = table[0]
                cols = view_all_columns(table)
                for col in cols:
                    if SequenceMatcher(None, search_form, col).ratio() > 0.7:
                        columns.append(col)
                        if col not in columns_alike and col != search: columns_alike.append(col)
                for col in columns:
                    if donation_code == "Todos los códigos":
                        data = view_search(table, col)
                        if data is not None:
                            for d in data:
                                if [d[0], d[1], table, col, d[2]] not in searchs: searchs2.append([d[0], d[1], table, col, d[2]])
                    else:
                        data = view_search(table, col, donation_code)
                        if data is not None: 
                            for d in data:
                                if [donation_code, d[0], table, col, d[1]] not in searchs: searchs2.append([donation_code, d[0], table, col, d[1]])
            if len(columns_alike) > 0 and len(searchs2) > 0: st.info("Búsqueda relacionada: {}".format(columns_alike))
            if len(searchs2) > 0:
                with st.expander("Datos encontrados"):
                    clean_df = pd.DataFrame(searchs2, columns = ["Código Donación", "Fecha", "Tabla", "Tipo", "Búsqueda"])
                    st.dataframe(clean_df)
        else:
            st.warning("No existe la columna: {}".format(search))
            found = False
            rango = 0.8
            for i in range(5):
                rango -= 0.1
                columns_alike = []
                for table in tables:
                    columns = []
                    table = table[0]
                    cols = view_all_columns(table)
                    for col in cols:
                        if SequenceMatcher(None, search_form, col).ratio() > rango:
                            columns.append(col)
                            if col not in columns_alike: columns_alike.append(col)
                    for col in columns:
                        if donation_code == "Todos los códigos":
                            data = view_search(table, col)
                            if data is not None:
                                for d in data:
                                    searchs.append([d[0], d[1], table, col, d[2]])
                        else:
                            data = view_search(table, col, donation_code)
                            if data is not None: 
                                for d in data:
                                    searchs.append([donation_code, d[0], table, col, d[1]])
                if len(columns_alike) > 0: st.info("Búsqueda relacionada: {}".format(columns_alike))
                if len(searchs) > 0:
                    with st.expander("Datos encontrados"):
                        clean_df = pd.DataFrame(searchs, columns = ["Código Donación", "Fecha", "Tabla", "Tipo", "Búsqueda"])
                        st.dataframe(clean_df)
                        found = True
                        break
            if not found:
                st.error("No se ha obtenido información")
                
    else:
        st.error("Debes introducir un campo de búsqueda")