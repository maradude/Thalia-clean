import dash_core_components as dcc
import dash_html_components as html

from .tab_elements.returns import returns_dashboard
from .tab_elements.summary import summary_dashboard
from .tab_elements.allocations import options_wrapper
from .tab_elements.metrics import table
from .tab_elements.overfitting import overfitting_test
from .tab_elements.drawdowns import drawdowns_dashboard

tabs_styles = {"height": "44px"}
tab_style = {
    "borderBottom": "1px solid #d6d6d6",
    "padding": "6px",
    "fontWeight": "bold",
}

tab_selected_style = {
    "borderTop": "1px solid #d6d6d6",
    "borderBottom": "1px solid #d6d6d6",
    "backgroundColor": "#f26a4b",
    "color": "white",
    "padding": "6px",
}

tab_disabled_style = {
    "borderTop": "1px solid #d6d6d6",
    "borderBottom": "1px solid #d6d6d6",
    "backgroundColor": "#d6d6d6",
    "color": "white",
    "padding": "6px",
}


def title(title):
    return html.Div(
        html.H1(title, className="title"),
        className="column is-12",
        style={"padding-top": "2cm", "padding-bottom": "1cm"},
    )


def allocations():
    return dcc.Tab(
        label="Allocations",
        children=[title("Select Constraints"), options_wrapper()],
        style=tab_style,
        selected_style=tab_selected_style,
        disabled_style=tab_disabled_style,
        id="allocations",
        value="allocations",
        disabled=False,
        className="has-text-vcentered",
    )


def summary():
    return dcc.Tab(
        label="Summary",
        children=[title("Portfolio Summary"), summary_dashboard()],
        style=tab_style,
        selected_style=tab_selected_style,
        disabled_style=tab_disabled_style,
        id="summary",
        value="summary",
        disabled=True,
    )


def metrics():
    return dcc.Tab(
        label="Metrics",
        children=[title("Key Metrics"), dcc.Loading(table([], "key_metrics_table"))],
        style=tab_style,
        selected_style=tab_selected_style,
        disabled_style=tab_disabled_style,
        id="metrics",
        value="metrics",
        disabled=True,
    )


def returns():
    return dcc.Tab(
        label="Returns",
        children=[title("Returns"), returns_dashboard()],
        style=tab_style,
        selected_style=tab_selected_style,
        disabled_style=tab_disabled_style,
        id="returns",
        value="returns",
        disabled=True,
    )


def drawdowns():
    return dcc.Tab(
        label="Drawdowns",
        children=[title("Drawdowns"), dcc.Loading(drawdowns_dashboard())],
        style=tab_style,
        selected_style=tab_selected_style,
        disabled_style=tab_disabled_style,
        id="drawdowns",
        value="drawdowns",
        disabled=True,
    )


def assets():
    return dcc.Tab(
        label="Assets",
        children=[
            title("Assets Breakdown"),
            dcc.Loading(
                html.Div(id="assets-container", className="columns is-multiline")
            ),
        ],
        style=tab_style,
        selected_style=tab_selected_style,
        disabled_style=tab_disabled_style,
        id="assets",
        value="assets",
        disabled=True,
    )


def overfitting():
    return dcc.Tab(
        label="Overfitting",
        children=[title("Overfitting"), overfitting_test()],
        style=tab_style,
        selected_style=tab_selected_style,
        disabled_style=tab_disabled_style,
        id="overfitting",
        value="overfitting",
        disabled=True,
    )
