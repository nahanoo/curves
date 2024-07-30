import pandas as pd
from dash import Dash, dcc, html, Input, Output, dash_table, callback
import plotly.express as px
from os.path import join
from functools import reduce
import os

# Data directory with the subfolders for each project
parsed_data_dir = "export"
parsed_projects = next(os.walk(parsed_data_dir))[1]
parsed_projects.sort()

# Choose the first project as default
project = parsed_projects[0]

# Load the data
pooled_df_joint_metadata = pd.DataFrame()
for project in parsed_projects:
    df_species = pd.read_csv(
        join(parsed_data_dir, project, project + "_species_data.csv")
    )
    df_carbon_source = pd.read_csv(
        join(parsed_data_dir, project, project + "_carbon_source_data.csv")
    )
    df_technical = pd.read_csv(
        join(parsed_data_dir, project, project + "_technical_data.csv")
    )
    df_comments = pd.read_csv(
        join(parsed_data_dir, project, project + "_comment_data.csv")
    )
    df_run = pd.read_csv(join(parsed_data_dir, project, project + "_run_data.csv"))
    df_inhibitor = pd.read_csv(
        join(parsed_data_dir, project, project + "_inhibitor_data.csv")
    )

    # Merge data with expID as common columns
    df_joint_technical = df_run.merge(df_technical, on="exp_ID", how="outer")

    # Merge all metadata with linegroup as common reference
    df_joint_metadata = reduce(
        lambda x, y: pd.merge(x, y, on="linegroup", how="outer"),
        [df_joint_technical, df_species, df_carbon_source, df_comments],
    )
    pooled_df_joint_metadata = pd.concat([pooled_df_joint_metadata, df_joint_metadata])

to_show_in_table = [
    "Experimenter",
    "Device",
    "Temperature",
    "species",
    "carbon_source",
    "cs_conc",
    "comments",
]

# Get unique carbon sources and species
cs = list(set(pooled_df_joint_metadata["carbon_source"]))
species = list(set(pooled_df_joint_metadata["species"]))

cs.sort()
species.sort()

# Create the Dash app
app = Dash(__name__)
app.css.append_css({"external_url": "assets/style_new.css"})

# App layout with dropdowns for project, carbon source and species
app.layout = html.Div(
    className="container",
    children=[
        html.H1(children="Growth Phenotyping"),
        html.Hr(),
        html.Div(
            className="dropdown",
            children=[
                dcc.Dropdown(parsed_projects, parsed_projects[0], id="proj-dropdown"),
                dcc.Dropdown(cs, cs[0], id="cs-dropdown"),
                dcc.Dropdown(species, species[0], id="species-dropdown"),
            ],
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
                        for i in pooled_df_joint_metadata[to_show_in_table].columns
                    ],
                ),
            ],
        ),
    ],
)


# Add controls to build the interaction
@callback(
    [
        Output(component_id="controls-and-graph", component_property="figure"),
        Output(component_id="table", component_property="data"),
    ],
    [
        Input(component_id="proj-dropdown", component_property="value"),
        Input(component_id="cs-dropdown", component_property="value"),
        Input(component_id="species-dropdown", component_property="value"),
    ],
)
def update_carbon_source(proj_chosen, col_chosen, species_chosen):
    # Read only data for selected project, species and carbon source
    df_data = pd.read_csv(
        join(parsed_data_dir, proj_chosen, proj_chosen + "_measurement_data.csv")
    )

    # Filter the appropriate linegroups and associated data
    lg_species_chosen = pooled_df_joint_metadata[
        pooled_df_joint_metadata["species"] == species_chosen
    ]["linegroup"]
    lg_carbon_source_chosen = pooled_df_joint_metadata[
        pooled_df_joint_metadata["carbon_source"] == col_chosen
    ]["linegroup"]
    filtered_lg = list(set(lg_species_chosen) & set(lg_carbon_source_chosen))
    df_data_filtered = df_data[df_data["linegroup"].isin(filtered_lg)].sort_values(
        by="time"
    )

    # Plot the data
    fig = px.line(df_data_filtered, x="time", y="measurement", line_group="linegroup")

    # Add chosen metadata as table
    filtered_metadata = pooled_df_joint_metadata[
        pooled_df_joint_metadata["linegroup"].isin(filtered_lg)
    ]
    table_data = (
        filtered_metadata[to_show_in_table].drop_duplicates().to_dict("records")
    )
    return fig, table_data


# Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=True)
