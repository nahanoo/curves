from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
from os.path import join
import plotly.express as px
import plotly.graph_objects as go

df = pd.read_csv(join("test_data", "240619_alisson", "data_annotated.csv"))

app = Dash()

# App layout
app.layout = [
    html.Div(children='Example data'),
    html.Hr(),
    dcc.RadioItems(options=['sample', 'species'], value='sample', id='controls-and-radio-item'),
    dcc.Graph(figure={}, id='controls-and-graph')
]

# Add controls to build the interaction
@callback(
    Output(component_id='controls-and-graph', component_property='figure'),
    Input(component_id='controls-and-radio-item', component_property='value')
)
def update_graph(col_chosen):
    fig = px.line(df, x='Time', y='OD',color=col_chosen)
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)

# branch testing comment