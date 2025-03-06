import dash
from dash import dcc, html, callback, Output, Input, State, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import zipfile
from io import BytesIO
from . import utils

pooled_df_joint_metadata = pd.read_csv("metadata/pooled_df_joint_metadata.csv")
projects, cs, species, concentrations = utils.load_dropdown_data(
    pooled_df_joint_metadata
)

loaded_data = []
loaded_metadata = []
# Dash layout
dash.register_page(__name__, path="/", name="Home", order=1)  # '/' is home page

layout = html.Div(
    [
        dbc.Row(html.H2("Data viewer"), class_name="pb-2"),
        dbc.Col(
            [
                dbc.Row(
                    html.Span("Select projects and conditions:"),
                    class_name="pb-1",
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
                dbc.Row(
                    dcc.Dropdown(
                        options=concentrations,
                        placeholder="Select concentration",
                        id="concentration-dropdown",
                        multi=True,
                    ),
                ),
            ],
            width=6,
        ),
        dbc.Col(
            [
                dbc.Row(html.H6("Color graph by:"), class_name="pt-4"),
                dbc.Row(
                    dcc.Dropdown(
                        options=["Carbon Source", "Species"],
                        value="Carbon Source",
                        id="color-by",
                    ),
                    class_name="pt-1",
                ),
                dbc.Row(
                    dbc.Checklist(
                        options={"label": " Plot replicates"}, id="plot-replicates"
                    ),
                    class_name="pt-1",
                ),
                dbc.Row(
                    dbc.RadioItems(
                        options=[
                            {"label": "Linear y-axis", "value": "linear-scale"},
                            {"label": "Log-scale y-axis", "value": "log-scale"},
                        ],
                        value="linear-scale",
                        id="plot-type",
                    ),
                    class_name="pt-1",
                ),
            ],
            width=3,
        ),
        dbc.Col(
            dcc.Graph(
                figure={},
                id="controls-and-graph",
            ),
            width=11,
            class_name="pb-3",
        ),
        dbc.Col(
            html.Details(
                [
                    html.Summary(html.Span("Project description")),
                    html.Span(
                        children=[""],
                        id="project-description",
                    ),
                ],
            ),
            class_name="pb-1",
            width=11,
        ),
        dbc.Col(
            html.Details(
                [
                    html.Summary(html.Span("Experiment description")),
                    html.Span(
                        children=[""],
                        id="experiment-description",
                    ),
                ],
            ),
            class_name="pb-1",
            width=11,
        ),
        dbc.Col(
            html.Details(
                [
                    html.Summary(html.Span("Metadata")),
                    html.Span(
                        children=[""],
                        id="metadata-table",
                    ),
                ],
            ),
            width=11,
        ),
        dbc.Col(
            [
                dbc.Button("Download Data", id="download-btn"),
                dcc.Download(id="download-data"),
            ],
            class_name="pt-3 pb-4",
            width="auto",
        ),
    ]
)


# Callback for plotting the selected data
@callback(
    [
        Output(component_id="controls-and-graph", component_property="figure"),
        Output(component_id="metadata-table", component_property="children"),
        Output(component_id="project-description", component_property="children"),
        Output(component_id="experiment-description", component_property="children"),
    ],
    [
        Input(component_id="proj-dropdown", component_property="value"),
        Input("cs-dropdown", "value"),
        Input("species-dropdown", "value"),
        Input("color-by", "value"),
        Input("plot-replicates", "value"),
        Input("plot-type", "value"),
    ],
)
def update_graph_view(
    proj_chosen,
    chosen_carbon_sources,
    chosen_species,
    color_by,
    plot_replicates,
    plot_type,
):
    fig_layout = go.Layout(
        margin=dict(l=0, r=50, t=50, b=10),
        xaxis=dict(title="Time [h]"),
        yaxis=dict(title="OD"),
    )
    parsed_data_dir = "export"
    if (
        proj_chosen == "Select Project"
        or proj_chosen == None
        or chosen_carbon_sources == "Select Carbon Source"
        or chosen_carbon_sources == None
        or chosen_species == "Select Species"
        or chosen_species == None
        or chosen_concentration == None
    ):
        fig = go.Figure(layout=fig_layout)
        return fig, [], "", ""

    args = (
        projects[1:],
        species,
        cs,
        concentrations,
        pooled_df_joint_metadata,
        parsed_data_dir,
    )
    filtered_metadata = utils.load_selected_metadata(
        proj_chosen, chosen_carbon_sources, chosen_species, chosen_concentration, args
    )
    if len(filtered_metadata) == 0:
        fig = go.Figure(layout=fig_layout)
        return fig, [], "", ""

    df_merged = utils.load_data_from_metadata(filtered_metadata, args)

    global loaded_data
    loaded_data = df_merged.copy()
    global loaded_metadata
    loaded_metadata = filtered_metadata.copy()

    fig = utils.plot_data(
        df_merged, filtered_metadata, color_by, plot_replicates, plot_type, fig_layout
    )
    table_df = utils.show_table(filtered_metadata)

    return (
        fig,
        table_df,
        utils.show_project_descriptions(filtered_metadata),
        utils.show_experiment_descriptions(filtered_metadata),
    )


# Callback for updating the dropdowns in the View Data tab
@callback(
    [Output(component_id="cs-dropdown", component_property="options")],
    [Output(component_id="species-dropdown", component_property="options")],
    [Output(component_id="concentration-dropdown", component_property="options")],
    [
        Input("proj-dropdown", "value"),
    ],
)
def update_dropwdown(chosen_project):
    df = pooled_df_joint_metadata
    if chosen_project is None:
        return (
            sorted(list(set(df["carbon_source"]))),
            sorted(list(set(df["species"]))),
            sorted(list(set(df["cs_conc"]))),
        )
    if len(chosen_project) == 0:
        return (
            sorted(list(set(df["carbon_source"]))),
            sorted(list(set(df["species"]))),
            sorted(list(set(df["cs_conc"]))),
        )
    elif "All" in chosen_project:
        return (
            sorted(list(set(df["carbon_source"]))),
            sorted(list(set(df["species"]))),
            sorted(list(set(df["cs_conc"]))),
        )
    else:
        df = df[df["project"].isin(chosen_project)]
        return sorted(list(set(df["carbon_source"]))), sorted(list(set(df["species"])))


# Callback for downloading the data
@callback(
    Output("download-data", "data"),
    Input("download-btn", "n_clicks"),
    prevent_initial_call=True,
)
def download_data(n_clicks):
    if n_clicks is None:
        return dash.no_update

    df_measurements = loaded_data.copy()
    filter_metadata = loaded_metadata.copy()

    df_export = utils.export_restructuring(df_measurements, filter_metadata)

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("metadata.csv", filter_metadata.to_csv(index=False))
        zf.writestr("measurements.csv", df_export.to_csv())

    zip_buffer.seek(0)
    return dcc.send_bytes(zip_buffer.getvalue(), "downloaded_data.zip")
