import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


DEFAULT_COLOR = "#CB2649"
AVAILABLE_MAPBOX_STYLES = [
    "open-street-map",
    "carto-positron",
    "carto-darkmatter",
    "stamen- terrain",
    "stamen-toner",
    "stamen-watercolor",
]
AVAILABLE_COLOR_SCALES = ["Turbo", "RdBu", "Mint", "BlackBody"]
MARKER_SINGLE_SIZE_DEFAULT_VALUE = 10
MARKERS_MIN_SIZE, MARKERS_MAX_SIZE = 1, 50
MARKER_SINGLE_SIZE_DEFAULT_LOW_VALUE, MARKER_SINGLE_SIZE_DEFAULT_HIGH_VALUE = 5, 15
MAP_DEFAULT_WIDTH, MAP_DEFAULT_HEIGHT = 900, 900
DEFAULT_ZOOM_MARGIN = 1.2
MARKER_MIN_OPACITY = 0.0
MARKER_MAX_OPACITY = 1.0
MARKER_OPACITY_DEFAULT_VALUE = 0.5
MARKER_OPACITY_DEFAULT_STEP = 0.01

st.set_page_config(page_title="Plot Map", layout="wide")

uploaded_file = st.sidebar.file_uploader("Quel fichier traiter?")

if uploaded_file is not None:
    # -----------------------------------------------------------------------------------------------------------------
    # Read csv
    df = pd.read_csv(uploaded_file)

    # -----------------------------------------------------------------------------------------------------------------
    # Color settings
    st.sidebar.header("Couleurs")

    color_strategy = st.sidebar.radio(
        label="Couleur unique ou variable?", options=("Unique", "Variable")
    )

    if color_strategy == "Unique":
        single_color = st.sidebar.color_picker(
            "Couleur à afficher:", value=DEFAULT_COLOR
        )

    else:
        color_scale = st.sidebar.selectbox(
            label="Quel choix de palette de couleurs?",
            options=AVAILABLE_COLOR_SCALES,
        )

        color_scale_column = st.sidebar.selectbox(
            label="Quelle colonne utiliser pour la couleur?", options=list(df.columns)
        )

    color_opacity = st.sidebar.slider(
        label="Opacité",
        min_value=MARKER_MIN_OPACITY,
        max_value=MARKER_MAX_OPACITY,
        value=MARKER_OPACITY_DEFAULT_VALUE,
        step=MARKER_OPACITY_DEFAULT_STEP,
    )

    # -----------------------------------------------------------------------------------------------------------------
    # Size settings
    st.sidebar.header("Taille des elements")

    size_strategy = st.sidebar.radio(
        label="Taille unique ou variable?", options=("Unique", "Variable")
    )

    if size_strategy == "Unique":
        single_size_marker = st.sidebar.slider(
            label="Taille des points",
            min_value=MARKERS_MIN_SIZE,
            max_value=MARKERS_MAX_SIZE,
            value=MARKER_SINGLE_SIZE_DEFAULT_VALUE,
            step=1,
            format="%g",
        )

    else:
        variable_size_marker = st.sidebar.slider(
            label="Taille des points",
            min_value=MARKERS_MIN_SIZE,
            max_value=MARKERS_MAX_SIZE,
            value=(
                MARKER_SINGLE_SIZE_DEFAULT_LOW_VALUE,
                MARKER_SINGLE_SIZE_DEFAULT_HIGH_VALUE,
            ),
            step=1,
            format="%g",
        )

        variable_size_column = st.sidebar.selectbox(
            label="Quelle colonne utiliser pour la taille?", options=list(df.columns)
        )

    # -----------------------------------------------------------------------------------------------------------------
    # Displayed columns on hover
    st.sidebar.header("Données à afficher")

    selected_hover_columns = st.sidebar.multiselect(
        "Quelles données afficher au passage de la souris",
        list(df.columns),
        list(df.columns),
    )

    # -----------------------------------------------------------------------------------------------------------------
    # Columns for latitude / longitude
    st.sidebar.header("Colonnes pour la latitude et la longitude")

    # Preselect latitude and longitude columns
    latitude_default_index = 0
    longitude_default_index = 0

    for index, col in enumerate(df.columns):
        if "lat" in col:
            latitude_default_index = index

    for index, col in enumerate(df.columns):
        if ("lon" in col) or ("lng" in col):
            longitude_default_index = index

    # Ask laittude and longitude columns values in case the default method doesn't work
    latitude_column = st.sidebar.selectbox(
        label="Quelle colonne utiliser pour la latitude?",
        options=list(df.columns),
        index=latitude_default_index,
    )
    longitude_column = st.sidebar.selectbox(
        label="Quelle colonne utiliser pour la longitude?",
        options=list(df.columns),
        index=longitude_default_index,
    )

    # -----------------------------------------------------------------------------------------------------------------
    # Map style
    st.sidebar.header("Fond carte")

    selected_mapbox_style = st.sidebar.selectbox(
        label="Quelle fond de carte utiliser?", options=AVAILABLE_MAPBOX_STYLES
    )

    # -----------------------------------------------------------------------------------------------------------------
    # Create map parameters

    map_parameters = {}

    map_parameters["lat"] = latitude_column
    map_parameters["lon"] = longitude_column

    map_parameters["hover_data"] = selected_hover_columns

    map_parameters["mapbox_style"] = selected_mapbox_style

    map_parameters["data_frame"] = df

    map_parameters["width"] = MAP_DEFAULT_WIDTH
    map_parameters["height"] = MAP_DEFAULT_HEIGHT

    map_parameters["opacity"] = color_opacity

    if color_strategy == "Variable":
        map_parameters["color"] = color_scale_column
        map_parameters["color_continuous_scale"] = color_scale

    # Set zoom level not handled by default,
    # See https://stackoverflow.com/questions/63787612/plotly-automatic-zooming-for-mapbox-maps
    map_center = {"lat": df[latitude_column].mean(), "lon": df[longitude_column].mean()}

    delta_latitude = (
        (df[latitude_column].max() - df[latitude_column].min())
        * DEFAULT_ZOOM_MARGIN
        * 2
    )
    delta_longitude = (
        df[longitude_column].max() - df[longitude_column].min()
    ) * DEFAULT_ZOOM_MARGIN

    latitude_zoom = 20 - np.log(delta_latitude / (360 / 2 ** 19)) / np.log(2)
    longitude_zoom = 20 - np.log(delta_longitude / (360 / 2 ** 19)) / np.log(2)

    map_parameters["center"] = map_center
    map_parameters["zoom"] = min(latitude_zoom, longitude_zoom)

    # -----------------------------------------------------------------------------------------------------------------
    # Create map

    fig_map = px.scatter_mapbox(**map_parameters)

    # -----------------------------------------------------------------------------------------------------------------
    # More parameters update

    # Color
    if color_strategy == "Unique":
        fig_map.update_traces(marker=dict(color=single_color))

    # Size
    if size_strategy == "Unique":
        markers_size = [single_size_marker for i in range(len(df))]

    else:
        markers_size = (df[variable_size_column] - df[variable_size_column].min()) / (
            df[variable_size_column].max() - df[variable_size_column].min()
        ) * (variable_size_marker[1] - variable_size_marker[0]) + variable_size_marker[
            0
        ]

    fig_map.update_traces(marker=dict(size=markers_size))

    # -----------------------------------------------------------------------------------------------------------------
    # Display map

    # st.set_page_config(layout="wide")
    st.plotly_chart(fig_map, use_container_width=True)
