# # # import streamlit as st
# # # import os
# # # import re
# # # from datetime import datetime, timedelta
# # # from collections import defaultdict
# # # import plotly.graph_objects as go
# # # import colorsys
# # # import pandas as pd
# # # from PIL import Image
# # # from streamlit_plotly_events import plotly_events
# # # import boto3
# # # from io import BytesIO

# # # # Configuración de la página de Streamlit
# # # st.set_page_config(page_title="Detecciones de Personas", page_icon="👥", layout="wide")
# # # st.title("Visualización de Detecciones de Personas")

# # # # Rango minutos
# # # rango_minutos = 20

# # # # AWS S3 configuration
# # # S3_BUCKET_NAME = "trialbucket-cv"
# # # S3_FOLDER = "person_count_output/"

# # # # Initialize S3 client
# # # s3_client = boto3.client('s3')

# # # # Function to list objects in S3 bucket
# # # def list_s3_objects(bucket, prefix):
# # #     paginator = s3_client.get_paginator('list_objects_v2')
# # #     pages = paginator.paginate(Bucket=bucket, Prefix=prefix)
    
# # #     for page in pages:
# # #         for obj in page.get('Contents', []):
# # #             yield obj['Key']

# # # # Función para cargar y procesar los datos
# # # def load_data(s3_folder):
# # #     pattern = r"Zone_(\d+)_person_(\d+)_(\d{8})_(\d{6})"
# # #     detections = []
    
# # #     for key in list_s3_objects(S3_BUCKET_NAME, s3_folder):
# # #         filename = os.path.basename(key)
# # #         match = re.match(pattern, filename)
# # #         if match:
# # #             zone, person_id, date, time = match.groups()
# # #             timestamp = datetime.strptime(f"{date}_{time}", "%Y%m%d_%H%M%S")
# # #             detections.append((timestamp, int(zone), int(person_id), key))
    
# # #     detections.sort()  # Ordenar de más antiguo a más reciente
# # #     return detections

# # # # Función para redondear al intervalo de X minutos más cercano
# # # def round_to_Xmin(dt):
# # #     return dt - timedelta(minutes=dt.minute % rango_minutos, seconds=dt.second, microseconds=dt.microsecond)

# # # # Función para generar colores distintos para cada zona
# # # def generate_colors(n):
# # #     HSV_tuples = [(x * 1.0 / n, 0.7, 0.7) for x in range(n)]
# # #     return ['rgb({},{},{})'.format(int(r * 255), int(g * 255), int(b * 255)) 
# # #             for r, g, b in [colorsys.hsv_to_rgb(*x) for x in HSV_tuples]]

# # # # Cargar los datos
# # # detections = load_data(S3_FOLDER)

# # # # Calcular el rango de tiempo por defecto (últimas 3 horas)
# # # end_time = detections[-1][0] if detections else datetime.now()  # La detección más reciente
# # # start_time = end_time - timedelta(hours=3)

# # # # Filtros en la barra lateral
# # # st.sidebar.header("Filtros")
# # # date_range = st.sidebar.date_input("Rango de fechas", 
# # #                                    [start_time.date(), end_time.date()])
# # # time_range = st.sidebar.slider(
# # #     "Rango de horas",
# # #     min_value=datetime.min.time(),
# # #     max_value=datetime.max.time(),
# # #     value=(start_time.time(), end_time.time())
# # # )

# # # # Filtrar los datos según los filtros seleccionados
# # # filtered_detections = [
# # #     d for d in detections 
# # #     if date_range[0] <= d[0].date() <= date_range[1] and
# # #     time_range[0] <= d[0].time() <= time_range[1]
# # # ]

# # # # Agrupar detecciones por intervalos de X minutos
# # # grouped_detections = defaultdict(list)
# # # for detection in filtered_detections:
# # #     interval_start = round_to_Xmin(detection[0])
# # #     grouped_detections[interval_start].append(detection)

# # # # Obtener zonas únicas y asignar colores
# # # unique_zones = sorted(set(detection[1] for detection in filtered_detections))
# # # zone_colors = dict(zip(unique_zones, generate_colors(len(unique_zones))))

# # # # Preparar datos para el gráfico
# # # x_data = []
# # # y_data = []
# # # colors = []
# # # hover_texts = []
# # # zone_counts = defaultdict(int)
# # # filenames = []

