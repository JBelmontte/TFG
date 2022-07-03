import streamlit as st
from PIL import Image

st.markdown("<h2 style='text-align: center; color: black;'>Trabajo Fin de Grado</h2>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: black;'>Diseño e implementación de una herramienta bioinformática para la gestión y procesamiento de datos dentro de la terapia celular del trasplante de médula ósea</h3>", unsafe_allow_html=True)
st.markdown("***")

st.markdown("<h4 style='text-align: center; color: black;'>Introducción</h4>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: black; font-size: 20px'>Esta <b><i>herramienta bioinformática</i></b> tiene como objetivo la <b>recogida y gestión</b> de los archivos derivados de la terapia celular en cada una de sus fases, automatizando y facilitando el trabajo del personal sanitario.</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: black; font-size: 18px'>Los <i>informes y datos clínicos</i> necesarios han sido proporcionados por el <b><i>Servicio de Hematología del Hospital Universitario Virgen de la Arrixaca</i></b>.</p>", unsafe_allow_html=True)

st.markdown("***")
cols = st.columns(3)
cols[0].markdown("<p style='text-align: center; color: black;'><b>Registrar Donación</b></p>", unsafe_allow_html=True)
cols[0].markdown("<p style='text-align: center; color: black;'>Página principal para la subida y registro de los archivos relativos a una donación, además de generar un informe final de cada etapa del proceso con la información más relevante.</p>", unsafe_allow_html=True)

cols[1].markdown("<p style='text-align: center; color: black;'><b>Visualizar DB</b></p>", unsafe_allow_html=True)
cols[1].markdown("<p style='text-align: center; color: black;'>Página para visualizar la información de la base de datos recogida en tablas.</p>", unsafe_allow_html=True)

cols[2].markdown("<p style='text-align: center; color: black;'><b>Buscar Datos</b></p>", unsafe_allow_html=True)
cols[2].markdown("<p style='text-align: center; color: black;'>Página de búsqueda y consulta de la información almacenada en la base de datos.</p>", unsafe_allow_html=True)
st.markdown("***")

umu = Image.open('./images/umu.jpg')
arrixaca = Image.open('./images/logo_arrixaca.png')
informatica = Image.open('./images/informatica.png')
cols = st.columns(3)
cols[0].image(arrixaca)
cols[1].image(umu)
cols[2].image(informatica)

st.markdown("***")
st.info("Copyright © Trabajo Fin de Grado - Jose María Belmonte Martínez - Universidad de Murcia 2022")
