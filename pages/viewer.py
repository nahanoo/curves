import dash
from dash import dcc, html, callback, Output, Input, State,no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import zipfile
from io import BytesIO
from . import utils

pooled_df_joint_metadata = pd.read_csv("metadata/pooled_df_joint_metadata.csv")
projects, cs, species = utils.load_dropdown_data(pooled_df_joint_metadata)

loaded_data = []
loaded_metadata = []

# Dash layout
dash.register_page(__name__, path="/", name="Home")  # '/' is home page

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
        dbc.Col(
            [
                dbc.Row(html.Span("Color graph by:"), class_name="pt-4"),
                dbc.Row(
                    dcc.Dropdown(
                        options=["Carbon Source", "Species"],
                        value="Carbon Source",
                        id="color-by",
                    ),
                    class_name="pt-1",
                ),
                dbc.Row(
                    dcc.Checklist([" Plot replicates"], id="plot-replicates"),
                    class_name="pt-1",
                ),
            ],
            width=3,
        ),
        dbc.Col(
            dbc.Row(
                [
                    dcc.Graph(
                        figure={},
                        id="controls-and-graph",
                    ),
                ]
            ),
            class_name="",
            width=10,
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Button(
                        children=["Show meta data"],
                        id="collapse-button",
                        n_clicks=0,
                        disabled=True,
                    ),
                    width="auto",
                    class_name="pt-3",
                ),
                dbc.Col(
                    [
                        dbc.Button("Download Data", id="download-btn"),
                        dcc.Download(id="download-data"),
                    ],
                    width="auto",
                    class_name="pt-3",
                ),
            ]
        ),
        dbc.Col(
            dbc.Row(
                dbc.Collapse(
                    id="collapse-table",
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


# Callback for plotting the selected data
@callback(
    [
        Output(component_id="controls-and-graph", component_property="figure"),
        Output(component_id="collapse-table", component_property="children"),
        Output(component_id="collapse-button", component_property="disabled"),
    ],
    [
        Input(component_id="proj-dropdown", component_property="value"),
        Input("cs-dropdown", "value"),
        Input("species-dropdown", "value"),
        Input("color-by", "value"),
        Input("plot-replicates", "value"),
    ],
)
def update_graph_view(
    proj_chosen, chosen_carbon_sources, chosen_species, color_by, plot_replicates
):
    fig_layout = go.Layout(
        margin=dict(l=0, r=10, t=100, b=10),
        xaxis=dict(title="Time [h]"),
        yaxis=dict(title="OD"),
    )
    parsed_data_dir = "export"
    if(proj_chosen == "Select Project" or proj_chosen == None or chosen_carbon_sources == "Select Carbon Source" or chosen_carbon_sources == None or chosen_species == "Select Species" or chosen_species == None):
        fig = go.Figure(layout=fig_layout)
        return fig, [], True

    args = projects[1:], species, cs, pooled_df_joint_metadata, parsed_data_dir
    filtered_metadata = utils.load_selected_metadata(
        proj_chosen, chosen_carbon_sources, chosen_species, args
    )
    if len(filtered_metadata) == 0:
        fig = go.Figure(layout=fig_layout)
        fig.update_layout(title="No data found")
        return fig, [], False

    df_merged = utils.load_data_from_metadata(filtered_metadata, args)

    global loaded_data
    loaded_data = df_merged.copy()
    global loaded_metadata
    loaded_metadata = filtered_metadata.copy()

    fig = utils.plot_data(df_merged, filtered_metadata, color_by, plot_replicates,fig_layout)
    table_df = utils.show_table(filtered_metadata)

    return (fig, table_df, False)


# Callback for updating the dropdowns in the View Data tab
@callback(
    [Output(component_id="cs-dropdown", component_property="options")],
    [Output(component_id="species-dropdown", component_property="options")],
    [
        Input("proj-dropdown", "value"),
    ],
)
def update_dropwdown(chosen_project):
    df = pooled_df_joint_metadata
    if chosen_project is None:
        return sorted(list(set(df["carbon_source"]))), sorted(list(set(df["species"])))
    if len(chosen_project) == 0:
        return sorted(list(set(df["carbon_source"]))), sorted(list(set(df["species"])))
    elif "All" in chosen_project:
        return sorted(list(set(df["carbon_source"]))), sorted(list(set(df["species"])))
    else:
        df = df[df["project"] == chosen_project[0]]
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

    df_export = pd.DataFrame()
    lg_list = filter_metadata["linegroup"].unique()
    for lg in lg_list:
        time_values = df_measurements[df_measurements["linegroup"] == lg][
            "time"
        ].to_numpy()
        measurement_values = df_measurements[df_measurements["linegroup"] == lg][
            "measurement"
        ].to_numpy()
        df_export = pd.concat(
            [
                df_export,
                pd.DataFrame(
                    {f"{lg}_time": time_values, f"{lg}_measurement": measurement_values}
                ),
            ],
            axis=1,
        )

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("metadata.csv", filter_metadata.to_csv(index=False))
        zf.writestr("measurements.csv", df_export.to_csv())

    zip_buffer.seek(0)
    return dcc.send_bytes(zip_buffer.getvalue(), "downloaded_data.zip")


@callback(
    [Output("collapse-table", "is_open")],
    [Output("collapse-button", "children")],
    [Input("collapse-button", "n_clicks")],
    [State("collapse-table", "is_open")],
)
def toggle_collapse(n, is_open):
    if n == 0:
        return is_open, ["Show meta data"]
    elif n % 2 == 0:
        return not is_open, ["Show meta data"]
    elif n % 2 != 0:
        return not is_open, ["Hide meta data"]
