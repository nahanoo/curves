import pandas as pd
import numpy as np
from os.path import join
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

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
    return projects,cs,species

def load_selected_metadata(proj_chosen, chosen_carbon_sources, chosen_species,args):
    parsed_projects,species,cs,pooled_df_joint_metadata,parsed_data_dir = args
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

def load_data_from_metadata(filtered_metadata,args):
    parsed_projects,species,cs,pooled_df_joint_metadata,parsed_data_dir = args

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

def show_table(filtered_metadata):
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
    return dbc.Table.from_dataframe(
            pd.DataFrame(table_data, index=range(len(table_data))),
            header=[
                "Experimenter",
                "Device",
                "Temperature",
                "Species",
                "Carbon source",
                "Concentration [mM]",
                "Comments",
            ],
        )
