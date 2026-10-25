
import plotly.express as px
from shiny import App, ui
from shinywidgets import output_widget, render_widget

from impute_sex import impute_sex
from load_dataset import load_raw_dataset
from transform_dataset import transform_raw_dataset

penguins = impute_sex(transform_raw_dataset(load_raw_dataset()))

variables = {
    "bill_length_mm": "Bill length (mm)",
    "bill_depth_mm": "Bill depth (mm)",
    "flipper_length_mm": "Flipper length (mm)",
    "body_mass_g": "Body mass (g)"
}

colors = {
    "Adelie": "darkorange",
    "Chinstrap": "purple",
    "Gentoo": "darkcyan"
}

symbols = {
    "Female": "circle-dot",
    "Male": "diamond-dot",
    "Unknown": "square-dot"
}

species_labels = {
    "Adelie": "Adélie",
    "Chinstrap": "Chinstrap",
    "Gentoo": "Gentoo"
}

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_select(
            "species",
            "Penguin species",
            choices=["All", "Adelie", "Chinstrap", "Gentoo"]
        ),
        ui.input_select(
            "x_var",
            "X-axis variable",
            choices=variables,
            selected="bill_length_mm"
        ),
        ui.input_select(
            "y_var",
            "Y-axis variable",
            choices=variables,
            selected="bill_depth_mm"
        ),
        ui.input_checkbox(
            "show_regression",
            "Show regression lines",
            value=False
        ),
        ui.input_radio_buttons(
            "split_by",
            "Split plot by",
            choices={"none": "None", "species": "Species", "island": "Island"},
            selected="none"
        )
    ),
    ui.h2("Palmer Penguins Dashboard"),
    ui.p("Morphological characteristics of penguins at Palmer Station LTER"),
    output_widget("scatterplot")
)


def server(input, output, session):

    @render_widget
    def scatterplot():
        df = penguins

        if input.species() != "All":
            df = df[df["species"] == input.species()]

        x_var = input.x_var()
        y_var = input.y_var()
        facet_col = None if input.split_by() == "none" else input.split_by()
        category_orders = {
            "species": list(colors),
            "sex": list(symbols),
            "island": ["Biscoe", "Dream", "Torgersen"],
        }
        # A species filter should produce only that species' panel.
        if input.species() != "All":
            category_orders["species"] = [input.species()]

        plot_options = {
            "x": x_var,
            "y": y_var,
            "color": "species",
            "color_discrete_map": colors,
            "facet_col": facet_col,
            "category_orders": category_orders,
            "labels": {
                **variables, "species": "Penguin species", "sex": "Sex",
                "island": "Island",
            },
        }

        fig = px.scatter(
            df,
            **plot_options,
            symbol="sex",
            symbol_map=symbols,
            hover_data=["island", "year"],
        )

        # Fit by species within each panel, independently of the sex symbols.
        if input.show_regression() and x_var != y_var:
            regression = px.scatter(df, **plot_options, trendline="ols")
            for trace in regression.data:
                if trace.mode == "lines":
                    trace.showlegend = False
                    fig.add_trace(trace)

        if facet_col == "island":
            for column, island in enumerate(category_orders["island"], start=1):
                if df.loc[df["island"] == island, [x_var, y_var]].dropna().empty:
                    fig.add_annotation(
                        text="No observations", showarrow=False,
                        x=0.5, y=0.5,
                        xref=f"x{column if column > 1 else ''} domain",
                        yref=f"y{column if column > 1 else ''} domain",
                    )

        fig.update_traces(
            marker={"size": 9, "opacity": 0.8, "line": {"width": 1}},
            selector={"mode": "markers"}
        )

        fig.update_layout(
            legend_title_text="Species, sex",
            margin={"t": 90}
        )

        return fig


app = App(app_ui, server)
