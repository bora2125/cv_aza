# import streamlit as st
# import pandas as pd
# import plotly.graph_objects as go
# import plotly.express as px
# from datetime import datetime, timedelta
# import boto3
# from io import BytesIO
# from PIL import Image
# import os
# import re
# from collections import defaultdict

# # Configuración de la página
# st.set_page_config(page_title="AZA-IA Demo", layout="wide")

# # Aplicar estilos personalizados
# st.markdown("""
#     <style>
#     .sidebar .sidebar-content {
#         background-color: #1E1E1E;
#         color: white;
#     }
#     .stButton>button {
#         width: 100%;
#         background-color: #1E1E1E;
#         color: white;
#         border: none;
#         text-align: left;
#         padding: 10px;
#     }
#     .stButton>button:hover {
#         background-color: #2E2E2E;
#     }
#     .main > div:first-child {
#         padding-top: 1.5rem;
#     }
#     h1 {
#         margin-top: -1rem;
#         margin-bottom: 1rem;
#     }
#     </style>
#     """, unsafe_allow_html=True)

# # AWS S3 configuration
# S3_BUCKET_NAME = "trialbucket-cv"
# S3_FOLDER = "person_count_output/"

# # Initialize S3 client
# s3_client = boto3.client('s3')

# # Function to list objects in S3 bucket
# def list_s3_objects(bucket, prefix):
#     paginator = s3_client.get_paginator('list_objects_v2')
#     pages = paginator.paginate(Bucket=bucket, Prefix=prefix)
    
#     for page in pages:
#         for obj in page.get('Contents', []):
#             yield obj['Key']

# # Función para cargar y procesar los datos
# def load_data(s3_folder):
#     pattern = r"Zone_(\d+)_person_(\d+)_(\d{8})_(\d{6})"
#     detections = []
    
#     for key in list_s3_objects(S3_BUCKET_NAME, s3_folder):
#         filename = os.path.basename(key)
#         match = re.match(pattern, filename)
#         if match:
#             zone, person_id, date, time = match.groups()
#             timestamp = datetime.strptime(f"{date}_{time}", "%Y%m%d_%H%M%S")
#             detections.append((timestamp, int(zone), int(person_id), key))
#         else:
#             print(f"Archivo no coincidente: {filename}")  # Para depuración
    
#     detections.sort(reverse=True)  # Ordenar de más reciente a más antiguo
#     return detections

# # Función para crear la barra lateral
# def sidebar():
#     with st.sidebar:
#         st.markdown("# 👁️ AZA-IA")
#         st.title("Demo")
#         if st.button("Alerts", key="alerts", type="primary" if st.session_state.current_page == "alerts" else "secondary"):
#             st.session_state.current_page = "alerts"        
#         if st.button("Visual analysis", key="visual_analysis"):
#             st.session_state.current_page = "visual_analysis"
#         if st.button("Control room (ROI)", key="control_room"):
#             st.session_state.current_page = "control_room"
        
#         # Añadir espacio para empujar el botón "Recargar datos" al final
#         st.markdown("<br>" * 10, unsafe_allow_html=True)
        
#         if st.button("Recargar datos"):
#             st.session_state.detections = load_data(S3_FOLDER)
#             st.success("Datos recargados exitosamente!")

# # Función para crear los filtros
# def filters():
#     col1, col2, col3, col4, col5 = st.columns(5)
#     with col1:
#         facility = st.selectbox("Facility", ["All facilities"])
#     with col2:
#         section = st.selectbox("Section", ["All sections"])
#     with col3:
#         camera = st.selectbox("Camera", ["All cameras"])
#     with col4:
#         event_type = st.selectbox("Type", ["All types"])
#     with col5:
#         start_date = st.date_input("Start Date", datetime.now().date() - timedelta(days=7))
#         end_date = st.date_input("End Date", datetime.now().date())
    
#     return facility, section, camera, event_type, start_date, end_date

# # Función para aplicar filtros a los datos
# def apply_filters(detections, facility, section, camera, event_type, start_date, end_date):
#     filtered_detections = [
#         d for d in detections
#         if start_date <= d[0].date() <= end_date
#         # Aquí puedes agregar más condiciones si tienes la información de facility, section, camera y event_type en tus datos
#     ]
#     return filtered_detections