# # # for interval_start, interval_detections in grouped_detections.items():
# # #     x = interval_start + timedelta(minutes=rango_minutos/2)  # Punto medio del intervalo
# # #     for i, (timestamp, zone, person_id, key) in enumerate(interval_detections):
# # #         x_data.append(x)
# # #         y_data.append(i)
# # #         colors.append(zone_colors[zone])
# # #         hover_texts.append(f"Tiempo: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}<br>"
# # #                            f"Zona: {zone}<br>"
# # #                            f"ID de persona: {person_id}")
# # #         zone_counts[zone] += 1
# # #         filenames.append(key)

# # # # Crear el gráfico interactivo
# # # fig = go.Figure(data=go.Scatter(
# # #     x=x_data,
# # #     y=y_data,
# # #     mode='markers',
# # #     marker=dict(size=10, color=colors, opacity=0.6),
# # #     text=hover_texts,
# # #     hoverinfo='text',
# # #     customdata=filenames
# # # ))

# # # # Configurar el diseño del gráfico
# # # fig.update_layout(
# # #     xaxis_title="Fecha y Hora",
# # #     yaxis_title="Número de detecciones",
# # #     xaxis=dict(
# # #         type='date',
# # #         tickformat="%H:%M",
# # #         dtick=rango_minutos*60000  # X minutos en milisegundos
# # #     ),
# # #     yaxis=dict(showticklabels=False),
# # #     hovermode='closest'
# # # )

# # # # Agregar leyenda para las zonas con el conteo de detecciones
# # # for zone, color in zone_colors.items():
# # #     fig.add_trace(go.Scatter(
# # #         x=[None],
# # #         y=[None],
# # #         mode='markers',
# # #         marker=dict(size=10, color=color),
# # #         name=f'Zona {zone}',
# # #         showlegend=True
# # #     ))

# # # # Crear dos columnas: una para el gráfico y otra para la imagen
# # # col1, col2 = st.columns([1, 2])

# # # # Mostrar el gráfico en la primera columna
# # # with col1:
# # #     selected_point = plotly_events(fig, click_event=True)

# # # # Variables de estado para la imagen
# # # if 'current_image_index' not in st.session_state:
# # #     st.session_state.current_image_index = len(filenames) - 1

# # # # Función para mostrar la imagen y la información
# # # def show_image_and_info(index):
# # #     if 0 <= index < len(filenames):
# # #         st.session_state.current_image_index = index
# # #         image_key = filenames[index]
        
# # #         try:
# # #             response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=image_key)
# # #             image_data = response['Body'].read()
# # #             image = Image.open(BytesIO(image_data))
# # #             st.session_state.image = image
# # #             st.session_state.image_caption = os.path.basename(image_key)
# # #         except Exception as e:
# # #             st.error(f"Error al cargar la imagen: {str(e)}")

# # # # Mostrar la imagen inicial (la más reciente)
# # # show_image_and_info(st.session_state.current_image_index)            

# # # # Manejar la selección de punto y mostrar la imagen correspondiente
# # # if selected_point:
# # #     selected_x = pd.to_datetime(selected_point[0]['x'])
# # #     selected_y = selected_point[0]['y']
    
# # #     index = next((i for i, (x, y) in enumerate(zip(x_data, y_data)) 
# # #                   if x == selected_x and y == selected_y), None)
    
# # #     if index is not None:
# # #         show_image_and_info(index)

# # # # Mostrar la imagen y la barra de desplazamiento en la segunda columna
# # # with col2:
# # #     # Barra de desplazamiento horizontal
# # #     selected_index = st.slider("Desliza para ver imágenes", 
# # #                                min_value=0, 
# # #                                max_value=len(filenames)-1, 
# # #                                value=st.session_state.current_image_index, 
# # #                                step=1)
    
# # #     # Actualizar la imagen si se cambia el índice
# # #     if selected_index != st.session_state.current_image_index:
# # #         show_image_and_info(selected_index)
    
# # #     # Mostrar la imagen
# # #     if 'image' in st.session_state:
# # #         st.image(st.session_state.image, caption=st.session_state.image_caption, use_column_width=True)

# # # # Mostrar estadísticas
# # # st.header("Estadísticas de detecciones")

