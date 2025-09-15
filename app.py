from __future__ import annotations

from pathlib import Path
import base64
import io
import zipfile
from datetime import datetime

import pandas as pd
from dash import Dash, Input, Output, State, dcc, html, callback
import dash_mantine_components as dmc
import plotly.express as px
import plotly.graph_objects as go

from whatsapp_chat_stats.parser import parse_whatsapp_exports


app = Dash(__name__)
app.title = "WhatsApp Chat Stats"


def _empty_fig(msg: str = "No data"):
    fig = go.Figure()
    fig.add_annotation(text=msg, xref="paper", yref="paper",
                       x=0.5, y=0.5, showarrow=False)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
    return fig


app.layout = html.Div([
    dcc.Store(id="color-scheme-store", data="light"),
    dmc.MantineProvider(
        id="mantine-provider",
        theme={"colorScheme": "light"},
        children=html.Div(
            className="app-container",
            children=[
                html.Div(
                    className="app-header",
                    children=[
                        dmc.Title("WhatsApp Chat Stats", order=2),
                        html.Button("Toggle Theme", id="toggle-theme", className="theme-toggle"),
                    ],
                ),
                html.Div(
                    className="content-grid",
                    children=[
                        html.Div(
                            className="sidebar",
                            children=[
                                dmc.Text(
                                    "Upload WhatsApp export .txt files or a .zip containing them.",
                                    size="sm",
                                ),
                                html.Div(style={"height": "8px"}),
                                dmc.Text("Inputs", size="sm", className="label-strong"),
                                html.Div(style={"height": "6px"}),
                                dcc.Upload(
                                    id="uploader",
                                    children=dmc.Paper(
                                        withBorder=True,
                                        shadow="xs",
                                        p="md",
                                        radius="sm",
                                        children=dmc.Text(
                                            "Drag and drop or click to select files",
                                        ),
                                    ),
                                    multiple=True,
                                ),
                                html.Div(id="status", className="status-text"),
                            ],
                        ),
                        html.Div(
                            className="main",
                            children=[
                                html.Div(
                                    className="metrics-grid",
                                    children=[
                                        dmc.Paper(
                                            withBorder=True,
                                            p="md",
                                            radius="sm",
                                            children=[
                                                dmc.Text("Messages", size="sm"),
                                                dmc.Title(id="m_count", order=2, children="-"),
                                            ],
                                        ),
                                        dmc.Paper(
                                            withBorder=True,
                                            p="md",
                                            radius="sm",
                                            children=[
                                                dmc.Text("Participants", size="sm"),
                                                dmc.Title(id="m_participants", order=2, children="-"),
                                            ],
                                        ),
                                        dmc.Paper(
                                            withBorder=True,
                                            p="md",
                                            radius="sm",
                                            children=[
                                                dmc.Text("Date Range", size="sm"),
                                                dmc.Title(id="m_range", order=4, children="-"),
                                            ],
                                        ),
                                    ],
                                ),
                                html.Div(style={"height": "16px"}),
                                dmc.Title("Messages by Sender", order=3),
                                dmc.Paper(withBorder=True, p="sm", radius="sm", children=dcc.Graph(id="by_sender", figure=_empty_fig())),
                                html.Div(style={"height": "16px"}),
                                dmc.Title("Messages Over Time", order=3),
                                dmc.Paper(withBorder=True, p="sm", radius="sm", children=dcc.Graph(id="over_time", figure=_empty_fig())),
                                html.Div(style={"height": "16px"}),
                                dmc.Title("Top Words", order=3),
                                dmc.Paper(withBorder=True, p="sm", radius="sm", children=html.Div(id="top_words", className="top-words")),
                                html.Div(style={"height": "16px"}),
                                dmc.Title("System Messages", order=3),
                                dmc.Paper(withBorder=True, p="sm", radius="sm", children=html.Div(id="system_messages", className="system-messages")),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ),
])


def _save_uploads_to_tmp(contents_list, filenames) -> Path | None:
    if not contents_list or not filenames:
        return None
    tmp_root = Path("tmp")
    tmp_root.mkdir(parents=True, exist_ok=True)
    session_dir = tmp_root / datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    session_dir.mkdir(parents=True, exist_ok=True)

    for content, name in zip(contents_list, filenames):
        if not content:
            continue
        header, _, b64data = content.partition(",")
        if not b64data:
            continue
        data = base64.b64decode(b64data)
        lower = (name or "").lower()
        if lower.endswith(".zip"):
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                for zi in zf.infolist():
                    # Extract only .txt files
                    if zi.is_dir():
                        continue
                    if not zi.filename.lower().endswith(".txt"):
                        continue
                    target = session_dir / Path(zi.filename).name
                    with zf.open(zi) as zf_file, target.open("wb") as out:
                        out.write(zf_file.read())
        elif lower.endswith(".txt"):
            target = session_dir / Path(name).name
            with target.open("wb") as out:
                out.write(data)
        # Ignore other file types

    return session_dir


@callback(
    Output("status", "children"),
    Output("m_count", "children"),
    Output("m_participants", "children"),
    Output("m_range", "children"),
    Output("by_sender", "figure"),
    Output("over_time", "figure"),
    Output("top_words", "children"),
    Output("system_messages", "children"),
    Input("uploader", "contents"),
    State("uploader", "filename"),
    State("color-scheme-store", "data"),
    prevent_initial_call=False,
)
def handle_upload(contents, filenames, color_scheme):
    if not contents:
        return (
            "Upload .txt files or a .zip to begin",
            "-",
            "-",
            "-",
            _empty_fig("No data"),
            _empty_fig("No data"),
            "No data",
            "No data",
        )

    try:
        # Dash provides either a single str or a list depending on multiple=True
        if isinstance(contents, str):
            contents_list = [contents]
            filenames_list = [filenames] if isinstance(
                filenames, str) else filenames
        else:
            contents_list = contents
            filenames_list = filenames if isinstance(
                filenames, list) else [filenames]

        folder = _save_uploads_to_tmp(contents_list, filenames_list)
        if folder is None:
            return (
                "No valid files uploaded",
                "-",
                "-",
                "-",
                _empty_fig("No data"),
                _empty_fig("No data"),
                "No data",
                "No data",
            )

        df = parse_whatsapp_exports(folder)
        if df.empty:
            return (
                f"Loaded 0 messages from uploaded files",
                "0",
                "0",
                "-",
                _empty_fig("No messages"),
                _empty_fig("No messages"),
                "No data",
                "No system messages",
            )

        # Metrics
        msg_count = f"{len(df):,}"
        participants = f"{df['sender'].nunique():,}"
        date_range = f"{df['timestamp'].min().date()} → {df['timestamp'].max().date()}"

        # Messages by sender
        by_sender = df.groupby("sender").size().reset_index(
            name="messages").sort_values("messages", ascending=False)
        fig_sender = px.bar(by_sender, x="sender", y="messages")
        fig_sender.update_layout(
            template="plotly_dark" if (
                color_scheme or "light") == "dark" else "plotly_white",
            margin=dict(l=20, r=20, t=20, b=40),
            xaxis_title="Sender",
            yaxis_title="Messages",
        )

        # Messages over time (daily)
        dfd = df.set_index("timestamp").sort_index()
        daily = dfd.resample("1D").size().reset_index(name="messages")
        fig_time = px.area(daily, x="timestamp", y="messages")
        fig_time.update_layout(
            template="plotly_dark" if (
                color_scheme or "light") == "dark" else "plotly_white",
            margin=dict(l=20, r=20, t=20, b=40),
            xaxis_title="Date",
            yaxis_title="Messages",
        )

        # Top words (top 500)
        import re
        from collections import Counter

        text_series = df[df["sender"] != "SYSTEM"]["message"].fillna("")
        # Remove URLs to avoid counting them as words
        url_re = re.compile(r"https?://\S+", re.IGNORECASE)
        word_re = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9']+")

        counts: Counter[str] = Counter()
        for msg in text_series:
            cleaned = url_re.sub(" ", str(msg))
            words = [w.lower() for w in word_re.findall(cleaned)]
            counts.update(words)

        top_items = counts.most_common(500)
        if top_items:
            header = html.Thead(
                html.Tr([html.Th("#"), html.Th("Word"), html.Th("Count")]))
            rows = [
                html.Tr([html.Td(i + 1), html.Td(word), html.Td(cnt)])
                for i, (word, cnt) in enumerate(top_items)
            ]
            top_words_children = html.Table(
                [header, html.Tbody(rows)], className="word-table")
        else:
            top_words_children = "No data"

        # System messages list
        sys_df = df[df["sender"] == "SYSTEM"].copy()
        if sys_df.empty:
            sys_children = "No system messages"
        else:
            sys_items = [
                html.Li(
                    f"{ts.strftime('%Y-%m-%d %H:%M')}: {msg}",
                )
                for ts, msg in zip(sys_df["timestamp"], sys_df["message"])
            ]
            sys_children = html.Ul(sys_items)

        status = f"Loaded {len(df):,} messages from uploads across {df['source_file'].nunique()} file(s)."
        return status, msg_count, participants, date_range, fig_sender, fig_time, top_words_children, sys_children

    except Exception as e:  # pragma: no cover - defensive
        return (
            f"Error: {e}",
            "-",
            "-",
            "-",
            _empty_fig("Error"),
            _empty_fig("Error"),
            "Error",
            "Error",
        )


if __name__ == "__main__":
    app.run(debug=True)

# Theme toggle + provider sync


@callback(
    Output("color-scheme-store", "data"),
    Input("toggle-theme", "n_clicks"),
    State("color-scheme-store", "data"),
    prevent_initial_call=True,
)
def _toggle_theme(n, current):
    if not n:
        return current or "light"
    return "dark" if (current or "light") == "light" else "light"


@callback(
    Output("mantine-provider", "theme"),
    Input("color-scheme-store", "data"),
)
def _sync_providers(scheme):
    scheme = scheme or "light"
    return {"colorScheme": scheme}
