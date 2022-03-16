import glob
import pickle

import dash
import dash_table as dt
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
import os

#word 2 vec
import gensim
from gensim.models import word2vec as w2v
from datetime import datetime



# based on: https://github.com/plotly/dash-sample-apps/blob/master/apps/dash-tsne/demo.py

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# read and process data
# TODO - hard coded models files (partial data)
data_dict = {
    "batch52_300t": r"/Volumes/GoogleDrive/My Drive/PhD/Projects/gene2vec/global_sewage/trained_models/ALL/batch_52",
    "batch52_300u": r"/Volumes/GoogleDrive/My Drive/PhD/Projects/gene2vec/global_sewage/trained_models/ALL/batch_52",
    "batch87_512t": r"/Volumes/GoogleDrive/My Drive/PhD/Projects/gene2vec/global_sewage/trained_models/ALL/batch_87",
    "batch87_512u": r"/Volumes/GoogleDrive/My Drive/PhD/Projects/gene2vec/global_sewage/trained_models/ALL/batch_87",
}

WORD_EMBEDDINGS = ("batch87_512u","batch87_512t","batch52_300u", "batch52_300t", "batch1717_300u", "batch1717_512u")
METADATA = pd.read_csv(r"/Users/daniellemiller/Google Drive/PhD/Projects/gene2vec/ko_data/metadata.csv")
TABLE_COLS = ["word", "Product", "label", "cluster"]


def load_data_for_app(dataset):
    if dataset.endswith("u"):
        alias="umap"
    else:
        alias = "tsne"
    mdl_files = glob.glob(f"{data_dict[dataset]}/*")
    embedding_path = [f for f in mdl_files if f"words_{alias}" in f][0]
    mdl_path = [f for f in mdl_files if f.endswith("w2v")][0]

    with open(embedding_path, 'rb') as handle:
        embedding_df = pickle.load(handle)
    g2v = w2v.Word2Vec.load(mdl_path)

    embedding_df["KO"] = embedding_df["word"]
    embedding_df["hypothetical"] = embedding_df["word"].apply(lambda x: "YES" if "Cluster" in x else "NO")
    embedding_df = embedding_df.merge(METADATA, on=["KO"], how="left").fillna("unknown")
    clustering_data = pd.read_csv(os.path.join(data_dict[dataset], f"{alias}_clusters.csv"))
    clustering_data["cluster"] = clustering_data["cluster"].astype(str)
    embedding_df = embedding_df.merge(clustering_data, on=["word"], how="left")

    return embedding_df, g2v



# Methods for creating components in the layout code
def Card(children, **kwargs):
    return html.Section(children, className="card-style")


def NamedSlider(name, short, min, max, step, val, marks=None):
    if marks:
        step = None
    else:
        marks = {i: i for i in range(min, max + 1, step)}

    return html.Div(
        style={"margin": "25px 5px 30px 0px"},
        children=[
            f"{name}:",
            html.Div(
                style={"margin-left": "5px"},
                children=[
                    dcc.Slider(
                        id=f"slider-{short}",
                        min=min,
                        max=max,
                        marks=marks,
                        step=step,
                        value=val,
                    )
                ],
            ),
        ],
    )


def NamedInlineRadioItems(name, short, options, val, **kwargs):
    return html.Div(
        id=f"div-{short}",
        style={"display": "inline-block"},
        children=[
            f"{name}:",
            dcc.RadioItems(
                id=f"radio-{short}",
                options=options,
                value=val,
                labelStyle={"display": "inline-block", "margin-right": "7px"},
                style={"display": "inline-block", "margin-left": "7px"},
            ),
        ],
    )


