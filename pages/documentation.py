from dash import html, dcc, Input, Output, register_page
import dash_bootstrap_components as dbc

register_page(__name__, path="/Documentation", name="Documentation")  # '/' is home page

with open("documentation/documentation.md", "r") as handle:
    docs = handle.read()

layout = dcc.Markdown(docs)
