import dash
from dash import dcc, html, callback, Output, Input, State, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import zipfile
from io import BytesIO
from . import utils
from . import fitting_utils


# Dash layout
dash.register_page(
    __name__, path="/Fitting", name="Fitting", order=2
)  # '/' is home page

pooled_df_joint_metadata = pd.read_csv("metadata/pooled_df_joint_metadata.csv")
projects, cs, species = utils.load_dropdown_data(pooled_df_joint_metadata)


layout = html.Div(
    [
        dbc.Col(
            [
                dbc.Row(
                    html.Span("Select projects and conditions:"), class_name="pb-1"
                ),
                dbc.Row(
                    dcc.Dropdown(
                        options=projects,
                        placeholder="Select Project",
                        id="proj-dropdown",
                        multi=True,
                    ),
                    class_name="pb-1",
                ),
                dbc.Row(
                    dcc.Dropdown(
                        options=cs,
                        placeholder="Select Carbon Source",
                        id="cs-dropdown",
                        multi=True,
                    ),
                    class_name="pb-1",
                ),
                dbc.Row(
                    dcc.Dropdown(
                        options=species,
                        placeholder="Select Species",
                        id="species-dropdown",
                        multi=True,
                    ),
                    class_name="pb-1",
                ),
            ],
            width=6,
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Button("Fit Parameters", id="fitting-button"),
                    ],
                    width="auto",
                    class_name="pt-3",
                ),
            ]
        ),
        dbc.Col(
            dbc.Row(
                dbc.Collapse(
                    id="parameters-table",
                    class_name="data-table",
                    is_open=False,
                    children=[],
                ),
                class_name="pt-3",
            ),
            width=12,
        ),
    ]
)


# Callback for fitting
@callback(
    [
        Output(component_id="parameters-table", component_property="children"),
        Output(component_id="parameters-table", component_property="is_open"),
    ],
    [
        State(component_id="proj-dropdown", component_property="value"),
        State(component_id="cs-dropdown", component_property="value"),
        State(component_id="species-dropdown", component_property="value"),
        Input("fitting-button", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def fit_parameters(chosen_projects, chosen_carbon_sources, chosen_species, nclicks):
    if nclicks == 0 or nclicks is None:
        return no_update, False
    if (
        chosen_projects == "Select Project"
        or chosen_projects == None
        or chosen_carbon_sources == "Select Carbon Source"
        or chosen_carbon_sources == None
        or chosen_species == "Select Species"
        or chosen_species == None
    ):
        return no_update, False

    args = projects[1:], species, cs, pooled_df_joint_metadata, "export"
    filtered_metadata = utils.load_selected_metadata(
        chosen_projects, chosen_carbon_sources, chosen_species, args
    )
    if len(filtered_metadata) == 0:
        return dbc.Alert(
            "No data found for the selected conditions", color="warning"
        ), True

    parsed_data_dir = "export"
    df_merged = utils.load_data_from_metadata(filtered_metadata, args)

    df_restructured = utils.export_restructuring(df_merged, filtered_metadata)
    parameters_table = fitting_utils.table_generator(df_restructured, filtered_metadata)

    return parameters_table, True
