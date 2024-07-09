import streamlit as st
import os
import re
from datetime import datetime, timedelta
from collections import defaultdict
import plotly.graph_objects as go
import colorsys
import pandas as pd
from PIL import Image
from streamlit_plotly_events import plotly_events
import requests
from io import BytesIO

# Configuración de la página de Streamlit
st.set_page_config(page_title="Detecciones de Personas", page_icon="👥", layout="wide")
st.title("Visualización de Detecciones de Personas")

# Rango minutos
rango_minutos = 20

# GitHub repository information
GITHUB_REPO = "bora2125/cv_aza"
GITHUB_BRANCH = "main"
GITHUB_FOLDER = "person_count_output"

# Function to get raw GitHub URL
def get_github_raw_url(filename):
    return f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/{GITHUB_FOLDER}/{filename}"

# Función para cargar y procesar los datos
def load_data(github_folder):
    pattern = r"Zone_(\d+)_person_(\d+)_(\d{8})_(\d{6})"
    detections = []
    
    # Get list of files from GitHub API
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{github_folder}"
    response = requests.get(api_url)
    if response.status_code == 200:
        files = response.json()
        for file in files:
            filename = file['name']
            match = re.match(pattern, filename)
            if match:
                zone, person_id, date, time = match.groups()
                timestamp = datetime.strptime(f"{date}_{time}", "%Y%m%d_%H%M%S")
                detections.append((timestamp, int(zone), int(person_id), filename))
    
    detections.sort()  # Ordenar de más antiguo a más reciente
    return detections

# Función para redondear al intervalo de X minutos más cercano
def round_to_Xmin(dt):
    return dt - timedelta(minutes=dt.minute % rango_minutos, seconds=dt.second, microseconds=dt.microsecond)

# Función para generar colores distintos para cada zona
def generate_colors(n):
    HSV_tuples = [(x * 1.0 / n, 0.7, 0.7) for x in range(n)]
    return ['rgb({},{},{})'.format(int(r * 255), int(g * 255), int(b * 255)) 
            for r, g, b in [colorsys.hsv_to_rgb(*x) for x in HSV_tuples]]

# Cargar los datos
detections = load_data(GITHUB_FOLDER)

# Calcular el rango de tiempo por defecto (últimas 3 horas)
end_time = detections[-1][0] if detections else datetime.now()  # La detección más reciente
start_time = end_time - timedelta(hours=3)

# Filtros en la barra lateral
st.sidebar.header("Filtros")
date_range = st.sidebar.date_input("Rango de fechas", 
                                   [start_time.date(), end_time.date()])
time_range = st.sidebar.slider(
    "Rango de horas",
    min_value=datetime.min.time(),
    max_value=datetime.max.time(),
    value=(start_time.time(), end_time.time())
)

# Filtrar los datos según los filtros seleccionados
filtered_detections = [
    d for d in detections 
    if date_range[0] <= d[0].date() <= date_range[1] and
    time_range[0] <= d[0].time() <= time_range[1]
]

# Agrupar detecciones por intervalos de X minutos
grouped_detections = defaultdict(list)
for detection in filtered_detections:
    interval_start = round_to_Xmin(detection[0])
    grouped_detections[interval_start].append(detection)

# Obtener zonas únicas y asignar colores
unique_zones = sorted(set(detection[1] for detection in filtered_detections))
zone_colors = dict(zip(unique_zones, generate_colors(len(unique_zones))))

# Preparar datos para el gráfico
x_data = []
y_data = []
colors = []
hover_texts = []
zone_counts = defaultdict(int)
filenames = []

for interval_start, interval_detections in grouped_detections.items():
    x = interval_start + timedelta(minutes=rango_minutos/2)  # Punto medio del intervalo
    for i, (timestamp, zone, person_id, filename) in enumerate(interval_detections):
        x_data.append(x)
        y_data.append(i)
        colors.append(zone_colors[zone])
        hover_texts.append(f"Tiempo: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}<br>"
                           f"Zona: {zone}<br>"
                           f"ID de persona: {person_id}")
        zone_counts[zone] += 1
        filenames.append(filename)

