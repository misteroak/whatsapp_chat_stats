from dash import Dash, html, dcc, callback, Input, Output, State
import dash_mantine_components as dmc

# Initialize Dash app with proper configuration
app = Dash(
    __name__,
    title="WhatsApp Chat Stats",
    suppress_callback_exceptions=True,
    external_stylesheets=[
        # Load only our essential custom CSS
        "/assets/styles.css"
    ]
)
server = app.server

# Mantine theme configuration following coding standards
MANTINE_THEME = {
    "primaryColor": "indigo",
    "fontFamily": "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
}

# Main application layout
app.layout = dmc.MantineProvider(
    theme=MANTINE_THEME,
    children=[
        # Store for application state
        dcc.Store(id="app-state", data={}),

        # Notifications container
        html.Div(id="notifications-container"),

        # Main container with external CSS class
        dmc.Container(
            className="app-container",
            fluid=True,
            children=[
                # Main content card using Mantine Card
                dmc.Card(
                    className="main-card",
                    children=[
                        # App badge
                        dmc.Center(
                            dmc.Badge(
                                "WhatsApp Chat Stats",
                                variant="gradient",
                                gradient={"from": "teal", "to": "lime"},
                                size="lg",
                                radius="sm"
                            )
                        ),

                        # Spacing using Mantine Space
                        dmc.Space(h="md"),

                        # Main title
                        dmc.Title(
                            "Hi! Upload exported chat file",
                            order=1,
                            ta="center"
                        ),

                        # Description text
                        dmc.Text(
                            "Start by uploading your exported .txt chat file to analyze.",
                            c="gray",
                            size="lg",
                            ta="center"
                        ),

                        # Spacing
                        dmc.Space(h="xl"),

                        # Upload section with Mantine components
                        dmc.Stack(
                            align="center",
                            gap="md",
                            children=[
                                # Upload button
                                dmc.Button(
                                    "Choose file",
                                    id="upload-btn",
                                    size="md",
                                    variant="gradient",
                                    gradient={"from": "indigo", "to": "cyan"},
                                    leftSection=dmc.Text("📁", size="lg")
                                ),

                                # Progress section using Mantine Progress
                                dmc.Collapse(
                                    id="progress-collapse",
                                    opened=False,
                                    children=[
                                        dmc.Stack(
                                            gap="sm",
                                            children=[
                                                dmc.Text(
                                                    "Processing file...",
                                                    id="progress-label",
                                                    fw="bold",
                                                    ta="center"
                                                ),
                                                dmc.Progress(
                                                    id="upload-progress",
                                                    value=0,
                                                    animated=True,
                                                    striped=True
                                                ),
                                                dmc.Text(
                                                    "Starting...",
                                                    id="progress-status",
                                                    size="sm",
                                                    c="gray",
                                                    ta="center"
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ]
                        ),

                        # Results section using Mantine Collapse
                        dmc.Collapse(
                            id="results-collapse",
                            opened=False,
                            children=[
                                dmc.Space(h="xl"),
                                dmc.Divider(
                                    label="Analysis Results",
                                    labelPosition="center",
                                    size="sm"
                                ),
                                dmc.Space(h="lg"),
                                html.Div(id="results-content")
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)


# Callback for handling file upload with Mantine notifications
@callback(
    [Output("progress-collapse", "opened"),
     Output("upload-progress", "value"),
     Output("progress-status", "children"),
     Output("notifications-container", "children")],
    [Input("upload-btn", "n_clicks")],
    prevent_initial_call=True
)
def handle_upload_start(n_clicks):
    """Handle upload start with Mantine progress indicators"""
    if n_clicks:
        # Show progress and start processing
        notification = dmc.Notification(
            title="Upload Started",
            message="Processing your WhatsApp chat file...",
            action="show",
            autoClose=3000,
            icon=dmc.Text("📤", size="lg")
        )
        return True, 25, "Parsing file structure...", notification
    return False, 0, "Starting...", None


# Callback for simulating processing steps with Mantine components
@callback(
    [Output("upload-progress", "value", allow_duplicate=True),
     Output("progress-status", "children", allow_duplicate=True),
     Output("progress-label", "children"),
     Output("results-collapse", "opened"),
     Output("notifications-container", "children", allow_duplicate=True)],
    [Input("upload-progress", "value")],
    prevent_initial_call=True
)
def update_progress_steps(current_value):
    """Update progress with Mantine feedback components"""
    if current_value == 25:
        return 50, "Analyzing message patterns...", "Processing file...", False, None
    elif current_value == 50:
        return 75, "Generating statistics...", "Processing file...", False, None
    elif current_value == 75:
        # Complete processing
        success_notification = dmc.Notification(
            title="Analysis Complete!",
            message="Your WhatsApp chat has been successfully analyzed.",
            action="show",
            autoClose=5000,
            color="green",
            icon=dmc.Text("✅", size="lg")
        )
        return 100, "Complete!", "Analysis finished", True, success_notification

    return current_value, "Processing...", "Processing file...", False, None


if __name__ == "__main__":
    app.run(debug=True)