# # # # Crear un DataFrame con todas las detecciones
# # # detections_data = []
# # # for timestamp, zone, person_id, key in filtered_detections:
# # #     detections_data.append({
# # #         'Fecha': timestamp.date(),
# # #         'Hora': timestamp.time(),
# # #         'Zona': zone,
# # #         'ID de Persona': person_id,
# # #         'Archivo': os.path.basename(key)
# # #     })

# # # stats_df = pd.DataFrame(detections_data)

# # # # Ordenar el DataFrame por fecha y hora, de más reciente a más antiguo
# # # stats_df = stats_df.sort_values(['Fecha', 'Hora'], ascending=[False, False])

# # # # Mostrar el DataFrame con scroll
# # # st.dataframe(stats_df, height=150)

# # # # Descargar datos
# # # if st.button('Descargar datos como CSV'):
# # #     csv = stats_df.to_csv(index=False)
# # #     st.download_button(
# # #         label="Haga clic para descargar",
# # #         data=csv,
# # #         file_name="detecciones_detalladas.csv",
# # #         mime="text/csv",
# # #     )







# import streamlit as st
# import pandas as pd
# import plotly.graph_objects as go
# import plotly.express as px
# from datetime import datetime, timedelta

# # Configuración de la página
# st.set_page_config(page_title="AZ/AI Demo", layout="wide")

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
#     </style>
#     """, unsafe_allow_html=True)

# # Función para crear la barra lateral
# def sidebar():
#     with st.sidebar:
#         st.markdown("# 👁️ AZ/AI")
#         st.title("Demo")
#         st.button("Control room", key="control_room")
#         st.button("Ergonomics", key="ergonomics")
#         st.button("Visual analysis", key="visual_analysis")
#         st.button("Alerts", key="alerts")

# # Función para crear la barra de navegación superior
# def top_navigation():
#     col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
#     with col1:
#         st.button("Overview")
#     with col2:
#         st.button("Alerts")
#     with col3:
#         st.button("Compliance")
#     with col4:
#         st.download_button("Save as PDF", "data", file_name="report.pdf")

# # Función para crear los filtros
# def filters():
#     col1, col2, col3, col4, col5 = st.columns(5)
#     with col1:
#         st.selectbox("Facility", ["All facilities"])
#     with col2:
#         st.selectbox("Section", ["All sections"])
#     with col3:
#         st.selectbox("Camera", ["All cameras"])
#     with col4:
#         st.selectbox("Type", ["All types"])
#     with col5:
#         st.date_input("Date Range", [datetime.now() - timedelta(days=7), datetime.now()])

# # Función para crear el gráfico circular
# def category_distribution():
#     data = {
#         'Category': ['Area controls', 'Behavior', 'Housekeeping', 'Pandemic', 'PPE', 'Vehicle'],
#         'Value': [10, 20, 15, 5, 30, 20]
#     }
#     fig = px.pie(data, values='Value', names='Category', title='Category distribution')
#     fig.update_traces(textposition='inside', textinfo='percent+label')
#     fig.update_layout(
#         showlegend=False,
#         margin=dict(l=20, r=20, t=40, b=20),
#     )
#     st.plotly_chart(fig, use_container_width=True)

# # Función para crear el gráfico de líneas
# def alert_count():
#     data = {
#         'Date': ['Jul 2', 'Jul 3', 'Jul 4', 'Jul 5', 'Jul 6', 'Jul 7', 'Jul 8'],
#         'Area controls': [3, 4, 2, 3, 2, 5, 4],
#         'Behavior': [20, 30, 34, 33, 28, 29, 34],
#         'Housekeeping': [1, 2, 3, 2, 1, 2, 3],
#         'Pandemic': [2, 3, 2, 1, 2, 1, 2],
#         'PPE': [50, 55, 51, 57, 61, 56, 64],
#         'Vehicle': [40, 45, 43, 44, 47, 45, 46]
#     }
#     df = pd.DataFrame(data)
#     fig = go.Figure()
#     for column in df.columns[1:]:
#         fig.add_trace(go.Scatter(x=df['Date'], y=df[column], mode='lines', name=column))
#     fig.update_layout(
#         title='Alert count per category',
#         xaxis_title='Date',
#         yaxis_title='Count',
#         legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
#         margin=dict(l=20, r=20, t=60, b=20),
#     )
#     st.plotly_chart(fig, use_container_width=True)