# # Función mejorada para mostrar la imagen principal y las miniaturas
# def show_image_and_info(index, filenames):
#     if 0 <= index < len(filenames):
#         # Botones de navegación centrados
#         col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])
#         with col1:
#             if st.button("⏪ -10", key="back_10_button"):
#                 st.session_state.current_index = min(len(filenames) - 1, st.session_state.current_index + 10)
#                 st.experimental_rerun()
#         with col2:
#             if st.button("⬅️ Anterior", key="prev_button"):
#                 st.session_state.current_index = min(len(filenames) - 1, st.session_state.current_index + 1)
#                 st.experimental_rerun()
#         with col3:
#             if st.button("Siguiente ➡️", key="next_button"):
#                 st.session_state.current_index = max(0, st.session_state.current_index - 1)
#                 st.experimental_rerun()
#         with col4:
#             if st.button("+10 ⏩", key="forward_10_button"):
#                 st.session_state.current_index = max(0, st.session_state.current_index - 10)
#                 st.experimental_rerun()

#         col1, col2 = st.columns([4, 1])
        
#         with col1:
#             image_key = filenames[index]
#             try:
#                 response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=image_key)
#                 image_data = response['Body'].read()
#                 image = Image.open(BytesIO(image_data))
#                 st.image(image, caption=os.path.basename(image_key), use_column_width=True)
#             except Exception as e:
#                 st.error(f"Error al cargar la imagen principal: {str(e)}")
        
#         with col2:
#             st.write("Imágenes anteriores:")
#             # Mostrar 4 miniaturas de las imágenes anteriores
#             for i in range(index + 1, min(index + 5, len(filenames))):
#                 thumbnail_key = filenames[i]
#                 try:
#                     response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=thumbnail_key)
#                     thumbnail_data = response['Body'].read()
#                     thumbnail = Image.open(BytesIO(thumbnail_data))
#                     thumbnail.thumbnail((180, 180))  # Aumentado el tamaño de la miniatura
#                     # Crear un contenedor para la imagen y el botón
#                     col_thumb, col_button = st.columns([5, 1])  # Ajustado la proporción
#                     with col_thumb:
#                         st.image(thumbnail, width=180)  # Aumentado el ancho de la imagen
#                     with col_button:
#                         if st.button("👁️", key=f"thumb_{i}", help="Click para ver esta imagen"):
#                             st.session_state.current_index = i
#                             st.experimental_rerun()
#                 except Exception as e:
#                     st.error(f"Error al cargar la miniatura {i+1}: {str(e)}")

# # Función modificada para mostrar la sección de alertas
# def show_alerts_section():
#     st.header("Alertas")
#     facility, section, camera, event_type, start_date, end_date = filters()

#     # Cargar los datos
#     if 'detections' not in st.session_state:
#         st.session_state.detections = load_data(S3_FOLDER)

#     detections = st.session_state.detections
#     filtered_detections = apply_filters(detections, facility, section, camera, event_type, start_date, end_date)

#     # Mostrar información sobre el número de imágenes
#     st.write(f"Total de imágenes cargadas: {len(filtered_detections)}")

#     # Mostrar imágenes de alertas
#     if filtered_detections:
#         filenames = [d[3] for d in filtered_detections]
        
#         # Initialize current_index in session_state to show the most recent image
#         if 'current_index' not in st.session_state or st.session_state.current_page != "alerts":
#             st.session_state.current_index = 0  # Index of the most recent image (now at the start of the list)
        
#         st.session_state.current_page = "alerts"
        
#         # Display current image and thumbnails
#         show_image_and_info(st.session_state.current_index, filenames)
        
#         # Display image information
#         st.write(f"Imagen {st.session_state.current_index + 1} de {len(filenames)}")
#     else:
#         st.info("No se encontraron alertas para los filtros seleccionados.")

# # Nueva función para procesar datos para visualización
# def process_data_for_visualization(detections):
#     events_by_hour = defaultdict(lambda: defaultdict(int))
#     events_by_zone = defaultdict(int)
    
#     for detection in detections:
#         timestamp, zone, _, _ = detection
#         hour = timestamp.replace(minute=0, second=0, microsecond=0)
#         events_by_hour[zone][hour] += 1
#         events_by_zone[zone] += 1
    
#     return events_by_hour, events_by_zone

# # Función modificada para crear el gráfico de líneas
# def events_by_hour_chart(events_by_hour):
#     fig = go.Figure()
#     for zone, events in events_by_hour.items():
#         hours = list(events.keys())
#         counts = list(events.values())
#         fig.add_trace(go.Scatter(x=hours, y=counts, mode='lines', name=f'Zone {zone}'))
    
#     fig.update_layout(
#         title='Events by Hour and Zone',
#         xaxis_title='Hour',
#         yaxis_title='Number of Events',
#         legend_title='Zones',
#         legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
#     )
#     st.plotly_chart(fig, use_container_width=True)

# # Función modificada para crear el gráfico circular
# def events_by_zone_chart(events_by_zone):
#     data = pd.DataFrame(list(events_by_zone.items()), columns=['Zone', 'Events'])
#     fig = px.pie(data, values='Events', names='Zone', title='Events Distribution by Zone')
#     fig.update_traces(textposition='inside', textinfo='percent+label')
#     fig.update_layout(showlegend=False)
#     st.plotly_chart(fig, use_container_width=True)

