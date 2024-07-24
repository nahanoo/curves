from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
from os.path import join
import plotly.express as px
import plotly.graph_objects as go

df = pd.read_csv(join("data", "240623_growth_phenotyping", "at", "data_annotated.csv"))
species = list(set(df["species"]))

cs = list(set(df["carbon_source"]))
app = Dash()

# App layout
app.layout = [
    html.Div(children="Example data"),
    html.Hr(),
    dcc.Dropdown(cs, "D-glucose", id="cs-dropdown"),
    dcc.Dropdown(species, species[0], id="species-dropdown"),
    dcc.Graph(figure={}, id="controls-and-graph"),
]


# Add controls to build the interaction
@callback(
    Output(component_id="controls-and-graph", component_property="figure"),
    Input(component_id="cs-dropdown", component_property="value"),
    Input(component_id="species-dropdown", component_property="value"),
)
def update_carbon_source(col_chosen, species_chosen):
    df_filtered = df[
        (df["carbon_source"] == col_chosen) & (df["species"] == species_chosen)
    ].sort_values("Time")
    fig = px.line(df_filtered, x="Time", y="OD", line_group="linegroup")
    return fig


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
