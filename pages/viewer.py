import dash
from dash import dcc, html, callback, Output, Input, dash_table, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import os
from os.path import join
from functools import reduce


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

cs = list(set(pooled_df_joint_metadata["carbon_source"]))
species = list(set(pooled_df_joint_metadata["species"]))

cs.sort()
species.sort()
cs.insert(0, "All")
species.insert(0, "All")

dash.register_page(__name__, path="/", name="Home")  # '/' is home page


layout = html.Div(
    [
        dbc.Col(
            [
                dbc.Row(
                    [
                        dcc.Dropdown(
                            options=dropdown_list_projects,
                            placeholder="Select Project",
                            id="proj-dropdown",
                            multi=True,
                        ),
                        dcc.Dropdown(
                            options=cs,
                            placeholder="Select Carbon Source",
                            id="cs-dropdown",
                            multi=True,
                        ),
                        dcc.Dropdown(
                            options=species,
                            placeholder="Select Species",
                            id="species-dropdown",
                            multi=True,
                        ),
                    ],
                    class_name="pb-4",
                ),
                dcc.Dropdown(
                    ["Carbon Source", "Species"],
                    "Carbon Source",
                    id="color-by",
                ),
                dbc.Row([dcc.Graph(figure={}, id="controls-and-graph")]),
                dbc.Row(
                    [
                        dash_table.DataTable(
                            id="table",
                            columns=[
                                {"name": i, "id": j}
                                for i, j in zip(
                                    [
                                        "Experimenter",
                                        "Device",
                                        "Temperature",
                                        "Species",
                                        "Carbon source",
                                        "Carbon concentration [mM]",
                                        "Comments",
                                    ],
                                    [
                                        "Experimenter",
                                        "Device",
                                        "Temperature",
                                        "species",
                                        "carbon_source",
                                        "cs_conc",
                                        "comments",
                                    ],
                                )
                            ],
                        ),
                    ],
                    class_name="pt-4",
                ),
            ],
        ),
    ],
)


# Callback for updating the graph in the View Data tab
@callback(
    [
        Output(component_id="controls-and-graph", component_property="figure"),
        Output(component_id="table", component_property="data"),
    ],
    [
        Input(component_id="proj-dropdown", component_property="value"),
        Input("cs-dropdown", "value"),
        Input("species-dropdown", "value"),
        Input("color-by", "value"),
    ],
)
def update_graph_view(proj_chosen, chosen_carbon_sources, chosen_species, color_by):
    if proj_chosen == "Select Project" or proj_chosen == None:
        return go.Figure(), []
    if chosen_carbon_sources == "Select Carbon Source" or chosen_carbon_sources == None:
        return go.Figure(), []
    if chosen_species == "Select Species" or chosen_species == None:
        return go.Figure(), []

    if proj_chosen == ["All"]:
        proj_chosen = parsed_projects.copy()

    # Filter metadata based on selected carbon sources and species
    filtered_metadata = pooled_df_joint_metadata[
        (pooled_df_joint_metadata["species"].isin(chosen_species))
        & (pooled_df_joint_metadata["carbon_source"].isin(chosen_carbon_sources))
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
        colors = (
            px.colors.qualitative.Plotly if len(chosen_carbon_sources) > 1 else ["blue"]
        )
        for i, cur_cs in enumerate(chosen_carbon_sources):
            df_cs = df_merged[df_merged["carbon_source"] == cur_cs]
            for lg_id, lg in enumerate(df_cs["linegroup"].unique()):
                df_lg = df_cs[df_cs["linegroup"] == lg]
                cur_metadata = pooled_df_joint_metadata[
                    pooled_df_joint_metadata["linegroup"] == lg
                ]
                sp_lg = cur_metadata["species"].values[0]
                cs_conc_lg = cur_metadata["cs_conc"].values[0]
                fig.add_trace(
                    go.Scatter(
                        x=df_lg["time"],
                        y=df_lg["measurement"],
                        mode="lines",
                        line=dict(color=colors[i % len(colors)]),
                        name=f"{cur_cs}",
                        hovertemplate=f"<b>Species:</b> {sp_lg}<br>Time: %{{x}}<br>Measurement: %{{y}}<br>CS Concentration: {cs_conc_lg}<extra></extra>",
                        hoverlabel={"bgcolor": "#FFFFFF"},
                        showlegend=True if lg_id == 0 else False,
                    )
                )
    elif color_by == "Species":
        colors = px.colors.qualitative.Set2 if len(chosen_species) > 1 else ["magenta"]
        for i, cur_sp in enumerate(chosen_species):
            df_sp = df_merged[df_merged["species"] == cur_sp]
            for lg_id, lg in enumerate(df_sp["linegroup"].unique()):
                df_lg = df_sp[df_sp["linegroup"] == lg]
                cur_metadata = pooled_df_joint_metadata[
                    pooled_df_joint_metadata["linegroup"] == lg
                ]
                cs_lg = cur_metadata["carbon_source"].values[0]
                cur_cs_conc = cur_metadata["cs_conc"].values[0]
                fig.add_trace(
                    go.Scatter(
                        x=df_lg["time"],
                        y=df_lg["measurement"],
                        mode="lines",
                        line=dict(color=colors[i % len(colors)]),
                        name=f"{cur_sp}",
                        hovertemplate=f"<b>Carbon Source:</b> {cs_lg}<br>Time: %{{x}}<br>Measurement: %{{y}}<br>CS Concentration: {cur_cs_conc}<extra></extra>",
                        hoverlabel={"bgcolor": "#FFFFFF"},
                        showlegend=True if lg_id == 0 else False,
                    )
                )
    to_show_in_table = [
        "Experimenter",
        "Device",
        "Temperature",
        "species",
        "carbon_source",
        "cs_conc",
        "comments",
    ]
    table_data = (
        filtered_metadata[to_show_in_table].drop_duplicates().to_dict("records")
    )

    return (
        fig,
        table_data,
    )


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
    elif chosen_project[0] == "All":
        return sorted(list(set(df["carbon_source"]))), sorted(list(set(df["species"])))
    else:
        df = df[df["project"] == chosen_project[0]]
        return sorted(list(set(df["carbon_source"]))), sorted(list(set(df["species"])))
