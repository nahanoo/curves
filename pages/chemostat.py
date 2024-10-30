import dash
from dash import dcc, html, callback, Output, Input, State, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import dash_daq as daq
from scipy.integrate import odeint
import numpy as np
import plotly.express as px

dash.register_page(__name__, path="/Chemostat", name="Chemostat", order=4)

w_param_names = 2
w_box = '70px'
layout = html.Div([
    dbc.Row(html.H2("Chemostat simulator")),
    dbc.Row([
        dbc.Col(html.Span('Km [mM]:'), width=w_param_names),
        dbc.Col(
            dcc.Input(id='input_Km',
                      type='number',
                      step=0.1,
                      value=1,
                      style={'width': w_box}))
    ]),
    dbc.Row([
        dbc.Col(html.Span('Maximum growth rate [1/h]:'), width=w_param_names),
        dbc.Col(
            dcc.Input(id='input_v',
                      min=0,
                      value=0.3,
                      type='number',
                      step=0.1,
                      style={'width': w_box}))
    ]),
    dbc.Row([
        dbc.Col(html.Span('Yield [OD/mM]:'), width=w_param_names),
        dbc.Col(
            dcc.Input(id='input_q',
                      min=0,
                      type='number',
                      value=0.1,
                      step=0.1,
                      style={'width': w_box}))
    ]),
    dbc.Row([
        dbc.Col(html.Span('Supply concentration [mM]:'), width=w_param_names),
        dbc.Col(
            dcc.Input(id='input_M',
                      min=0,
                      type='number',
                      value=10,
                      style={'width': w_box}))
    ]),
    dbc.Row([
        dbc.Col(html.Span('Dilution rate [1/h]:'), width=w_param_names),
        dbc.Col(
            dcc.Input(id='input_D',
                      min=0,
                      type='number',
                      value=0.1,
                      step=0.01,
                      style={'width': w_box}))
    ]),
    dbc.Row([
        dbc.Col(html.Span('Time [h]:'), width=w_param_names),
        dbc.Col(
            dcc.Input(id='input_t',
                      min=0,
                      type='number',
                      value=100,
                      style={'width': w_box}))
    ]),
    dbc.Row(html.H3("Species and resource dynamics"), class_name='pt-5'),
    dbc.Row([
        dbc.Col(dcc.Graph(figure={}, id='graph_N'), width=5),
        dbc.Col(dcc.Graph(figure={}, id='graph_R'), width=5)
    ]),
    dbc.Row(
        html.H3("R* and steady state species densities across dilution rates"),
        class_name='pt-5'),
    dbc.Row([
        dbc.Col(dcc.Graph(figure={}, id='graph_r_star'), width=5),
        dbc.Col(dcc.Graph(figure={}, id='graph_n_star'), width=5)
    ])
])


def model(y, t, Km, v, q, M, D):
    N, R = y
    dN = v * R / (R + Km) * N - D * N
    dR = D * M - v * R / (R + Km) * N / q - D * R
    return dN, dR


@callback([Output('graph_N', 'figure'),
           Output('graph_R', 'figure')], [
               Input('input_Km', 'value'),
               Input('input_v', 'value'),
               Input('input_q', 'value'),
               Input('input_M', 'value'),
               Input('input_D', 'value'),
               Input('input_t', 'value')
           ])
def plot(Km, v, q, M, D, t):
    xs = np.linspace(0, t, t * 10)
    y = odeint(model, [0.05, M], xs, args=(Km, v, q, M, D))
    N = px.line(x=xs, y=y[:, 0])
    N.update_layout(title='Species density')
    N.update_xaxes(title='Time [h]'), N.update_yaxes(title='OD')
    R = px.line(x=xs, y=y[:, 1])
    R.update_layout(title='Resource concentration')
    R.update_xaxes(title='Time [h]'), R.update_yaxes(
        title='Concentration [mM]')
    return N, R


@callback(Output('graph_r_star', 'figure'), [
    Input('input_Km', 'value'),
    Input('input_v', 'value'),
    Input('input_M', 'value')
])
def r_star_Ds(Km, v, M):
    D_crit = M * v / (Km + M)
    Ds = np.linspace(0.001, D_crit, 50)
    ys = [-D * Km / (D - v) for D in Ds]
    fig = px.line(x=Ds, y=ys)
    fig.update_layout(title='R* across dilution rates')
    fig.update_xaxes(title='Dilution rates [1/h]'), fig.update_yaxes(
        title='R* [mM]')
    return fig


@callback(Output('graph_n_star', 'figure'), [
    Input('input_Km', 'value'),
    Input('input_v', 'value'),
    Input('input_M', 'value'),
    Input('input_q', 'value'),
])
def n_star_Ds(Km, v, M, q):
    D_crit = M * v / (Km + M)
    Ds = np.linspace(0.001, D_crit, 50)
    R_stars = [-D * Km / (D - v) for D in Ds]
    N_stars = [
        D * q * (Km * M + R_star * (-Km + M - R_star)) / (R_star * v)
        for R_star, D in zip(R_stars, Ds)
    ]
    fig = px.line(x=Ds, y=N_stars)
    fig.update_layout(title='N* across dilution rates')
    fig.update_xaxes(title='Dilution rates [1/h]'), fig.update_yaxes(
        title='N* [OD]')
    return fig
