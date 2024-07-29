import pandas as pd
from dash import Dash, dcc, html, Input, Output, dash_table, callback
import plotly.express as px
from os.path import join

# Load the data
df = pd.read_csv(join("data", "240623_growth_phenotyping", "at", "data_annotated.csv"))

# Get unique carbon sources and species
cs = list(set(df["carbon_source"]))
species = list(set(df["species"]))

# Create the Dash app
app = Dash(__name__)

# App layout
app.layout = html.Div(
    [
        html.Div(children="Example data"),
        html.Hr(),
        dcc.Dropdown(cs, "D-glucose", id="cs-dropdown"),
        dcc.Dropdown(species, species[0], id="species-dropdown"),
        dcc.Graph(figure={}, id="controls-and-graph"),
        dash_table.DataTable(
            id="table",
            columns=[
                {"name": i, "id": i}
                for i in df[
                    ["species", "carbon_source", "concentration", "project"]
                ].columns
            ],
        ),
    ]
)


# Add controls to build the interaction
@callback(
    [
        Output(component_id="controls-and-graph", component_property="figure"),
        Output(component_id="table", component_property="data"),
    ],
    [
        Input(component_id="cs-dropdown", component_property="value"),
        Input(component_id="species-dropdown", component_property="value"),
    ],
)
def update_carbon_source(col_chosen, species_chosen):
    df_filtered = df[
        (df["carbon_source"] == col_chosen) & (df["species"] == species_chosen)
    ].sort_values("Time")
    fig = px.line(df_filtered, x="Time", y="OD", line_group="linegroup")
    table_data = (
        df_filtered[["species", "carbon_source", "concentration", "project"]]
        .drop_duplicates()
        .to_dict("records")
    )
    return fig, table_data


# Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=True)