def create_layout(app):
    # Actual layout of the app
    return html.Div(
        className="row",
        style={"max-width": "100%", "font-size": "1.5rem", "padding": "0px 0px"},
        children=[
            # Header
            html.Div(
                className="row header",
                id="app-header",
                style={"background-color": "#f9f9f9"},
                children=[
                    html.Div(
                        [
                            html.H3(
                                "Gene Space Explorer",
                                className="header_title",
                                id="app-title",
                            )
                        ],
                        className="nine columns header_title_container",
                    ),
                ],
            ),
            # Body
            html.Div(
                className="row background",
                style={"padding": "10px"},
                children=[
                    html.Div(
                        className="three columns",
                        children=[
                            Card(
                                [
                                    dcc.Dropdown(
                                        id="dropdown-dataset",
                                        searchable=False,
                                        clearable=False,
                                        options=[
                                            {
                                                "label": "BATCH 87 UMAP (V512)",
                                                "value": "batch87_512u",
                                            },
                                            {
                                                "label": "BATCH 87 tSNE (V512)",
                                                "value": "batch87_512t",
                                            },
                                            {
                                                "label": "BATCH 52 UMAP (V300)",
                                                "value": "batch52_300u",
                                            },
                                            {
                                                "label": "BATCH 52 tSNE (V300)",
                                                "value": "batch52_300t",
                                            },
                                            {
                                                "label": "BATCH 1717 UMAP (V300)",
                                                "value": "batch1717_300u",
                                            },
                                            {
                                                "label": "BATCH 1717 UMAP (V512)",
                                                "value": "batch1717_512u",
                                            },
                                        ],
                                        placeholder="Select a dataset",
                                        value="batch52_300u",
                                    ),
                                    NamedSlider(
                                        name="Opacity",
                                        short="opacity",
                                        min=0.1,
                                        max=1,
                                        step=None,
                                        val=0.2,
                                        marks={
                                            i: str(i) for i in [0.2, 0.5, 0.8, 1]
                                        },
                                    ),
                                    NamedSlider(
                                        name="Size",
                                        short="size",
                                        min=4,
                                        max=10,
                                        step=None,
                                        val=4,
                                        marks={i: str(i) for i in [4, 6, 8, 10]},
                                    ),
                                    html.Div(
                                        id="div-wordemb-controls",
                                        style={"display": "none"},
                                        children=[
                                            NamedInlineRadioItems(
                                                name="Display Mode",
                                                short="wordemb-display-mode",
                                                options=[
                                                    {
                                                        "label": " Regular",
                                                        "value": "regular",
                                                    },
                                                    {
                                                        "label": " Top-50 Neighbors",
                                                        "value": "neighbors",
                                                    },
                                                ],
                                                val="regular",
                                            ),
                                            dcc.Dropdown(
                                                id="dropdown-word-selected",
                                                placeholder="Select word to display its neighbors",
                                                style={"background-color": "#F7ECEC"},
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        id="div-search-ko",
                                        style={"display": "none", "margin": "25px 5px 30px 0px"},
                                        children=[
                                            html.Br(),
                                            html.Br(),
                                            html.Br(),
                                            html.I(
                                                "Search KO"),
                                            html.Br(),
                                            dcc.Input(id="input-ko",
                                                      type="text",
                                                      placeholder="Type any KO in gene spcae",
                                                      debounce=True,
                                                      size='35',
                                                      ),
                                            html.Div(id="output"),
                                        ]
                                    )
                                ]
                            )
                        ],
                    ),
                    html.Div(
                        className="six columns",
                        children=[
                            dcc.Graph(id="graph-2d-plot-tsne", style={"height": "98vh"})
                        ],
                    ),
                    html.Div(
                        className="three columns",
                        id="euclidean-distance",
                        children=[
                            Card(
                                style={"padding": "5px"},
                                children=[
                                    html.Div(
                                        id="div-plot-click-message",
                                        style={
                                            "text-align": "center",
                                            "margin-bottom": "7px",
                                            "font-weight": "bold",
                                        },
                                    ),
                                    html.Div(id="div-plot-click-wordemb"),
                                ],
                            )
                        ],
                    ),
                ],
            ),
            # Table
            html.Div(
                className="row table",
                style={"padding": "10px"},
                children=[
                    html.Div(
                        className="three columns",
                        children=[
                            Card(
                                [
                                    html.Div(
                                        id="div-table-controls",
                                        style={"display": "none"},
                                        children=[
                                            NamedInlineRadioItems(
                                                name="Color mode",
                                                short="table-display-mode",
                                                options=[
                                                    {
                                                        "label": " Label",
                                                        "value": "label",
                                                    },
                                                    {
                                                        "label": " Cluster",
                                                        "value": "cluster",
                                                    },
                                                    {
                                                        "label": " Hypothetical",
                                                        "value": "hypothetical",
                                                    },
                                                ],
                                                val="label",
                                            ),
                                            dcc.Dropdown(
                                                id="dropdown-label-selected",
                                                placeholder="Select groups to display on main graph",
                                                multi=True,
                                                style={"background-color": "#F7ECEC"},
                                            ),
                                        ],
                                    ),
                                ]
                            )
                        ],
                    ),
                    html.Div(
                        className="nine columns",
                        children=[
                            dt.DataTable(
                                id='info-table',
                                columns=[{"name": i, "id": i} for i in TABLE_COLS],
                                style_table={
                                    'display': 'inline-block',
                                },
                                fixed_rows={'headers': True},
                                page_size=20,
                                style_cell={
                                    "text-align": "left",
                                    "font-family": "Geneva",
                                    "backgroundColor": "#F7ECEC",
                                    "color": "#656060",
                                    'textOverflow': 'ellipsis',
                                    'overflow': 'hidden',
                                    'minWidth': '200px',
                                    'width': '2000px',
                                    'maxWidth': '200px',
                                },
                                tooltip_duration=None
                            ),
                        ],
                    ),
                ],
            ),
        ],

    )


def demo_callbacks(app):

    # Scatter Plot of the t-SNE datasets
    def generate_figure_word_vec(
            embedding_df, layout, wordemb_display_mode, selected_word, mdl, size, opacity, table_display_mode,
    ):

        try:
            # Regular displays the full scatter plot with only circles
            if wordemb_display_mode == "regular":
                plot_mode = "markers"

            # Nearest Neighbors displays only the 100 nearest neighbors of the selected_word, in text rather than circles
            elif wordemb_display_mode == "neighbors":
                if not selected_word:
                    return go.Figure(layout=layout)

                plot_mode = "text"

                # Get the nearest neighbors indices using Cosine distance
                neighbors = [c[0] for c in mdl.wv.most_similar(selected_word, topn=50)] + [selected_word]

                # Select those neighbors from the embedding_df
                embedding_df = embedding_df[embedding_df["word"].isin(neighbors)]
            legend=False
            if table_display_mode == "hypothetical":
                legend = True
            figure = px.scatter(embedding_df.sort_values(by=["word"]), x="x", y="y", color=table_display_mode, opacity=opacity,
                                color_discrete_sequence=px.colors.qualitative.Plotly[::-1], text="word",
                                custom_data=['word', 'Product', 'KO_lvl_3', 'hypothetical', 'label'])
            figure.update_traces(
                hovertemplate="<br>".join([
                    "word: %{customdata[0]}",
                    "Product: %{customdata[1]}",
                    "KO_lvl_3: %{customdata[2]}",
                    "hypothetical: %{customdata[3]}",
                    "label: %{customdata[4]}",
                ]), marker=dict(size=size), mode=plot_mode,
            )
            figure.update_layout(layout, showlegend=legend)
            return figure

        except KeyError as error:
            print(error)
            raise PreventUpdate


    @app.callback(
        Output("div-search-ko", "style"), [Input("dropdown-dataset", "value")]
    )
    def show_wordemb_controls(dataset):
        if dataset in WORD_EMBEDDINGS:
            return None
        else:
            return {"display": "none"}

    @app.callback(
        Output("div-wordemb-controls", "style"), [Input("dropdown-dataset", "value")]
    )
    def show_wordemb_controls(dataset):
        if dataset in WORD_EMBEDDINGS:
            return None
        else:
            return {"display": "none"}

    @app.callback(
        Output("dropdown-word-selected", "disabled"),
        [Input("radio-wordemb-display-mode", "value")],
    )
    def disable_word_selection(mode):
        return not mode == "neighbors"

    @app.callback(
        Output("div-table-controls", "style"), [Input("dropdown-dataset", "value")]
    )
    def show_table_controls(dataset):
        if dataset in WORD_EMBEDDINGS:
            return None
        else:
            return {"display": "none"}

    @app.callback(
        Output("dropdown-word-selected", "options"),
        [Input("dropdown-dataset", "value")],
    )
    def fill_dropdown_word_selection_options(dataset):
        embedding_df, mdl = load_data_for_app(dataset)
        if dataset in WORD_EMBEDDINGS:
            return [
                {"label": i, "value": i} for i in embedding_df["word"].tolist()
            ]
        else:
            return []

    @app.callback(
        Output("dropdown-label-selected", "options"),
        [Input("dropdown-dataset", "value"),
         Input("radio-table-display-mode", "value")],
    )
    def fill_dropdown_label_selection_options(dataset, label):
        embedding_df, mdl = load_data_for_app(dataset)
        return [{"label": i, "value": i} for i in embedding_df[label].unique()]

    @app.callback(
        [Output("graph-2d-plot-tsne", "figure"),Output("info-table", "data"), Output("info-table", "tooltip_data")],
        [
            Input("dropdown-dataset", "value"),
            Input("slider-opacity", "value"),
            Input("slider-size", "value"),
            Input("dropdown-word-selected", "value"),
            Input("radio-wordemb-display-mode", "value"),
            Input("radio-table-display-mode", "value"),
            Input("dropdown-label-selected", "value")
        ],
    )
    def display_scatter_plot_and_table(
            dataset,
            opacity,
            size,
            selected_word,
            wordemb_display_mode,
            table_display_mode,
            selected_label,
    ):
        if dataset:
            try:
                embedding_df, mdl = load_data_for_app(dataset)

            except FileNotFoundError as error:
                print(
                    error,
                    "\nThe dataset was not found. Please generate it using generate_demo_embeddings.py",
                )
                return go.Figure()

            # Plot layout
            axes = dict(title="", showgrid=True, zeroline=False, showticklabels=False)

            layout = go.Layout(
                margin=dict(l=0, r=0, b=0, t=0),
                scene=dict(xaxis=axes, yaxis=axes, zaxis=axes),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
            )

            # Everything else is word embeddings
            if dataset in WORD_EMBEDDINGS:
                if selected_label is None or selected_label == []:
                    figure = generate_figure_word_vec(
                        embedding_df=embedding_df,
                        layout=layout,
                        wordemb_display_mode=wordemb_display_mode,
                        selected_word=selected_word,
                        mdl=mdl,
                        size=size,
                        opacity=opacity,
                        table_display_mode=table_display_mode,
                    )
                    table = embedding_df[TABLE_COLS].to_dict('records')

                else:
                    dff = embedding_df.copy()
                    dff[table_display_mode] = dff[table_display_mode].apply(lambda x: x if x in selected_label else "no")
                    figure = generate_figure_word_vec(
                        embedding_df=dff,
                        layout=layout,
                        wordemb_display_mode=wordemb_display_mode,
                        selected_word=selected_word,
                        mdl=mdl,
                        size=size,
                        opacity=opacity,
                        table_display_mode=table_display_mode,
                    )
                    table = embedding_df[embedding_df[table_display_mode].isin(selected_label)][TABLE_COLS].to_dict('records')

            else:
                figure = go.Figure(layout=layout)
                table = embedding_df[TABLE_COLS].to_dict('records')

            tooltip_data = [{column: {'value': str(value), 'type': 'markdown'}
                             for column, value in row.items()} for row in table]
            return figure, table, tooltip_data



    @app.callback(
        Output("div-plot-click-wordemb", "children"),
        [Input("graph-2d-plot-tsne", "clickData"), Input("dropdown-dataset", "value")],
    )
    def display_click_word_neighbors(clickData, dataset):
        embedding_df, mdl = load_data_for_app(dataset)
        if dataset in WORD_EMBEDDINGS and clickData:
            selected_word = clickData["points"][0]["customdata"][0]

            try:
                # Get the nearest neighbors indices using cosine distance
                nearest_neighbors = [c for c in mdl.wv.most_similar(selected_word, topn=20)]
                trace = go.Bar(
                    x=[c[1] for c in nearest_neighbors],
                    y=[" ".join(c[0].split("_")[-2:]) for c in nearest_neighbors],
                    width=0.8,
                    orientation="h",
                    marker=dict(color="rgb(232, 192, 237)"),
                    text = [embedding_df[embedding_df["word"] == w]["Product"].values[0] for w, _ in nearest_neighbors],
                    hovertemplate="Score: %{x:.2f}<br>Word: %{text}",
                    hoverlabel = dict(namelength = -1),
                )

                layout = go.Layout(
                    title=f'20 nearest neighbors of<br>{" ".join(selected_word.split("_")[-2:])}',
                    xaxis=dict(title="Cosine Distance"),
                    margin=go.layout.Margin(l=60, r=60, t=35, b=35, pad=12),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                )

                fig = go.Figure(data=[trace], layout=layout)

                return dcc.Graph(
                    id="graph-bar-nearest-neighbors-word",
                    figure=fig,
                    style={"height": "80vh"},
                    config={"displayModeBar": False},
                )
            except KeyError as error:
                raise PreventUpdate
        return None


    @app.callback(
        Output("div-plot-click-message", "children"),
        [Input("graph-2d-plot-tsne", "clickData"), Input("dropdown-dataset", "value")],
    )
    def display_click_message(clickData, dataset):
        # Displays message shown when a point in the graph is clicked,
        if dataset in WORD_EMBEDDINGS:
            if clickData:
                return None
            else:
                return "Click a word on the plot to see its top 20 neighbors."

    @app.callback(
        Output("output", "children"),
        [Input("dropdown-dataset", "value"),
         Input("input-ko", "value")],
    )
    def update_output(dataset, ko):
        embedding_df, mdl = load_data_for_app(dataset)
        if ko is None or ko == '':
            return ''
        elif ko not in embedding_df["word"].unique():
            return "No KO found"
        else:
            return f"{embedding_df[embedding_df['word']==ko]['label'].values[0]}\n" \
                   f"{embedding_df[embedding_df['word']==ko]['Product'].values[0]}"


server = app.server
app.layout = create_layout(app)
demo_callbacks(app)

# Running server
if __name__ == "__main__":
    app.run_server(debug=True)
