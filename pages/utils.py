import pandas as pd
import numpy as np
from os.path import join
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html, dcc

# Helper functions


def load_dropdown_data(pooled_df_joint_metadata):
    cs = list(set(pooled_df_joint_metadata["carbon_source"]))
    species = list(set(pooled_df_joint_metadata["species"]))
    projects = list(set(pooled_df_joint_metadata["project"]))

    cs.sort()
    species.sort()
    cs.insert(0, "All")
    species.insert(0, "All")
    projects.insert(0, "All")
    return projects, cs, species


def load_selected_metadata(proj_chosen, chosen_carbon_sources, chosen_species, args):
    parsed_projects, species, cs, pooled_df_joint_metadata, parsed_data_dir = args
    if "All" in proj_chosen:
        proj_chosen = parsed_projects.copy()
    if "All" in chosen_carbon_sources:
        chosen_carbon_sources = cs[1:]
    if "All" in chosen_species:
        chosen_species = species[1:]

    # Filter metadata based on selected carbon sources and species
    filtered_metadata = pooled_df_joint_metadata[
        (pooled_df_joint_metadata["species"].isin(chosen_species))
        & (pooled_df_joint_metadata["carbon_source"].isin(chosen_carbon_sources))
        & (pooled_df_joint_metadata["project"].isin(proj_chosen))
    ]
    return filtered_metadata


def load_data_from_metadata(filtered_metadata, args):
    parsed_projects, species, cs, pooled_df_joint_metadata, parsed_data_dir = args

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
    df_data = df_data[df_data["linegroup"].isin(common_lg)].sort_values(by="time").drop_duplicates()

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
            species_filtered_metadata = projects_filtered_metadata[
                projects_filtered_metadata["species"] == species_selected[i]
            ]
            cur_species_concs = []
            cur_sp_lg_replicates = []
            for j in range(len(carbon_source_selected)):
                cs_filtered_metadata = species_filtered_metadata[
                    species_filtered_metadata["carbon_source"]
                    == carbon_source_selected[j]
                ]
                unique_cs_concs = cs_filtered_metadata["cs_conc"].unique()
                cur_species_concs.append(unique_cs_concs)
                lg_conc_replicates = []
                for k in range(len(unique_cs_concs)):
                    lg_selected_conc = cs_filtered_metadata[
                        cs_filtered_metadata["cs_conc"] == unique_cs_concs[k]
                    ]["linegroup"].unique()
                    lg_conc_replicates.append(lg_selected_conc)
                cur_sp_lg_replicates.append(lg_conc_replicates)
            cur_proj_concs.append(cur_species_concs)
            cur_proj_lg_replicates.append(cur_sp_lg_replicates)
        concentrations_present.append(cur_proj_concs)
        lg_replicates.append(cur_proj_lg_replicates)

    return (
        projects_present,
        species_selected,
        carbon_source_selected,
        concentrations_present,
        lg_replicates,
    )


def add_trace(
    fig, cur_time, cur_measurement, color_dict, legendgroup, name, hovertext, showlegend
):
    fig.add_trace(
        go.Scatter(
            x=cur_time,
            y=cur_measurement,
            mode="lines",
            line=color_dict,
            legendgroup=legendgroup,
            name=name,
            hovertemplate=hovertext,
            hoverlabel={"bgcolor": "#FFFFFF"},
            showlegend=showlegend,
        )
    )


def generate_legend_params(cur_sp, cur_cs, color_by, used_legendgroups):
    if color_by == "Carbon Source":
        legendgroup, name = cur_cs, cur_cs
        showlegend = True if cur_cs not in used_legendgroups else False
    else:
        legendgroup, name = cur_sp, cur_sp
        showlegend = True if cur_sp not in used_legendgroups else False

    if showlegend:
        used_legendgroups.append(legendgroup)
    return showlegend, legendgroup, name, used_legendgroups


