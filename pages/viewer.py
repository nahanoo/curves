import dash
from dash import dcc, html, callback, Output, Input, dash_table, no_update, State, ALL
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import os
from os.path import join
from functools import reduce
import zipfile
from io import BytesIO
import numpy as np

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

loaded_data = []
loaded_metadata = []

# Helper functions

def load_selected_metadata(proj_chosen, chosen_carbon_sources, chosen_species):
    if "All" in proj_chosen:
        proj_chosen = parsed_projects.copy()
    if "All" in chosen_carbon_sources:
        chosen_carbon_sources = cs[1:]
    if "All" in chosen_species:
        chosen_species = species[1:]


    # Filter metadata based on selected carbon sources and species
    filtered_metadata = pooled_df_joint_metadata[
        (pooled_df_joint_metadata["species"].isin(chosen_species))
        & (pooled_df_joint_metadata["carbon_source"].isin(chosen_carbon_sources)) &
        (pooled_df_joint_metadata["project"].isin(proj_chosen))
    ]
    return filtered_metadata

def load_data_from_metadata(filtered_metadata):
    # Obtain the relevant linegroups from the filtered metadata
    common_lg = filtered_metadata["linegroup"].unique()

    # Choose projects based on linegroups
    projects_common = pooled_df_joint_metadata[
        pooled_df_joint_metadata["linegroup"].isin(common_lg)
    ]["project"].unique()

    # Load only selected projects
    dfs = []
    for project in projects_common:
        dfs.append(pd.read_csv(join(parsed_data_dir, project, "measurement_data.csv")))
    df_data = pd.concat(dfs)
    df_data = df_data[df_data["linegroup"].isin(common_lg)].sort_values(by="time")

    # Merge the measurement data with the filtered metadata to include carbon source and species info
    df_merged = df_data.merge(filtered_metadata, on="linegroup")

    return df_merged

def restructure_metadata(df_metadata):
    projects_present = df_metadata["project"].unique()
    species_selected = df_metadata["species"].unique()
    carbon_source_selected = df_metadata["carbon_source"].unique()
    concentrations_present = []
    lg_replicates = []
    for i_0 in range(len(projects_present)):
        cur_project = projects_present[i_0]
        projects_filtered_metadata = df_metadata[df_metadata["project"] == cur_project]
        cur_proj_concs = []
        cur_proj_lg_replicates = []
        for i in range(len(species_selected)):
            species_filtered_metadata = projects_filtered_metadata[projects_filtered_metadata["species"] == species_selected[i]]
            cur_species_concs = []
            cur_sp_lg_replicates = []
            for j in range(len(carbon_source_selected)):
                cs_filtered_metadata = species_filtered_metadata[species_filtered_metadata["carbon_source"] == carbon_source_selected[j]]
                unique_cs_concs = cs_filtered_metadata["cs_conc"].unique()
                # linegroup_carbon_source = cs_filtered_metadata["linegroup"].unique()
                # projects_present = cs_filtered_metadata["project"].unique()
                # if(len(projects_present)>1):
                #     print("Warning: %s with %s has data from multiple projects."%(species_selected[i],carbon_source_selected[j]))
                cur_species_concs.append(unique_cs_concs)
                lg_conc_replicates = []
                for k in range(len(unique_cs_concs)):
                    lg_selected_conc = cs_filtered_metadata[cs_filtered_metadata["cs_conc"] == unique_cs_concs[k]]["linegroup"].unique()
                    lg_conc_replicates.append(lg_selected_conc)
                cur_sp_lg_replicates.append(lg_conc_replicates)
            cur_proj_concs.append(cur_species_concs)
            cur_proj_lg_replicates.append(cur_sp_lg_replicates)
        concentrations_present.append(cur_proj_concs)
        lg_replicates.append(cur_proj_lg_replicates)

    return projects_present,species_selected, carbon_source_selected, concentrations_present, lg_replicates

def add_trace(fig,cur_time,cur_measurement,color_dict,legendgroup,name,hovertext,showlegend):
    fig.add_trace(
        go.Scatter(
            x=cur_time,
            y=cur_measurement,
            mode="lines",
            line = color_dict,    
            legendgroup= legendgroup,
            name = name,
            hovertemplate=hovertext,
            hoverlabel={"bgcolor": "#FFFFFF"},
            showlegend=showlegend,
        )
    )

