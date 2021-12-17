from bokeh.colors import RGB
from bokeh.embed import file_html
from bokeh.models import HoverTool, LinearColorMapper, ColorBar, WheelZoomTool
from bokeh.plotting import figure
from bokeh.palettes import Set2
from bokeh.transform import linear_cmap
from bokeh.resources import CDN
from bokeh import tile_providers as tp
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st


DEFAULT_COLOR = "#CB2649"
AVAILABLE_MAPBOX_STYLES = {
    "open-street-map": tp.OSM,
    "carto-positron": tp.CARTODBPOSITRON,
    "stamen-terrain": tp.STAMEN_TERRAIN,
    "stamen-toner": tp.STAMEN_TONER,
    "wikimedia": tp.WIKIMEDIA,
    "esri": tp.ESRI_IMAGERY,
}
AVAILABLE_CONTINUOUS_COLOR_SCALES = ["jet", "coolwarm", "RdYlGn", "jet_r", "coolwarm_r"]
MARKER_SINGLE_SIZE_DEFAULT_VALUE = 10
MARKERS_MIN_SIZE, MARKERS_MAX_SIZE = 1, 50
MARKER_SINGLE_SIZE_DEFAULT_LOW_VALUE, MARKER_SINGLE_SIZE_DEFAULT_HIGH_VALUE = 5, 15
MARKER_MIN_OPACITY = 0.0
MARKER_MAX_OPACITY = 1.0
MARKERS_LINE_MIN_WIDTH, MARKERS_LINE_MAX_WIDTH = 0, 5
MARKERS_LINE_MIN_OPACITY, MARKERS_LINE_MAX_OPACITY = 0.0, 1.0
MARKERS_LINE_OPACITY_DEFAULT_VALUE = 0.5
MARKER_OPACITY_DEFAULT_VALUE = 0.5
MARKER_OPACITY_DEFAULT_STEP = 0.01
MARKERS_LINE_OPACITY_DEFAULT_STEP = 0.01

MAX_DISPLAYED_DISTINCT_SCATTER_TYPES = 10

EARTH_RADIUS_METERS = 6378137


st.set_page_config(page_title="Plot Map", layout="wide")

uploaded_file = st.sidebar.file_uploader("Quel fichier traiter?", type=["csv", "xlsx"])

