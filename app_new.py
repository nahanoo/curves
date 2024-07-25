import pandas as pd
from dash import Dash, dcc, html, Input, Output, dash_table, callback
import plotly.express as px
from os.path import join
from functools import reduce

# Load the data
df_data = pd.read_csv(join("data", "parsed_csvs", "240623_growth_phenotyping_measurement_data.csv"))
df_species = pd.read_csv(join("data", "parsed_csvs", "240623_growth_phenotyping_species_data.csv"))
df_carbon_source = pd.read_csv(join("data", "parsed_csvs", "240623_growth_phenotyping_carbon_source_data.csv"))
df_run = pd.read_csv(join("data", "parsed_csvs", "240623_growth_phenotyping_run_data.csv"))
df_comments = pd.read_csv(join("data", "parsed_csvs", "240623_growth_phenotyping_comment_data.csv"))
df_inhibitor = pd.read_csv(join("data", "parsed_csvs", "240623_growth_phenotyping_inhibitor_data.csv"))
df_technical = pd.read_csv(join("data", "parsed_csvs", "240623_growth_phenotyping_technical_data.csv"))

df_joint_technical = df_run.merge(df_technical, on="expID", how="outer")
df_joint_metadata = reduce(lambda x,y: pd.merge(x,y, on='linegroup', how='outer'), [df_joint_technical,df_species,df_carbon_source,df_comments])

to_show_in_table = ["project","Experimenter","Device","Temperature","species", "carbon_source", "cs_conc", "comments"]

# Get unique carbon sources and species
cs = list(set(df_carbon_source["carbon_source"]))
species = list(set(df_species["species"]))

cs.sort()
species.sort()

# Create the Dash app
app = Dash(__name__)
app.css.append_css({"external_url": "assets/style_new.css"})

# App layout

app.layout = html.Div(
    className="container",
    children=[
        html.H1(children="Example Data"),
        html.Hr(),
        html.Div(
            className="dropdown",
            children=[
                dcc.Dropdown(cs, cs[0], id="cs-dropdown"),
                dcc.Dropdown(species, species[0], id="species-dropdown"),
            ]
        ),
        html.Div(
            className="graph",
            children=[
                dcc.Graph(figure={}, id="controls-and-graph"),
            ]
        ),
        html.Div(
            className="table",
            children=[
                dash_table.DataTable(
                    id="table",
                    columns=[
                        {"name": i, "id": i}
                        for i in df_joint_metadata[to_show_in_table].columns
                    ],
                ),
            ]
        ),
    ]
)

# app.layout = html.Div(
#     style={
#         "fontFamily": "Arial, sans-serif",
#         "backgroundColor": "#f8f9fa",
#         "margin": "0",
#         "padding": "0"
#     },
#     children=[
#         html.Div(
#             className="container",
#             style={
#                 "margin": "20px",
#                 "padding": "20px",
#                 "backgroundColor": "#ffffff",
#                 "borderRadius": "8px",
#                 "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)"
#             },
#             children=[
#                 html.H1(
#                     children="Example Data",
#                     style={
#                         "textAlign": "center",
#                         "color": "#343a40"
#                     }
#                 ),
#                 html.Hr(),
#                 html.Div(
#                     className="dropdown",
#                     style={"margin": "10px 0"},
#                     children=[
#                         dcc.Dropdown(cs, cs[0], id="cs-dropdown"),
#                         dcc.Dropdown(species, species[0], id="species-dropdown"),
#                     ]
#                 ),
#                 html.Div(
#                     className="graph",
#                     style={"margin": "20px 0"},
#                     children=[
#                         dcc.Graph(figure={}, id="controls-and-graph"),
#                     ]
#                 ),
#                 html.Div(
#                     className="table",
#                     style={"margin": "20px 0"},
#                     children=[
#                         dash_table.DataTable(
#                             id="table",
#                             columns=[
#                                 {"name": i, "id": i}
#                                 for i in df_joint_metadata[
#                                     ["species", "carbon_source", "cs_conc", "comments"]
#                                 ].columns
#                             ],
#                         ),
#                     ]
#                 ),
#             ]
#         ),
#     ]
# )


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
    lg_species_chosen = df_species[df_species["species"] == species_chosen]["linegroup"]
    lg_carbon_source_chosen = df_carbon_source[df_carbon_source["carbon_source"] == col_chosen]["linegroup"]
    filtered_lg = list(set(lg_species_chosen) & set(lg_carbon_source_chosen))
    df_data_filtered = df_data[df_data["linegroup"].isin(filtered_lg)].sort_values(by="time")

    # dfs_filtered = []
    # for i in range(len(filtered_lg)):
    #     dfs_filtered.append(df_data[df_data["linegroup"] == filtered_lg[i]].sort_values(by="time"))
  
    fig = px.line(df_data_filtered, x="time", y="measurement", line_group="linegroup")

    filtered_metadata = df_joint_metadata[df_joint_metadata["linegroup"].isin(filtered_lg)]
    table_data = (
        filtered_metadata[to_show_in_table]
        .drop_duplicates()
        .to_dict("records")
    )
    return fig, table_data


# Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=True)