# # Función principal
# def main():
#     sidebar()
#     top_navigation()
#     filters()
    
#     col1, col2 = st.columns(2)
#     with col1:
#         category_distribution()
#     with col2:
#         alert_count()

#     # Añadir más contenido aquí según sea necesario

# if __name__ == "__main__":
#     main()


## VERSION OPTIMA #1 ##

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
# st.set_page_config(page_title="AZ/AI Demo", layout="wide")

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
    
#     detections.sort()  # Ordenar de más antiguo a más reciente
#     return detections

# # Función para crear la barra lateral
# def sidebar():
#     with st.sidebar:
#         st.markdown("# 👁️ AZ/AI")
#         st.title("Demo")
#         st.button("Control room", key="control_room")
#         st.button("Ergonomics", key="ergonomics")
#         st.button("Visual analysis", key="visual_analysis")
#         if st.button("Alerts", key="alerts"):
#             st.session_state.show_alerts = True
#         else:
#             st.session_state.show_alerts = False

# # Función para crear la barra de navegación superior
# def top_navigation():
#     col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
#     with col1:
#         st.button("Overview")
#     with col2:
#         if st.button("Alerts"):
#             st.session_state.show_alerts = True
#     with col3:
#         st.button("Compliance")
#     with col4:
#         st.download_button("Save as PDF", "data", file_name="report.pdf")

# # Función para crear los filtros
# def filters():
#     col1, col2, col3, col4, col5 = st.columns(5)
#     with col1:
#         st.selectbox("Facility", ["All facilities"])
#     with col2:
#         st.selectbox("Section", ["All sections"])
#     with col3:
#         st.selectbox("Camera", ["All cameras"])
#     with col4:
#         st.selectbox("Type", ["All types"])
#     with col5:
#         st.date_input("Date Range", [datetime.now() - timedelta(days=7), datetime.now()])

# # Función para crear el gráfico circular
# def category_distribution():
#     data = {
#         'Category': ['Area controls', 'Behavior', 'Housekeeping', 'Pandemic', 'PPE', 'Vehicle'],
#         'Value': [10, 20, 15, 5, 30, 20]
#     }
#     fig = px.pie(data, values='Value', names='Category', title='Category distribution')
#     fig.update_traces(textposition='inside', textinfo='percent+label')
#     fig.update_layout(
#         showlegend=False,
#         margin=dict(l=20, r=20, t=40, b=20),
#     )
#     st.plotly_chart(fig, use_container_width=True)

# # Función para crear el gráfico de líneas
# def alert_count():
#     data = {
#         'Date': ['Jul 2', 'Jul 3', 'Jul 4', 'Jul 5', 'Jul 6', 'Jul 7', 'Jul 8'],
#         'Area controls': [3, 4, 2, 3, 2, 5, 4],
#         'Behavior': [20, 30, 34, 33, 28, 29, 34],
#         'Housekeeping': [1, 2, 3, 2, 1, 2, 3],
#         'Pandemic': [2, 3, 2, 1, 2, 1, 2],
#         'PPE': [50, 55, 51, 57, 61, 56, 64],
#         'Vehicle': [40, 45, 43, 44, 47, 45, 46]
#     }
#     df = pd.DataFrame(data)
#     fig = go.Figure()
#     for column in df.columns[1:]:
#         fig.add_trace(go.Scatter(x=df['Date'], y=df[column], mode='lines', name=column))
#     fig.update_layout(
#         title='Alert count per category',
#         xaxis_title='Date',
#         yaxis_title='Count',
#         legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
#         margin=dict(l=20, r=20, t=60, b=20),
#     )
#     st.plotly_chart(fig, use_container_width=True)

# # Función para mostrar la imagen y la información
# def show_image_and_info(index, filenames):
#     if 0 <= index < len(filenames):
#         st.session_state.current_image_index = index
#         image_key = filenames[index]
        
#         try:
#             response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=image_key)
#             image_data = response['Body'].read()
#             image = Image.open(BytesIO(image_data))
#             st.image(image, caption=os.path.basename(image_key), use_column_width=True)
#         except Exception as e:
#             st.error(f"Error al cargar la imagen: {str(e)}")

# # Función para mostrar la sección de alertas
# def show_alerts_section():
#     st.header("Alertas")

