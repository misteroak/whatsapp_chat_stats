from dash import Dash
import dash_mantine_components as dmc

app = Dash(__name__, title="WhatsApp Chat Stats",
           suppress_callback_exceptions=True)
server = app.server

# Simple Mantine-themed landing page
app.layout = dmc.MantineProvider(
    theme={
        "primaryColor": "indigo",
        "fontFamily": "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
    },
    children=dmc.Container(
        children=[
            dmc.Container(
                children=[
                    dmc.Badge(
                        "WhatsApp Chat Stats",
                        variant="gradient",
                        gradient={"from": "teal", "to": "lime"},
                        size="lg",
                        radius="sm",
                    ),
                    dmc.Space(h=12),
                    dmc.Title("Hi! Upload exported chat file",
                              order=1, style={"textAlign": "center"}),
                    dmc.Text(
                        "Start by uploading your exported .txt chat file to analyze.",
                        c="gray",
                        size="lg",
                        style={"textAlign": "center"},
                    ),
                    dmc.Space(h=24),
                    dmc.Center(
                        dmc.Button(
                            "Choose file",
                            id="upload-btn",
                            size="md",
                            radius="xl",
                            variant="gradient",
                            gradient={"from": "indigo", "to": "cyan"},
                        )
                    ),
                ],
                style={
                    "textAlign": "center",
                    "backdropFilter": "blur(6px)",
                    "background": "rgba(255, 255, 255, 0.7)",
                    "borderRadius": 16,
                    "boxShadow": "0 8px 24px rgba(0,0,0,0.08)",
                    "maxWidth": 640,
                    "width": "100%",
                    "padding": "32px 24px",
                },
            )
        ],
        fluid=True,
        style={
            "minHeight": "100vh",
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
            "padding": "24px",
            "background": "radial-gradient(1200px 600px at 100% 0%, #e7f5ff 0%, #f8f9fa 40%, #ffffff 100%)",
        },
    ),
)

if __name__ == "__main__":
    app.run(debug=True)