def generate_legend_params(cur_sp,cur_cs,color_by,plot_replicates,i,j,k,l=None):
    if(color_by == "Carbon Source"):
        if(plot_replicates == None or len(plot_replicates) == 0):
            showlegend= True if (i==0 and k==0) else False
        else:
            showlegend=  True if (i==0 and k==0 and l == 0) else False
        legendgroup,name = cur_cs,cur_cs
    else:
        if(plot_replicates == None or len(plot_replicates) == 0):
            showlegend=  True if (j==0 and k==0) else False
        else:
            showlegend=  True if (j==0 and k==0 and  l == 0) else False
        legendgroup,name = cur_sp,cur_sp
    return showlegend,legendgroup,name

def plot_data(df_merged,filtered_metadata,color_by,plot_replicates):
    projects_present,species_selected, carbon_source_selected, concentrations_present, lg_replicates = restructure_metadata(filtered_metadata)
    color_palette = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728","#9467bd", "#8c564b", "#e377c2", "#7f7f7f","#bcbd22", "#17becf"]

    fig = go.Figure()
    for i_0 in range(len(projects_present)):
        cur_project = projects_present[i_0]
        for i in range(len(species_selected)):
            cur_sp = species_selected[i]
            for j in range(len(carbon_source_selected)):
                cur_cs = carbon_source_selected[j]
                color_dict = {"color":color_palette[j] if color_by == "Carbon Source" else color_palette[i]}
                for k in range(len(concentrations_present[i_0][i][j])):
                    cur_conc = concentrations_present[i_0][i][j][k]
                    cur_lgs = lg_replicates[i_0][i][j][k]
                    experimenter = df_merged[df_merged["linegroup"] == cur_lgs[0]]["Experimenter"].values[0]
                    hovertext = f"<b>Species:</b> {cur_sp}<br><b>Carbon Source:</b> {cur_cs}<br>CS Concentration: {cur_conc}<br>Time: %{{x}}<br>Measurement: %{{y}}<br>Experimenter: {experimenter}<extra></extra>"
                    if(plot_replicates == None or len(plot_replicates) == 0):
                        showlegend,legendgroup,name = generate_legend_params(cur_sp,cur_cs,color_by,plot_replicates,i,j,k)
                        try:
                            common_time = np.array([df_merged[df_merged["linegroup"] == cur_lgs[i]]["time"] for i in range(len(cur_lgs))])
                        except:
                            print(cur_lgs)
                            common_time = np.array([df_merged[df_merged["linegroup"] == cur_lgs[i]]["time"] for i in range(len(cur_lgs))])
                        common_measurement = np.array([df_merged[df_merged["linegroup"] == cur_lgs[i]]["measurement"] for i in range(len(cur_lgs))])
                        add_trace(fig,common_time[0],np.mean(common_measurement,axis=0),color_dict,legendgroup,name,hovertext,showlegend)

                    else:
                        for l in range(len(cur_lgs)):
                            showlegend,legendgroup,name = generate_legend_params(cur_sp,cur_cs,color_by,plot_replicates,i,j,k,l)
                            cur_lg = cur_lgs[l]
                            cur_time = df_merged[df_merged["linegroup"] == cur_lg]["time"]
                            cur_measurement = df_merged[df_merged["linegroup"] == cur_lg]["measurement"]
                            add_trace(fig,cur_time,cur_measurement,color_dict,legendgroup,name,hovertext,showlegend)
                    
    return fig




# Dash layout
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
                dcc.Checklist([" Plot replicates"], id="plot-replicates"),
                html.Hr(),
                dbc.Row([dcc.Graph(figure={}, id="controls-and-graph")]),
                dbc.Row([
                    html.Button("Download Data", id="download-btn"),
                    dcc.Download(id="download-data"),
            ]),
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
                            style_table={'overflowX': 'auto'},
                            style_header={
                                'backgroundColor': '#415a77',
                                'fontWeight': 'bold',
                                'color': '#f8f9fa',
                                'textAlign': 'center',
                                'border': '1px solid black'
                            },
                            style_cell={
                                'backgroundColor': '#ecf0f1',
                                'color': '#2c3e50',
                                'textAlign': 'center',
                                'border': '1px solid lightgrey',
                                'fontFamily': 'Arial, sans-serif',
                                'fontSize': '14px',
                            },
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': '#f5f5f5',
                                },
                                {
                                    'if': {'row_index': 'even'},
                                    'backgroundColor': '#ffffff',
                                },
                                {
                                    'if': {
                                        'column_id': 'Temperature',
                                        'filter_query': '{Temperature} > 37'
                                    },
                                    'backgroundColor': '#e74c3c',
                                    'color': 'white',
                                },
                            ],
                            style_as_list_view=True,
                            style_cell_conditional=[
                                {'if': {'column_id': 'Comments'},
                                'textAlign': 'left'},
                            ],
                            css=[{
                                'selector': 'table',
                                'rule': 'border-collapse: collapse; width: 100%;'
                            }],
                        ),
                    ],
                    class_name="pt-4",
                ),
            ],
        ),
    ],
)