#     # Cargar los datos
#     detections = load_data(S3_FOLDER)

#     # Calcular el rango de tiempo por defecto (últimas 3 horas)
#     end_time = detections[-1][0] if detections else datetime.now()
#     start_time = end_time - timedelta(hours=3)

#     # Filtros para las alertas
#     date_range = st.date_input("Rango de fechas para alertas", 
#                                [start_time.date(), end_time.date()])
#     time_range = st.slider(
#         "Rango de horas para alertas",
#         min_value=datetime.min.time(),
#         max_value=datetime.max.time(),
#         value=(start_time.time(), end_time.time())
#     )

#     # Filtrar los datos según los filtros seleccionados
#     filtered_detections = [
#         d for d in detections 
#         if date_range[0] <= d[0].date() <= date_range[1] and
#         time_range[0] <= d[0].time() <= time_range[1]
#     ]

#     # Mostrar imágenes de alertas
#     if filtered_detections:
#         filenames = [d[3] for d in filtered_detections]
#         selected_index = st.slider("Desliza para ver imágenes de alertas", 
#                                    min_value=0, 
#                                    max_value=len(filenames)-1, 
#                                    value=0, 
#                                    step=1)
#         show_image_and_info(selected_index, filenames)
#     else:
#         st.info("No se encontraron alertas en el rango de tiempo seleccionado.")

# # Función principal
# def main():
#     sidebar()
#     top_navigation()
    
#     if st.session_state.get('show_alerts', False):
#         show_alerts_section()
#     else:
#         filters()
#         col1, col2 = st.columns(2)
#         with col1:
#             category_distribution()
#         with col2:
#             alert_count()

# if __name__ == "__main__":
#     main()


import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import boto3
from io import BytesIO
from PIL import Image
import os
import re
from collections import defaultdict

