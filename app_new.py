import pandas as pd
from dash import Dash, dcc, html, Input, Output, dash_table, callback
import plotly.express as px
from os.path import join

# Load the data
df_data = pd.read_csv(join("data", "parsed_csvs", "240623_growth_phenotyping_measurement_data.csv"))
df_species = pd.read_csv(join("data", "parsed_csvs", "240623_growth_phenotyping_species_data.csv"))
df_carbon_source = pd.read_csv(join("data", "parsed_csvs", "240623_growth_phenotyping_carbon_source_data.csv"))
df_run = pd.read_csv(join("data", "parsed_csvs", "240623_growth_phenotyping_run_data.csv"))
df_comments = pd.read_csv(join("data", "parsed_csvs", "240623_growth_phenotyping_comment_data.csv"))
df_inhibitor = pd.read_csv(join("data", "parsed_csvs", "240623_growth_phenotyping_inhibitor_data.csv"))
df_technical = pd.read_csv(join("data", "parsed_csvs", "240623_growth_phenotyping_technical_data.csv"))

# Get unique carbon sources and species
cs = list(set(df_carbon_source["carbon_source"]))
species = list(set(df_species["species"]))

# Create the Dash app
app = Dash(__name__)

# App layout
app.layout = html.Div(
    [
        html.Div(children="Example data"),
        html.Hr(),
        dcc.Dropdown(cs, cs[0], id="cs-dropdown"),
        dcc.Dropdown(species, species[0], id="species-dropdown"),
        dcc.Graph(figure={}, id="controls-and-graph"),
        # dash_table.DataTable(
        #     id="table",
        #     columns=[
        #         {"name": i, "id": i}
        #         for i in df[
        #             ["species", "carbon_source", "concentration", "project"]
        #         ].columns
        #     ],
        # ),
    ]
)


# Add controls to build the interaction
@callback(
    [
        Output(component_id="controls-and-graph", component_property="figure"),
        # Output(component_id="table", component_property="data"),
    ],
    [
        Input(component_id="cs-dropdown", component_property="value"),
        Input(component_id="species-dropdown", component_property="value"),
    ],
)
def update_carbon_source(col_chosen, species_chosen):
    lg_species_chosen = df_species[df_species["species"] == species_chosen]["linegroup"]
    lg_carbon_source_chosen = df_carbon_source[df_carbon_source["carbon_source"] == col_chosen]["linegroup"]
    filtered_lg = list(set(lg_species_chosen) & set(lg_carbon_source_chosen))
    df_data_filtered = df_data[df_data["linegroup"].isin(filtered_lg)]
    # df_filtered = df[
    #     (df["carbon_source"] == col_chosen) & (df["species"] == species_chosen)
    # ].sort_values("Time")
    fig = px.line(df_data_filtered, x="time", y="measurement", line_group="linegroup")
    # table_data = (
    #     df_filtered[["species", "carbon_source", "concentration", "project"]]
    #     .drop_duplicates()
    #     .to_dict("records")
    # )
    return fig


# Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=True)