# Callback for plotting the selected data
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
        Input("plot-replicates", "value"),
    ],
)
def update_graph_view(proj_chosen, chosen_carbon_sources, chosen_species, color_by,plot_replicates):
    if proj_chosen == "Select Project" or proj_chosen == None:
        return go.Figure(), []
    if chosen_carbon_sources == "Select Carbon Source" or chosen_carbon_sources == None:
        return go.Figure(), []
    if chosen_species == "Select Species" or chosen_species == None:
        return go.Figure(), []
    
    filtered_metadata = load_selected_metadata(proj_chosen, chosen_carbon_sources, chosen_species)
    if(len(filtered_metadata) == 0):
        fig = go.Figure()
        fig.update_layout(title="No data found")
        return fig, []

    df_merged = load_data_from_metadata(filtered_metadata)

    global loaded_data 
    loaded_data = df_merged.copy()
    global loaded_metadata
    loaded_metadata = filtered_metadata.copy()

    fig = plot_data(df_merged,filtered_metadata,color_by,plot_replicates)
    # # Initialize figure
    # fig = go.Figure()

    # # Color plotting based on carbon source or species
    # if color_by == "Carbon Source":
    #     colors = (
    #         px.colors.qualitative.Plotly if len(chosen_carbon_sources) > 1 else ["blue"]
    #     )
    #     for i, cur_cs in enumerate(chosen_carbon_sources):
    #         df_cs = df_merged[df_merged["carbon_source"] == cur_cs]
    #         for lg_id, lg in enumerate(df_cs["linegroup"].unique()):
    #             df_lg = df_cs[df_cs["linegroup"] == lg]
    #             cur_metadata = pooled_df_joint_metadata[
    #                 pooled_df_joint_metadata["linegroup"] == lg
    #             ]
    #             sp_lg = cur_metadata["species"].values[0]
    #             cs_conc_lg = cur_metadata["cs_conc"].values[0]
    #             fig.add_trace(
    #                 go.Scatter(
    #                     x=df_lg["time"],
    #                     y=df_lg["measurement"],
    #                     mode="lines",
    #                     line=dict(color=colors[i % len(colors)]),
    #                     name=f"{cur_cs}",
    #                     hovertemplate=f"<b>Species:</b> {sp_lg}<br>Time: %{{x}}<br>Measurement: %{{y}}<br>CS Concentration: {cs_conc_lg}<extra></extra>",
    #                     hoverlabel={"bgcolor": "#FFFFFF"},
    #                     showlegend=True if lg_id == 0 else False,
    #                 )
    #             )
    # elif color_by == "Species":
    #     colors = px.colors.qualitative.Set2 if len(chosen_species) > 1 else ["magenta"]
    #     for i, cur_sp in enumerate(chosen_species):
    #         df_sp = df_merged[df_merged["species"] == cur_sp]
    #         for lg_id, lg in enumerate(df_sp["linegroup"].unique()):
    #             df_lg = df_sp[df_sp["linegroup"] == lg]
    #             cur_metadata = pooled_df_joint_metadata[
    #                 pooled_df_joint_metadata["linegroup"] == lg
    #             ]
    #             cs_lg = cur_metadata["carbon_source"].values[0]
    #             cur_cs_conc = cur_metadata["cs_conc"].values[0]
    #             fig.add_trace(
    #                 go.Scatter(
    #                     x=df_lg["time"],
    #                     y=df_lg["measurement"],
    #                     mode="lines",
    #                     line=dict(color=colors[i % len(colors)]),
    #                     name=f"{cur_sp}",
    #                     hovertemplate=f"<b>Carbon Source:</b> {cs_lg}<br>Time: %{{x}}<br>Measurement: %{{y}}<br>CS Concentration: {cur_cs_conc}<extra></extra>",
    #                     hoverlabel={"bgcolor": "#FFFFFF"},
    #                     showlegend=True if lg_id == 0 else False,
    #                 )
    #             )
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
    elif chosen_project[0] == "All":
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