# Configuración de la página
st.set_page_config(page_title="AZ/AI Demo", layout="wide")

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
    </style>
    """, unsafe_allow_html=True)

# AWS S3 configuration
S3_BUCKET_NAME = "trialbucket-cv"
S3_FOLDER = "person_count_output/"

# Initialize S3 client
s3_client = boto3.client('s3')

# Function to list objects in S3 bucket
def list_s3_objects(bucket, prefix):
    paginator = s3_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket, Prefix=prefix)
    
    for page in pages:
        for obj in page.get('Contents', []):
            yield obj['Key']

# Función para cargar y procesar los datos
@st.cache_data
def load_data(s3_folder):
    pattern = r"Zone_(\d+)_person_(\d+)_(\d{8})_(\d{6})"
    detections = []
    
    for key in list_s3_objects(S3_BUCKET_NAME, s3_folder):
        filename = os.path.basename(key)
        match = re.match(pattern, filename)
        if match:
            zone, person_id, date, time = match.groups()
            timestamp = datetime.strptime(f"{date}_{time}", "%Y%m%d_%H%M%S")
            detections.append((timestamp, int(zone), int(person_id), key))
    
    detections.sort()  # Ordenar de más antiguo a más reciente
    return detections

# Función para crear la barra lateral
def sidebar():
    with st.sidebar:
        st.markdown("# 👁️ AZ/AI")
        st.title("Demo")
        if st.button("Control room", key="control_room"):
            st.session_state.current_page = "control_room"
        if st.button("Ergonomics", key="ergonomics"):
            st.session_state.current_page = "ergonomics"
        if st.button("Visual analysis", key="visual_analysis"):
            st.session_state.current_page = "visual_analysis"
        if st.button("Alerts", key="alerts", type="primary" if st.session_state.current_page == "alerts" else "secondary"):
            st.session_state.current_page = "alerts"

# Función para crear la barra de navegación superior
def top_navigation():
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    with col1:
        if st.button("Overview"):
            st.session_state.current_page = "overview"
    with col2:
        if st.button("Alerts", type="primary" if st.session_state.current_page == "alerts" else "secondary"):
            st.session_state.current_page = "alerts"
    with col3:
        st.button("Compliance")
    with col4:
        st.download_button("Save as PDF", "data", file_name="report.pdf")

# Función para crear los filtros
def filters():
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.selectbox("Facility", ["All facilities"])
    with col2:
        st.selectbox("Section", ["All sections"])
    with col3:
        st.selectbox("Camera", ["All cameras"])
    with col4:
        st.selectbox("Type", ["All types"])
    with col5:
        st.date_input("Date Range", [datetime.now() - timedelta(days=7), datetime.now()])

# Función para crear el gráfico circular
def category_distribution():
    data = {
        'Category': ['Area controls', 'Behavior', 'Housekeeping', 'Pandemic', 'PPE', 'Vehicle'],
        'Value': [10, 20, 15, 5, 30, 20]
    }
    fig = px.pie(data, values='Value', names='Category', title='Category distribution')
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

# Función para crear el gráfico de líneas
def alert_count():
    data = {
        'Date': ['Jul 2', 'Jul 3', 'Jul 4', 'Jul 5', 'Jul 6', 'Jul 7', 'Jul 8'],
        'Area controls': [3, 4, 2, 3, 2, 5, 4],
        'Behavior': [20, 30, 34, 33, 28, 29, 34],
        'Housekeeping': [1, 2, 3, 2, 1, 2, 3],
        'Pandemic': [2, 3, 2, 1, 2, 1, 2],
        'PPE': [50, 55, 51, 57, 61, 56, 64],
        'Vehicle': [40, 45, 43, 44, 47, 45, 46]
    }
    df = pd.DataFrame(data)
    fig = go.Figure()
    for column in df.columns[1:]:
        fig.add_trace(go.Scatter(x=df['Date'], y=df[column], mode='lines', name=column))
    fig.update_layout(
        title='Alert count per category',
        xaxis_title='Date',
        yaxis_title='Count',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=60, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

# Función para mostrar la imagen y la información
def show_image_and_info(index, filenames):
    if 0 <= index < len(filenames):
        image_key = filenames[index]
        
        try:
            response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=image_key)
            image_data = response['Body'].read()
            image = Image.open(BytesIO(image_data))
            st.image(image, caption=os.path.basename(image_key), use_column_width=True)
        except Exception as e:
            st.error(f"Error al cargar la imagen: {str(e)}")

# Función para mostrar la sección de alertas
def show_alerts_section():
    st.header("Alertas")

    # Cargar los datos
    detections = load_data(S3_FOLDER)

    # Calcular el rango de tiempo por defecto (últimas 3 horas)
    end_time = detections[-1][0] if detections else datetime.now()
    start_time = end_time - timedelta(hours=3)

    # Filtros para las alertas
    date_range = st.date_input("Rango de fechas para alertas", 
                               [start_time.date(), end_time.date()],
                               key="alert_date_range")
    time_range = st.slider(
        "Rango de horas para alertas",
        min_value=datetime.min.time(),
        max_value=datetime.max.time(),
        value=(start_time.time(), end_time.time()),
        key="alert_time_range"
    )

    # Filtrar los datos según los filtros seleccionados
    filtered_detections = [
        d for d in detections 
        if date_range[0] <= d[0].date() <= date_range[1] and
        time_range[0] <= d[0].time() <= time_range[1]
    ]

    # Mostrar imágenes de alertas
    if filtered_detections:
        filenames = [d[3] for d in filtered_detections]
        
        # Initialize current_index in session_state if it doesn't exist
        if 'current_index' not in st.session_state:
            st.session_state.current_index = 0

        # Display navigation buttons
        col1, col2, col3 = st.columns([1,3,1])
        with col1:
            if st.button("⬅️ Anterior", key="prev_button"):
                st.session_state.current_index = max(0, st.session_state.current_index - 1)
                st.experimental_rerun()
        with col3:
            if st.button("Siguiente ➡️", key="next_button"):
                st.session_state.current_index = min(len(filenames) - 1, st.session_state.current_index + 1)
                st.experimental_rerun()
        
        # Display current image
        show_image_and_info(st.session_state.current_index, filenames)
        
        # Display image information
        st.write(f"Imagen {st.session_state.current_index + 1} de {len(filenames)}")
    else:
        st.info("No se encontraron alertas en el rango de tiempo seleccionado.")

# Función principal
def main():
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "overview"

    sidebar()
    top_navigation()
    
    if st.session_state.current_page == "alerts":
        show_alerts_section()
    else:
        filters()
        col1, col2 = st.columns(2)
        with col1:
            category_distribution()
        with col2:
            alert_count()

if __name__ == "__main__":
    main()
