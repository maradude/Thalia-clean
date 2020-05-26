import dash_html_components as html
import dash_core_components as dcc


def overfitting_button():
    return html.Div(
        html.Button(
            "Check Overfitting",
            id="overfitting-btn",
            className="button is-large is-primary",
            style={"background-color": "#f26a4b"},
        ),
        className="container has-text-centered",
    )


def overfitting_test():
    return html.Div(
        [
            html.Div(overfitting_button(), className="columns is-centered "),
            dcc.Store(id="portfolio-results"),
            html.Div(
                dcc.Loading(
                    html.Div(id="overfitting-results", style={"margin": "1rem"})
                ),
                className="columns is-centered",
            ),
        ],
    )
