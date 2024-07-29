import dash
from dash import html, dcc, Input, Output, ALL, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from io import BytesIO
import os
from os.path import join
from functools import reduce
import zipfile

# Load data
parsed_data_dir = "data/parsed_csvs"
parsed_projects = next(os.walk(parsed_data_dir))[1]
parsed_projects.sort()

pooled_df_joint_metadata = pd.DataFrame()

for project in parsed_projects:
    # Load data
    df_species = pd.read_csv(join("data", "parsed_csvs", project, project + "_species_data.csv"))
    df_carbon_source = pd.read_csv(join("data", "parsed_csvs", project, project + "_carbon_source_data.csv"))
    df_technical = pd.read_csv(join("data", "parsed_csvs", project, project + "_technical_data.csv"))
    df_comments = pd.read_csv(join("data", "parsed_csvs", project, project + "_comment_data.csv"))
    df_run = pd.read_csv(join("data", "parsed_csvs", project, project + "_run_data.csv"))
    df_inhibitor = pd.read_csv(join("data", "parsed_csvs", project, project + "_inhibitor_data.csv"))

    # Merge data with expID as common columns
    df_joint_technical = df_run.merge(df_technical, on="expID", how="outer")

    # Merge all metadata with linegroup as common reference
    df_joint_metadata = reduce(lambda x, y: pd.merge(x, y, on='linegroup', how='outer'),
                               [df_joint_technical, df_species, df_carbon_source, df_comments])
    pooled_df_joint_metadata = pd.concat([pooled_df_joint_metadata, df_joint_metadata])

# Get unique carbon sources and species
cs = list(set(pooled_df_joint_metadata["carbon_source"]))
species = list(set(pooled_df_joint_metadata["species"]))
cs.sort()
species.sort()

# Function to generate checklist for carbon source and species
def generate_checklist(options, index):
    return dbc.Checklist(
        options=[{'label': opt, 'value': opt} for opt in options],
        id={'type': 'checkboxes', 'index': index}
    )

# Create the table columns
carbon_source_checklist = generate_checklist(cs, 'carbon_source')
species_checklist = generate_checklist(species, 'species')

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# App layout with checklist, graph and download button
app.layout = html.Div(
    [
        dbc.Table(
            [
                html.Thead(
                    html.Tr([html.Th("carbon_source"), html.Th("species")])
                ),
                html.Tbody(
                    html.Tr([html.Td(carbon_source_checklist), html.Td(species_checklist)])
                )
            ],
            bordered=True,
            responsive=True,
            style={"width": "100vw"}
        ),
        html.Div(
            className="graph",
            children=[
                dcc.Graph(figure={}, id="controls-and-graph"),
            ]
        ),
        html.Button("Download Data", id="download-btn"),
        dcc.Download(id="download-data")
    ]
)

# Update graph based on selected carbon sources and species
@app.callback(
    Output(component_id="controls-and-graph", component_property="figure"),
    Input({'type': 'checkboxes', 'index': ALL}, 'value'),
)
def update_graph(value_in):
    # Check for when no values are selected
    if value_in is None or not any(value_in):
        return dash.no_update

    chosen_carbon_sources = value_in[0] if value_in[0] else []
    chosen_species = value_in[1] if value_in[1] else []

    if not chosen_carbon_sources or not chosen_species:
        return dash.no_update

    # Filter linegroup based on selected carbon sources and species
    lg_species = pooled_df_joint_metadata[pooled_df_joint_metadata["species"].isin(chosen_species)]
    lg_carbon_source = lg_species[lg_species["carbon_source"].isin(chosen_carbon_sources)]
    common_lg = list(set(lg_carbon_source["linegroup"]) & set(lg_species["linegroup"]))

    # Choose projects based on linegroups
    projects_chosen = pooled_df_joint_metadata[pooled_df_joint_metadata["linegroup"].isin(common_lg)]["project"].unique()

    # Load only selected projects
    dfs = []
    for project in projects_chosen:
        dfs.append(pd.read_csv(join("data", "parsed_csvs", project, project + "_measurement_data.csv")))

    df_data = pd.concat(dfs)
    
    # Plot data for visual representation
    df_data = df_data[df_data["linegroup"].isin(common_lg)].sort_values(by="time")
    fig = px.line(df_data, x="time", y="measurement", line_group="linegroup")

    return fig

# Download data based on selected carbon sources and species
@app.callback(
    Output("download-data", "data"),
    Input("download-btn", "n_clicks"),
    State({'type': 'checkboxes', 'index': ALL}, 'value'),
    prevent_initial_call=True
)
def download_data(n_clicks, checkbox_values):
    # Check for when button is not clicked yet
    if n_clicks is None:
        return dash.no_update
    
    # Extract checkbox values
    chosen_carbon_sources = checkbox_values[0] if checkbox_values[0] else []
    chosen_species = checkbox_values[1] if checkbox_values[1] else []

    # Filter data based on checkbox selection
    filter_metadata = pooled_df_joint_metadata[
        (pooled_df_joint_metadata["carbon_source"].isin(chosen_carbon_sources)) &
        (pooled_df_joint_metadata["species"].isin(chosen_species))
    ]

    # Assuming measurement data is stored separately or needs to be re-fetched
    measurement_data_frames = []
    for project in filter_metadata['project'].unique():
        df_measurements = pd.read_csv(join(parsed_data_dir, project, project + "_measurement_data.csv"))
        measurement_data_frames.append(df_measurements)

    # Combine measurement data from selected projects
    df_measurements = pd.concat(measurement_data_frames)
    df_measurements = df_measurements[df_measurements['linegroup'].isin(filter_metadata['linegroup'].unique())]
    
    # Pivot data to have linegroups as columns, indexed by time
    measurement_pivot = df_measurements.pivot_table(index='time', columns='linegroup', values='measurement', aggfunc='first')

    # Create a Bytes buffer to hold the ZIP file
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Save metadata CSV
        zf.writestr('metadata.csv', filter_metadata.to_csv(index=False))
        # Save measurement pivot CSV
        zf.writestr('measurements.csv', measurement_pivot.to_csv())

    # Prepare buffer for download
    zip_buffer.seek(0)
    return dcc.send_bytes(zip_buffer.getvalue(), "downloaded_data.zip")

if __name__ == '__main__':
    app.run_server(debug=True)
