import dash
from dash import html, dcc, Input, Output, State, ALL, no_update, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from io import BytesIO
import os
from os.path import join
from functools import reduce
import zipfile

# Data directory with the subfolders for each project
parsed_data_dir = "export"
parsed_projects = next(os.walk(parsed_data_dir))[1]
parsed_projects.sort()

# Choose the first project as default
project = parsed_projects[0]
dropdown_list_projects = parsed_projects.copy()
dropdown_list_projects.insert(0, "All")

# Load the data
pooled_df_joint_metadata = pd.DataFrame()
for project in parsed_projects:
    df_species = pd.read_csv(join(parsed_data_dir, project, "species_data.csv"))
    df_carbon_source = pd.read_csv(
        join(parsed_data_dir, project, "carbon_source_data.csv")
    )
    df_technical = pd.read_csv(join(parsed_data_dir, project, "technical_data.csv"))
    df_comments = pd.read_csv(join(parsed_data_dir, project, "comment_data.csv"))
    df_run = pd.read_csv(join(parsed_data_dir, project, "run_data.csv"))
    df_inhibitor = pd.read_csv(join(parsed_data_dir, project, "inhibitor_data.csv"))

    df_joint_technical = df_run.merge(df_technical, on="exp_ID", how="outer")
    df_joint_metadata = reduce(
        lambda x, y: pd.merge(x, y, on="linegroup", how="outer"),
        [df_joint_technical, df_species, df_carbon_source, df_comments],
    )
    pooled_df_joint_metadata = pd.concat([pooled_df_joint_metadata, df_joint_metadata])

# Get unique carbon sources and species
cs = list(set(pooled_df_joint_metadata["carbon_source"]))
species = list(set(pooled_df_joint_metadata["species"]))

cs.sort()
species.sort()
cs.insert(0, "All")
species.insert(0, "All")

to_show_in_table = [
    "Experimenter",
    "Device",
    "Temperature",
    "species",
    "carbon_source",
    "cs_conc",
    "comments",
]

# Function to generate checklist for carbon source and species
def generate_checklist(options, index):
    return dbc.Checklist(
        options=[{"label": opt, "value": opt} for opt in options],
        id={"type": "checkboxes", "index": index},
    )

# Create the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, "assets/style_new.css"])