if uploaded_file is not None:
    # -----------------------------------------------------------------------------------------------------------------
    # Read file

    if uploaded_file.type == "text/csv":
        df = pd.read_csv(uploaded_file)

    else:
        df = pd.read_excel(uploaded_file)

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

        color_scale_column = st.sidebar.selectbox(
            label="Quelle colonne utiliser pour la couleur?", options=list(df.columns)
        )

        color_scale_column_is_numeric = np.issubdtype(
            df[color_scale_column].dtype, np.number
        )

        if color_scale_column_is_numeric:
            color_scale = st.sidebar.selectbox(
                label="Quel choix de palette de couleurs?",
                options=AVAILABLE_CONTINUOUS_COLOR_SCALES,
            )
            color_value_range = st.sidebar.slider(
                label="Intervalle des valeurs de couleur",
                min_value=float(df[color_scale_column].min()),
                max_value=float(df[color_scale_column].max()),
                value=(
                    float(df[color_scale_column].min()),
                    float(df[color_scale_column].max()),
                ),
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
    # Scatter line settings
    st.sidebar.header("Contour des points")

    scatter_line = st.sidebar.checkbox("Ajouter un contour aux points", value=False)

    if scatter_line:
        is_specific_scatter_line_color = st.sidebar.checkbox(
            "Contour de couleur différente des points ?", value=False
        )

        if is_specific_scatter_line_color:
            specific_scatter_line_color = st.sidebar.color_picker(
                "Quel couleur pour le contour des points?", value="#FFFFFF"
            )

        scatter_line_width = st.sidebar.slider(
            label="Taille du countour",
            min_value=MARKERS_LINE_MIN_WIDTH,
            max_value=MARKERS_LINE_MAX_WIDTH,
            value=MARKERS_LINE_MIN_WIDTH,
            step=1,
            format="%g",
        )

        scatter_line_opacity = st.sidebar.slider(
            label="Opacité du countour",
            min_value=MARKERS_LINE_MIN_OPACITY,
            max_value=MARKERS_LINE_MAX_OPACITY,
            value=MARKERS_LINE_OPACITY_DEFAULT_VALUE,
            step=MARKERS_LINE_OPACITY_DEFAULT_STEP,
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
        label="Quelle fond de carte utiliser?", options=AVAILABLE_MAPBOX_STYLES.keys()
    )

    # -----------------------------------------------------------------------------------------------------------------
    # Add parameters to displayer df

    df_to_disp = df.copy()

    # MArcator projection
    df_to_disp["x"] = df_to_disp[longitude_column] * (
        EARTH_RADIUS_METERS * np.pi / 180.0
    )
    df_to_disp["y"] = (
        np.log(np.tan((90 + df[latitude_column]) * np.pi / 360.0)) * EARTH_RADIUS_METERS
    )

    # -----------------------------------------------------------------------------------------------------------------
    # Create map parameters

    map_parameters = {}

    map_parameters["x"] = "x"
    map_parameters["y"] = "y"

    map_parameters["size"] = "marker_size"

    map_parameters["source"] = df_to_disp

    map_parameters["alpha"] = color_opacity

    if scatter_line:

        if is_specific_scatter_line_color:
            map_parameters["line_color"] = specific_scatter_line_color

        map_parameters["line_width"] = scatter_line_width
        map_parameters["line_alpha"] = scatter_line_opacity

    else:
        map_parameters["line_alpha"] = 0

    if size_strategy == "Unique":
        map_parameters["size"] = single_size_marker

    else:
        df_to_disp["marker_size"] = (
            df_to_disp[variable_size_column] - df_to_disp[variable_size_column].min()
        ) / (
            df_to_disp[variable_size_column].max()
            - df_to_disp[variable_size_column].min()
        ) * (
            variable_size_marker[1] - variable_size_marker[0]
        ) + variable_size_marker[
            0
        ]
        map_parameters["size"] = "marker_size"

    # -----------------------------------------------------------------------------------------------------------------
    # Create map

    for col in selected_hover_columns:
        df_to_disp["_" + col] = df_to_disp[col].astype("str")

    if color_strategy == "Variable" and color_scale_column_is_numeric:

        processed_color_scale_column = "_" + color_scale_column
        df_to_disp[processed_color_scale_column] = df_to_disp[color_scale_column].clip(
            lower=color_value_range[0], upper=color_value_range[1]
        )

    fig_map = figure(
        x_axis_type="mercator",
        y_axis_type="mercator",
        sizing_mode="stretch_both",
    )

    tile_provider = tp.get_provider(AVAILABLE_MAPBOX_STYLES[selected_mapbox_style])
    fig_map.add_tile(tile_provider)

    if color_strategy == "Unique":
        map_parameters["color"] = single_color

        fig_map.circle(**map_parameters)

    else:
        if color_scale_column_is_numeric:

            color_palette = (255 * plt.get_cmap(color_scale)(range(256))).astype("int")
            color_palette = [RGB(*tuple(rgb)).to_hex() for rgb in color_palette]

            linear_cmapper = linear_cmap(
                field_name=processed_color_scale_column,
                palette=color_palette,
                low=df_to_disp[processed_color_scale_column].min(),
                high=df_to_disp[processed_color_scale_column].max(),
            )

            color_mapper = LinearColorMapper(
                palette=color_palette,
                low=df_to_disp[processed_color_scale_column].min(),
                high=df_to_disp[processed_color_scale_column].max(),
            )

            map_parameters["color"] = linear_cmapper
            map_parameters["source"] = df_to_disp

            fig_map.circle(**map_parameters)

            fig_map.add_layout(
                ColorBar(color_mapper=color_mapper, title=color_scale_column), "right"
            )

        else:
            for i, col_value in enumerate(df_to_disp[color_scale_column].unique()):

                map_parameters["legend_label"] = str(col_value)
                map_parameters["color"] = Set2[8][i % 8]
                map_parameters["source"] = df_to_disp[
                    df_to_disp[color_scale_column] == col_value
                ]

                fig_map.circle(**map_parameters)

                if i >= MAX_DISPLAYED_DISTINCT_SCATTER_TYPES:
                    break

            fig_map.legend.click_policy = "hide"

    tt = [(col, "@{_" + str(col) + "}") for col in selected_hover_columns]
    fig_map.add_tools(HoverTool(tooltips=tt))

    fig_map.xgrid.grid_line_color = None
    fig_map.ygrid.grid_line_color = None

    fig_map.toolbar.active_scroll = fig_map.select_one(WheelZoomTool)

    # -----------------------------------------------------------------------------------------------------------------
    # Display map

    # st.set_page_config(layout="wide")
    st.bokeh_chart(fig_map, use_container_width=True)

    # -----------------------------------------------------------------------------------------------------------------
    # Download button

    st.sidebar.header("Téléchargement")

    st.sidebar.download_button(
        "Télécharger la carte",
        data=file_html(fig_map, CDN, "Map"),
        file_name="personalized_map.html",
        help="Fichier interactif au format html",
    )
