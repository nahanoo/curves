from dash import dcc, html, register_page
import dash_bootstrap_components as dbc


register_page(__name__, path="/Contact", name="Contact", order=4)  # '/' is home page


layout = html.Div(
    [
        dbc.Row(html.H1("Contact")),
        dbc.Row(
            [
                html.Span(
                    [
                        "MonOD is developed by postdoc ",
                        html.A(
                            "Prajwal Padmanabha",
                            href="https://applicationspub.unil.ch/interpub/noauth/php/Un/UnPers.php?PerNum=1262133&LanCode=8",
                        ),
                        " and PhD student ",
                        html.A(
                            "Eric Ulrich",
                            href="https://applicationspub.unil.ch/interpub/noauth/php/Un/UnPers.php?PerNum=1242399&LanCode=8",
                        ),
                        ", both members of the ",
                        html.A(
                            "Mitri lab",
                            href="https://wp.unil.ch/mitrilab/",
                        ),
                        ".",
                    ]
                ),
            ]
        ),
    ]
)