# Tabs Layout
app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(label="View Data", children=[
            html.Div(
                className="container",
                children=[
                    html.H1(children="Growth Phenotyping"),
                    html.Hr(),
                    html.Div(
                        className="dropdown",
                        children=[
                            dcc.Dropdown(dropdown_list_projects, "Select Project", id="proj-dropdown",multi=True),
                            dcc.Dropdown(cs, "Select Carbon Source", id="cs-dropdown", multi=True),
                            dcc.Dropdown(species, "Select Species", id="species-dropdown", multi=True),
                        ],
                    ),
                    html.Hr(),
                    html.Div(
                        children=[
                            html.Hr(),
                            html.H6(children="Color graph by:"),
                            dcc.Dropdown(["Carbon Source", "Species"], "Carbon Source", id="color-by"),
                        ]
                    ),
                    html.Div(
                        className="graph",
                        children=[
                            dcc.Graph(figure={}, id="controls-and-graph"),
                        ],
                    ),
                    html.Div(
                        className="table",
                        children=[
                            dash_table.DataTable(
                                id="table",
                                columns=[
                                    {"name": i, "id": i}
                                    for i in pooled_df_joint_metadata[
                                        ["Experimenter", "Device", "Temperature", "species", "carbon_source", "cs_conc", "comments"]
                                    ].columns
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ]),
        dcc.Tab(label="Export Data", children=[
            html.Div(className = "container",children=[
                html.H1(children="Data Export"),
                html.Hr(),
                dbc.Table(
                    [
                        html.Thead(html.Tr([html.Th("Carbon Source"), html.Th("Species")])),
                        html.Tbody(
                            html.Tr(
                                [html.Td(generate_checklist(cs, "carbon_source")), html.Td(generate_checklist(species, "species"))]
                            )
                        ),
                    ],
                    bordered=True,
                    responsive=True,
                    style={"width": "100vw"},
                ),
                html.Div(
                    children=[
                        html.Hr(),
                        html.H6(children="Color graph by:"),
                        dcc.Dropdown(["Carbon Source", "Species"], "Carbon Source", id="color-by-export"),
                    ]
                ),
                html.Div(
                    className="graph",
                    children=[
                        dcc.Graph(figure={}, id="controls-and-graph-export", style={"height": "90vh"}),
                    ],
                ),
                html.Button("Download Data", id="download-btn"),
                dcc.Download(id="download-data"),
            ])
        ])
    ])
])

# Callback for updating the graph in the View Data tab
@app.callback(
    [
        Output(component_id="controls-and-graph", component_property="figure"),
        Output(component_id="table", component_property="data"),
    ],
    [
        Input(component_id="proj-dropdown", component_property="value"),
        Input("cs-dropdown", "value"),
        Input("species-dropdown", "value"),
        Input("color-by", "value"),
    ]
)
def update_graph_view(proj_chosen, chosen_carbon_sources, chosen_species,color_by):
    if(proj_chosen == "Select Project" or proj_chosen == None):
        return go.Figure(), []
    if(chosen_carbon_sources == "Select Carbon Source" or chosen_carbon_sources == None):
        return go.Figure(), []
    if(chosen_species == "Select Species" or chosen_species == None):
        return go.Figure(), []
    
    if(proj_chosen == ["All"]):
        proj_chosen = parsed_projects.copy()

    # Filter metadata based on selected carbon sources and species
    filtered_metadata = pooled_df_joint_metadata[
        (pooled_df_joint_metadata["species"].isin(chosen_species)) &
        (pooled_df_joint_metadata["carbon_source"].isin(chosen_carbon_sources))
    ]

    # Obtain the relevant linegroups from the filtered metadata
    common_lg = filtered_metadata["linegroup"].unique()

    # Choose projects based on linegroups
    projects_needed = pooled_df_joint_metadata[
        pooled_df_joint_metadata["linegroup"].isin(common_lg)
    ]["project"].unique()

    # Get the common projects
    projects_common = list(set(proj_chosen).intersection(set(projects_needed)))
    if len(projects_common) == 0:
        fig = go.Figure()
        fig.update_layout(title="No data found")
        return fig, []

    # Load only selected projects
    dfs = []
    for project in projects_common:
        dfs.append(pd.read_csv(join(parsed_data_dir, project, "measurement_data.csv")))

    try:
        df_data = pd.concat(dfs)
    except:
        return no_update
    df_data = df_data[df_data["linegroup"].isin(common_lg)].sort_values(by="time")

    # Merge the measurement data with the filtered metadata to include carbon source and species info
    df_merged = df_data.merge(filtered_metadata, on="linegroup")

    # Initialize figure
    fig = go.Figure()

    # Color plotting based on carbon source or species
    if color_by == "Carbon Source":
        colors = px.colors.qualitative.Plotly if len(chosen_carbon_sources) > 1 else ["blue"]
        for i, cur_cs in enumerate(chosen_carbon_sources):
            df_cs = df_merged[df_merged["carbon_source"] == cur_cs]
            for lg_id,lg in enumerate(df_cs["linegroup"].unique()):
                df_lg = df_cs[df_cs["linegroup"] == lg]
                cur_metadata = pooled_df_joint_metadata[pooled_df_joint_metadata["linegroup"] == lg]
                sp_lg = cur_metadata["species"].values[0]
                cs_conc_lg = cur_metadata["cs_conc"].values[0]
                fig.add_trace(
                    go.Scatter(
                        x=df_lg["time"],
                        y=df_lg["measurement"],
                        mode="lines",
                        line=dict(color=colors[i % len(colors)]),
                        name=f'{cur_cs}',
                        hovertemplate=f'<b>Species:</b> {sp_lg}<br>Time: %{{x}}<br>Measurement: %{{y}}<br>CS Concentration: {cs_conc_lg}<extra></extra>',
                        hoverlabel={"bgcolor": "#FFFFFF"},
                        showlegend=True if lg_id == 0 else False,
                    )
                )
    elif color_by == "Species":
        colors = px.colors.qualitative.Set2 if len(chosen_species) > 1 else ["magenta"]
        for i, cur_sp in enumerate(chosen_species):
            df_sp = df_merged[df_merged["species"] == cur_sp]
            for lg_id,lg in enumerate(df_sp["linegroup"].unique()):
                df_lg = df_sp[df_sp["linegroup"] == lg]
                cur_metadata = pooled_df_joint_metadata[pooled_df_joint_metadata["linegroup"] == lg]
                cs_lg = cur_metadata["carbon_source"].values[0]
                cur_cs_conc = cur_metadata["cs_conc"].values[0]
                fig.add_trace(
                    go.Scatter(
                        x=df_lg["time"],
                        y=df_lg["measurement"],
                        mode="lines",
                        line=dict(color=colors[i % len(colors)]),
                        name=f'{cur_sp}',
                        hovertemplate=f'<b>Carbon Source:</b> {cs_lg}<br>Time: %{{x}}<br>Measurement: %{{y}}<br>CS Concentration: {cur_cs_conc}<extra></extra>',
                        hoverlabel={"bgcolor": "#FFFFFF"},
                        showlegend=True if lg_id == 0 else False,
                    )
                )
    table_data = (
    filtered_metadata[to_show_in_table].drop_duplicates().to_dict("records")
    )

    return fig, table_data

# Callback for updating the graph in the Export Data tab
@app.callback(
    Output("controls-and-graph-export", "figure"),
    [Input({"type": "checkboxes", "index": ALL}, "value"),
     Input("color-by-export", "value")]
)

def update_graph_export(value_in, color_by):
    # Check for when no values are selected
    if value_in is None or not any(value_in):
        return dash.no_update

    chosen_carbon_sources = value_in[0] if value_in[0] else []
    chosen_species = value_in[1] if value_in[1] else []

    if not chosen_carbon_sources or not chosen_species:
        return dash.no_update

    # Handle "All" option if implemented
    if "All" in chosen_carbon_sources:
        chosen_carbon_sources = cs[1:]  # Assuming 'cs' is your list of all carbon sources
    if "All" in chosen_species:
        chosen_species = species[1:]  # Assuming 'species' is your list of all species

    # Filter metadata based on selected carbon sources and species
    filtered_metadata = pooled_df_joint_metadata[
        (pooled_df_joint_metadata["species"].isin(chosen_species)) &
        (pooled_df_joint_metadata["carbon_source"].isin(chosen_carbon_sources))
    ]

    if filtered_metadata.empty:
        fig = go.Figure()
        fig.update_layout(title="No data found for selected species and carbon sources")
        return fig

    # Obtain the relevant linegroups from the filtered metadata
    common_lg = filtered_metadata["linegroup"].unique()

    # Choose projects based on linegroups
    projects_chosen = pooled_df_joint_metadata[
        pooled_df_joint_metadata["linegroup"].isin(common_lg)
    ]["project"].unique()

    # Load only selected projects
    dfs = []
    for project in projects_chosen:
        dfs.append(pd.read_csv(join(parsed_data_dir, project, "measurement_data.csv")))

    df_data = pd.concat(dfs)
    df_data = df_data[df_data["linegroup"].isin(common_lg)].sort_values(by="time")

    # Merge the measurement data with the filtered metadata to include carbon source and species info
    df_merged = df_data.merge(filtered_metadata, on="linegroup")

    # Initialize figure
    fig = go.Figure()

    # Color plotting based on carbon source or species
    if color_by == "Carbon Source":
        colors = px.colors.qualitative.Plotly if len(chosen_carbon_sources) > 1 else ["blue"]
        for i, cur_cs in enumerate(chosen_carbon_sources):
            df_cs = df_merged[df_merged["carbon_source"] == cur_cs]
            for lg_id,lg in enumerate(df_cs["linegroup"].unique()):
                df_lg = df_cs[df_cs["linegroup"] == lg]
                cur_metadata = pooled_df_joint_metadata[pooled_df_joint_metadata["linegroup"] == lg]
                sp_lg = cur_metadata["species"].values[0]
                cs_conc_lg = cur_metadata["cs_conc"].values[0]
                fig.add_trace(
                    go.Scatter(
                        x=df_lg["time"],
                        y=df_lg["measurement"],
                        mode="lines",
                        line=dict(color=colors[i % len(colors)]),
                        name=f'{cur_cs}',
                        hovertemplate=f'<b>Species:</b> {sp_lg}<br><b>Carbon Source:</b> {cur_cs}<br>Time: %{{x}}<br>Measurement: %{{y}}<br>CS Concentration: {cs_conc_lg}<extra></extra>',
                        hoverlabel={"bgcolor": "#FFFFFF"},
                        showlegend=True if lg_id == 0 else False,
                    )
                )
    elif color_by == "Species":
        colors = px.colors.qualitative.Set2 if len(chosen_species) > 1 else ["magenta"]
        for i, cur_sp in enumerate(chosen_species):
            df_sp = df_merged[df_merged["species"] == cur_sp]
            for lg_id,lg in enumerate(df_sp["linegroup"].unique()):
                df_lg = df_sp[df_sp["linegroup"] == lg]
                cur_metadata = pooled_df_joint_metadata[pooled_df_joint_metadata["linegroup"] == lg]
                cs_lg = cur_metadata["carbon_source"].values[0]
                cur_cs_conc = cur_metadata["cs_conc"].values[0]
                fig.add_trace(
                    go.Scatter(
                        x=df_lg["time"],
                        y=df_lg["measurement"],
                        mode="lines",
                        line=dict(color=colors[i % len(colors)]),
                        name=f'{cur_sp}',
                        hovertemplate=f'<b>Species:</b> {cur_sp}<br><b>Carbon Source:</b> {cs_lg}<br>Time: %{{x}}<br>Measurement: %{{y}}<br>CS Concentration: {cur_cs_conc}<extra></extra>',
                        hoverlabel={"bgcolor": "#FFFFFF"},
                        showlegend=True if lg_id == 0 else False,
                    )
                )

    return fig

# Callback for downloading data
@app.callback(
    Output("download-data", "data"),
    Input("download-btn", "n_clicks"),
    State({"type": "checkboxes", "index": ALL}, "value"),
    prevent_initial_call=True
)
def download_data(n_clicks, checkbox_values):
    if n_clicks is None:
        return dash.no_update

    chosen_carbon_sources = checkbox_values[0] if checkbox_values[0] else []
    chosen_species = checkbox_values[1] if checkbox_values[1] else []

    if "All" in chosen_carbon_sources:
        chosen_carbon_sources = cs[1:]
    if "All" in chosen_species:
        chosen_species = species[1:]

    filter_metadata = pooled_df_joint_metadata[
        (pooled_df_joint_metadata["carbon_source"].isin(chosen_carbon_sources)) &
        (pooled_df_joint_metadata["species"].isin(chosen_species))
    ]

    measurement_data_frames = []
    for project in filter_metadata["project"].unique():
        df_measurements = pd.read_csv(
            join(parsed_data_dir, project, "measurement_data.csv")
        )
        measurement_data_frames.append(df_measurements)

    df_measurements = pd.concat(measurement_data_frames)
    df_measurements = df_measurements[
        df_measurements["linegroup"].isin(filter_metadata["linegroup"].unique())
    ]

    df_export = pd.DataFrame()
    lg_list = filter_metadata["linegroup"].unique()
    for lg in lg_list:
        time_values = df_measurements[df_measurements["linegroup"] == lg]["time"].to_numpy()
        measurement_values = df_measurements[df_measurements["linegroup"] == lg]["measurement"].to_numpy()
        df_export = pd.concat(
            [df_export, pd.DataFrame({f"{lg}_time": time_values, f"{lg}_measurement": measurement_values})],
            axis=1,
        )

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("metadata.csv", filter_metadata.to_csv(index=False))
        zf.writestr("measurements.csv", df_export.to_csv())

    zip_buffer.seek(0)
    return dcc.send_bytes(zip_buffer.getvalue(), "downloaded_data.zip")


# Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=True)