# Crear el gráfico interactivo
fig = go.Figure(data=go.Scatter(
    x=x_data,
    y=y_data,
    mode='markers',
    marker=dict(size=10, color=colors, opacity=0.6),
    text=hover_texts,
    hoverinfo='text',
    customdata=filenames
))

# Configurar el diseño del gráfico
fig.update_layout(
    xaxis_title="Fecha y Hora",
    yaxis_title="Número de detecciones",
    xaxis=dict(
        type='date',
        tickformat="%H:%M",
        dtick=rango_minutos*60000  # X minutos en milisegundos
    ),
    yaxis=dict(showticklabels=False),
    hovermode='closest'
)

# Agregar leyenda para las zonas con el conteo de detecciones
for zone, color in zone_colors.items():
    fig.add_trace(go.Scatter(
        x=[None],
        y=[None],
        mode='markers',
        marker=dict(size=10, color=color),
        name=f'Zona {zone}',
        showlegend=True
    ))

# Crear dos columnas: una para el gráfico y otra para la imagen
col1, col2 = st.columns([1, 2])

# Mostrar el gráfico en la primera columna
with col1:
    selected_point = plotly_events(fig, click_event=True)

# Variables de estado para la imagen
if 'current_image_index' not in st.session_state:
    st.session_state.current_image_index = len(filenames) - 1

# Función para mostrar la imagen y la información
def show_image_and_info(index):
    if 0 <= index < len(filenames):
        st.session_state.current_image_index = index
        image_filename = filenames[index]
        image_url = get_github_raw_url(image_filename)
        
        try:
            response = requests.get(image_url)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                st.session_state.image = image
                st.session_state.image_caption = image_filename
            else:
                st.error(f"No se pudo cargar la imagen: {image_filename}")
        except Exception as e:
            st.error(f"Error al cargar la imagen: {str(e)}")

# Mostrar la imagen inicial (la más reciente)
show_image_and_info(st.session_state.current_image_index)            

# Manejar la selección de punto y mostrar la imagen correspondiente
if selected_point:
    selected_x = pd.to_datetime(selected_point[0]['x'])
    selected_y = selected_point[0]['y']
    
    index = next((i for i, (x, y) in enumerate(zip(x_data, y_data)) 
                  if x == selected_x and y == selected_y), None)
    
    if index is not None:
        show_image_and_info(index)

# Mostrar la imagen y la barra de desplazamiento en la segunda columna
with col2:
    # Barra de desplazamiento horizontal
    selected_index = st.slider("Desliza para ver imágenes", 
                               min_value=0, 
                               max_value=len(filenames)-1, 
                               value=st.session_state.current_image_index, 
                               step=1)
    
    # Actualizar la imagen si se cambia el índice
    if selected_index != st.session_state.current_image_index:
        show_image_and_info(selected_index)
    
    # Mostrar la imagen
    if 'image' in st.session_state:
        st.image(st.session_state.image, caption=st.session_state.image_caption, use_column_width=True)

# Mostrar estadísticas
st.header("Estadísticas de detecciones")

# Crear un DataFrame con todas las detecciones
detections_data = []
for timestamp, zone, person_id, filename in filtered_detections:
    detections_data.append({
        'Fecha': timestamp.date(),
        'Hora': timestamp.time(),
        'Zona': zone,
        'ID de Persona': person_id,
        'Archivo': filename
    })

stats_df = pd.DataFrame(detections_data)

# Ordenar el DataFrame por fecha y hora, de más reciente a más antiguo
stats_df = stats_df.sort_values(['Fecha', 'Hora'], ascending=[False, False])

# Mostrar el DataFrame con scroll
st.dataframe(stats_df, height=150)

# Descargar datos
if st.button('Descargar datos como CSV'):
    csv = stats_df.to_csv(index=False)
    st.download_button(
        label="Haga clic para descargar",
        data=csv,
        file_name="detecciones_detalladas.csv",
        mime="text/csv",
    )
