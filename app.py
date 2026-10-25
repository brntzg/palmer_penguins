
import plotly.express as px
from plotly.subplots import make_subplots
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
    output_widget("scatterplot", height="70vh")
)


def build_scatterplot(data, species, x_var, y_var, split_by, show_regression):
    """Build populated panels with data-driven ranges and per-panel axis titles."""
    df = data if species == "All" else data[data["species"] == species]
    df = df.dropna(subset=[x_var, y_var])
    facet_col = None if split_by == "none" else split_by
    panels = {
        "none": [None],
        "species": list(colors) if species == "All" else [species],
        "island": ["Biscoe", "Dream", "Torgersen"],
    }[split_by]
    empty_panels = []
    if facet_col is not None:
        empty_panels = [panel for panel in panels if df[df[facet_col] == panel].empty]
        panels = [panel for panel in panels if panel not in empty_panels]
    # Keep one panel for a genuinely empty selection.
    panels = panels or [None]
    titles = [] if facet_col is None or panels == [None] else [
        f"{facet_col.title()}={species_labels.get(panel, panel)}" for panel in panels
    ]
    fig = make_subplots(
        rows=1, cols=len(panels), shared_xaxes="all", shared_yaxes="all",
        subplot_titles=titles, horizontal_spacing=0.09,
    )
    legend_entries = set()
    populated_columns = []
    for column, panel in enumerate(panels, start=1):
        panel_df = df if facet_col is None else df[df[facet_col] == panel]
        if panel_df.empty:
            fig.add_annotation(
                text="No observations", showarrow=False, x=0.5, y=0.5,
                xref="paper", yref="paper",
            )
            fig.update_xaxes(visible=False, row=1, col=column)
            fig.update_yaxes(visible=False, row=1, col=column)
            continue

        populated_columns.append(column)
        plot_options = {
            "x": x_var, "y": y_var, "color": "species",
            "color_discrete_map": colors,
            "category_orders": {"species": list(colors), "sex": list(symbols)},
            "labels": {**variables, "species": "Penguin species", "sex": "Sex"},
        }
        scatter = px.scatter(
            panel_df, **plot_options, symbol="sex", symbol_map=symbols,
            hover_data=["island", "year"],
        )
        for trace in scatter.data:
            if not len(trace.x):
                continue
            trace.showlegend = trace.name not in legend_entries
            legend_entries.add(trace.name)
            fig.add_trace(trace, row=1, col=column)

        if show_regression and x_var != y_var:
            regression = px.scatter(panel_df, **plot_options, trendline="ols")
            for trace in regression.data:
                if trace.mode == "lines":
                    trace.showlegend = False
                    fig.add_trace(trace, row=1, col=column)

    # Explicit padded ranges avoid zero-based ranges from empty axes or annotations.
    def padded_range(variable):
        low, high = float(df[variable].min()), float(df[variable].max())
        padding = (high - low) * 0.07 or max(abs(low) * 0.07, 0.5)
        return [low - padding, high + padding]

    for column in populated_columns:
        fig.update_xaxes(
            title_text=variables[x_var], title_standoff=12,
            range=padded_range(x_var), autorange=False,
            showticklabels=True, automargin=True, row=1, col=column,
        )
        fig.update_yaxes(
            title_text=variables[y_var], title_standoff=12,
            range=padded_range(y_var), autorange=False,
            showticklabels=True, automargin=True, row=1, col=column,
        )
    if empty_panels and not df.empty:
        fig.add_annotation(
            text="No observations: " + ", ".join(empty_panels),
            x=0.5, y=-0.22, xref="paper", yref="paper", showarrow=False,
            xanchor="center", yanchor="top",
        )
    fig.update_traces(
        marker={"size": 9, "opacity": 0.8, "line": {"width": 1}},
        selector={"mode": "markers"},
    )
    fig.update_layout(
        template="plotly", legend_title_text="Species, sex",
        height=650, margin={"t": 70, "b": 130, "l": 80},
    )
    return fig


def server(input, output, session):
    @render_widget
    def scatterplot():
        return build_scatterplot(
            penguins, input.species(), input.x_var(), input.y_var(),
            input.split_by(), input.show_regression(),
        )


app = App(app_ui, server)
