import dash
from dash import html, Input, Output, ALL,dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import os
from os.path import join
from functools import reduce

# Load data
parsedDataDir = "data/parsed_csvs"
parsedProjects = next(os.walk(parsedDataDir))[1]
parsedProjects.sort()

project = parsedProjects[0]
pooled_df_joint_metadata = pd.DataFrame()

for project in parsedProjects:
    df_species = pd.read_csv(join("data", "parsed_csvs", project, project + "_species_data.csv"))
    df_carbon_source = pd.read_csv(join("data", "parsed_csvs", project, project + "_carbon_source_data.csv"))
    df_technical = pd.read_csv(join("data", "parsed_csvs", project, project + "_technical_data.csv"))
    df_comments = pd.read_csv(join("data", "parsed_csvs", project, project + "_comment_data.csv"))
    df_run = pd.read_csv(join("data", "parsed_csvs", project, project + "_run_data.csv"))
    df_inhibitor = pd.read_csv(join("data", "parsed_csvs", project, project + "_inhibitor_data.csv"))

    df_joint_technical = df_run.merge(df_technical, on="expID", how="outer")
    df_joint_metadata = reduce(lambda x, y: pd.merge(x, y, on='linegroup', how='outer'),
                               [df_joint_technical, df_species, df_carbon_source, df_comments])
    pooled_df_joint_metadata = pd.concat([pooled_df_joint_metadata, df_joint_metadata])

cs = list(set(pooled_df_joint_metadata["carbon_source"]))
species = list(set(pooled_df_joint_metadata["species"]))

cs.sort()
species.sort()

def generate_checklist(options, index):
    return dbc.Checklist(
        options=[{'label': opt, 'value': opt} for opt in options],
        id={'type': 'checkboxes', 'index': index}
    )

# Create the table columns
carbon_source_checklist = generate_checklist(cs, 'carbon_source')
species_checklist = generate_checklist(species, 'species')

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

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

@app.callback(
    Output(component_id="controls-and-graph", component_property="figure"),
    Input({'type': 'checkboxes', 'index': ALL}, 'value'),
    
)
def update_div(value_in):

    if value_in is None or not any(value_in):
        return dash.no_update

    chosen_carbon_sources = value_in[0] if value_in[0] else []
    chosen_species = value_in[1] if value_in[1] else []

    if not chosen_carbon_sources or not chosen_species:
        return dash.no_update

    lg_species = pooled_df_joint_metadata[pooled_df_joint_metadata["species"].isin(chosen_species)]
    lg_carbon_source = lg_species[lg_species["carbon_source"].isin(chosen_carbon_sources)]
    common_lg = list(set(lg_carbon_source["linegroup"]) & set(lg_species["linegroup"]))

    projects_chosen = pooled_df_joint_metadata[pooled_df_joint_metadata["linegroup"].isin(common_lg)]["project"].unique()

    dfs = []

    for project in projects_chosen:
        dfs.append(pd.read_csv(join("data", "parsed_csvs", project, project + "_measurement_data.csv")))
        
    df_data = pd.concat(dfs)

    df_data = df_data[df_data["linegroup"].isin(common_lg)].sort_values(by="time")
                        
    fig = px.line(df_data, x="time", y="measurement", line_group="linegroup")

    return fig


@app.callback(
    Output("download-data", "data"),
    Input("download-btn", "n_clicks"),
    prevent_initial_call=True
)
def download_data(n_clicks):
    if n_clicks is None:
        return dash.no_update


if __name__ == '__main__':
    app.run_server(debug=True)