# # Nueva función para mostrar la sección de análisis visual
# def show_visual_analysis_section():
#     st.header("Visual Analysis")
#     facility, section, camera, event_type, start_date, end_date = filters()

#     # Cargar los datos
#     if 'detections' not in st.session_state:
#         st.session_state.detections = load_data(S3_FOLDER)

#     detections = st.session_state.detections
#     filtered_detections = apply_filters(detections, facility, section, camera, event_type, start_date, end_date)

#     # Procesar datos para visualización
#     events_by_hour, events_by_zone = process_data_for_visualization(filtered_detections)

#     # Mostrar gráficos
#     col1, col2 = st.columns(2)
#     with col1:
#         events_by_hour_chart(events_by_hour)
#     with col2:
#         events_by_zone_chart(events_by_zone)

# # Función principal
# def main():
#     # Initialize session state
#     if 'current_page' not in st.session_state:
#         st.session_state.current_page = "alerts"
#     if 'current_index' not in st.session_state:
#         st.session_state.current_index = 0

#     sidebar()
    
#     if st.session_state.current_page == "alerts":
#         show_alerts_section()
#     elif st.session_state.current_page == "visual_analysis":
#         show_visual_analysis_section()
#     elif st.session_state.current_page == "control_room":
#         st.header("Control room (ROI)")
#         facility, section, camera, event_type, start_date, end_date = filters()
#         st.write("Esta sección está en desarrollo.")

# if __name__ == "__main__":
#     main()





import streamlit as st
import boto3
from io import BytesIO
from PIL import Image
import os

# Configuración de la página
st.set_page_config(page_title="AZA-IA Demo Simplificada", layout="wide")

# Aplicar estilos personalizados
st.markdown("""
    <style>
    .sidebar .sidebar-content {
        background-color: #1E1E1E;
        color: white;
    }
    .stButton>button {
        width: 100%;
        background-color: #1E1E1E;
        color: white;
        border: none;
        text-align: left;
        padding: 10px;
    }
    .stButton>button:hover {
        background-color: #2E2E2E;
    }
    .main > div:first-child {
        padding-top: 1.5rem;
    }
    h1 {
        margin-top: -1rem;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Configuración de AWS S3
S3_BUCKET_NAME = "trialbucket-cv"
CAM1_FOLDER = "detections/cam1/"
CAM2_FOLDER = "detections/cam2/"

# Inicializar el cliente de S3
s3_client = boto3.client('s3')

# Función para listar objetos en una carpeta específica de S3
def list_s3_images(bucket, prefix):
    try:
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket, Prefix=prefix)
        image_keys = []
        for page in pages:
            for obj in page.get('Contents', []):
                key = obj['Key']
                if key.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    image_keys.append(key)
        return sorted(image_keys, reverse=True)  # Ordenar de más reciente a más antiguo
    except Exception as e:
        st.error(f"Error al listar objetos en S3: {e}")
        return []

# Función para cargar una imagen desde S3
def load_image(bucket, key):
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        image_data = response['Body'].read()
        image = Image.open(BytesIO(image_data))
        return image
    except Exception as e:
        st.error(f"Error al cargar la imagen {key}: {e}")
        return None

# Función para crear la barra lateral
def sidebar():
    with st.sidebar:
        st.markdown("# 👁️ AZA-IA")
        st.title("Demo Simplificada")
        if st.button("Recargar imágenes"):
            st.session_state.reload = True
            st.experimental_rerun()

# Función para mostrar las imágenes
def show_images():
    st.header("Visualización de Imágenes desde S3")

    # Selección de cámara
    camera = st.selectbox("Selecciona la cámara", ["cam1", "cam2"])

    # Definir la carpeta según la selección
    if camera == "cam1":
        images = list_s3_images(S3_BUCKET_NAME, CAM1_FOLDER)
    else:
        images = list_s3_images(S3_BUCKET_NAME, CAM2_FOLDER)

    st.subheader(f"Imágenes de {camera}")

    if images:
        # Mostrar imágenes en un layout de cuadrícula
        cols = st.columns(3)  # Ajusta el número de columnas según prefieras
        for idx, image_key in enumerate(images):
            image = load_image(S3_BUCKET_NAME, image_key)
            if image:
                with cols[idx % 3]:
                    st.image(image, caption=os.path.basename(image_key), use_column_width=True)
    else:
        st.info("No se encontraron imágenes en la carpeta seleccionada.")

# Función principal
def main():
    # Inicializar estado de recarga
    if 'reload' not in st.session_state:
        st.session_state.reload = False

    sidebar()
    show_images()

if __name__ == "__main__":
    main()