def plot_data(df_merged, filtered_metadata, color_by, plot_replicates, plot_type, fig_layout):
    (
        projects_present,
        species_selected,
        carbon_source_selected,
        concentrations_present,
        lg_replicates,
    ) = restructure_metadata(filtered_metadata)
    color_palette = [
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf",
    ]

    fig = go.Figure(layout=fig_layout)
    used_legendgrouos = []
    for i_0 in range(len(projects_present)):
        cur_project = projects_present[i_0]
        for i in range(len(species_selected)):
            cur_sp = species_selected[i]
            for j in range(len(carbon_source_selected)):
                cur_cs = carbon_source_selected[j]
                color_dict = {
                    "color": color_palette[j]
                    if color_by == "Carbon Source"
                    else color_palette[i]
                }
                for k in range(len(concentrations_present[i_0][i][j])):
                    cur_conc = concentrations_present[i_0][i][j][k]
                    cur_lgs = lg_replicates[i_0][i][j][k]
                    cur_exp_ID = df_merged[df_merged["linegroup"] == cur_lgs[0]][
                        "exp_ID"
                    ].values[0]
                    experimenter = df_merged[df_merged["linegroup"] == cur_lgs[0]][
                        "Experimenter"
                    ].values[0]
                    hovertext = f"<b>Species:</b> {cur_sp}<br><b>Carbon Source:</b> {cur_cs}<br><b>CS Concentration</b>: {cur_conc}<br><b>Time</b>: %{{x}}<br><b>Measurement:</b> %{{y}}<br><b>Experimenter</b>: {experimenter}<br><b>Project</b>: {cur_project}<br><b>Experiment</b>: {cur_exp_ID}"
                    if plot_replicates == None or len(plot_replicates) == 0:
                        showlegend, legendgroup, name, used_legendgrouos = (
                            generate_legend_params(
                                cur_sp, cur_cs, color_by, used_legendgrouos
                            )
                        )
                        common_time = np.array(
                            [
                                df_merged[df_merged["linegroup"] == cur_lgs[i]]["time"]
                                for i in range(len(cur_lgs))
                            ]
                        )
                        common_measurement = np.array(
                            [
                                df_merged[df_merged["linegroup"] == cur_lgs[i]][
                                    "measurement"
                                ]
                                for i in range(len(cur_lgs))
                            ]
                        )
                        add_trace(
                            fig,
                            common_time[0],
                            np.mean(common_measurement, axis=0),
                            color_dict,
                            legendgroup,
                            name,
                            hovertext,
                            showlegend,
                        )


                    else:
                        for l in range(len(cur_lgs)):
                            showlegend, legendgroup, name, used_legendgrouos = (
                                generate_legend_params(
                                    cur_sp, cur_cs, color_by, used_legendgrouos
                                )
                            )
                            cur_lg = cur_lgs[l]
                            cur_time = df_merged[df_merged["linegroup"] == cur_lg][
                                "time"
                            ]
                            cur_measurement = df_merged[
                                df_merged["linegroup"] == cur_lg
                            ]["measurement"]
                            add_trace(
                                fig,
                                cur_time,
                                cur_measurement,
                                color_dict,
                                legendgroup,
                                name,
                                hovertext,
                                showlegend,
                            )
    if(plot_type == "log-scale"):
        fig.update_yaxes(type="log",range=[-3, 1])

    return fig

def export_restructuring(df_measurements,filter_metadata):
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
    return df_export

def show_table(filtered_metadata):
    to_show_in_table = [
        "Experimenter",
        "exp_ID",
        "Temperature",
        "species",
        "carbon_source",
        "cs_conc",
        "comments",
    ]
    table_data = (
        filtered_metadata[to_show_in_table].drop_duplicates().to_dict("records")
    )
    return dbc.Table.from_dataframe(
        pd.DataFrame(table_data, index=range(len(table_data))),
        header=[
            "Experimenter",
            "Experiment",
            "Temperature",
            "Species",
            "Carbon source",
            "Concentration [mM]",
            "Comments",
        ],
    )


def show_project_descriptions(filtered_metadata):
    df_project = pd.DataFrame(columns=["Project", "Description"])

    for project in set(filtered_metadata["project"]):
        with open(join("export", project, "description.txt"), "r") as handle:
            description = handle.read()
        df_project.loc[len(df_project)] = [project, description]

    return dbc.Table.from_dataframe(df_project)


def show_experiment_descriptions(filtered_metadata):
    df_experiment = pd.DataFrame(columns=["Experiment", "Description"])
    for project in set(filtered_metadata["project"]):
        for experiment in set(filtered_metadata["exp_ID"]):
            description = filtered_metadata[filtered_metadata["exp_ID"] == experiment][
                "Experiment description"
            ].values[0]
            df_experiment.loc[len(df_experiment)] = [experiment, description]
    return dbc.Table.from_dataframe(df_experiment)
