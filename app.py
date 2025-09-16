from dash import Dash, html, dcc, callback, Input, Output, State, ctx
import dash_mantine_components as dmc
import json

# Import our custom components and utilities
from components.upload_component import (
    create_upload_section,
    create_file_preview_card,
    create_error_alert,
    create_success_notification
)
from components.progress_component import (
    create_overall_progress,
    create_upload_summary,
    create_loading_overlay
)
from utils.file_handler import create_file_processor

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

# Initialize file processor
file_processor = create_file_processor()

# Main application layout
app.layout = dmc.MantineProvider(
    theme=MANTINE_THEME,
    children=[
        # Store for application state
        dcc.Store(id="app-state", data={}),
        dcc.Store(id="upload-results", data={}),

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
                            "Upload WhatsApp Chat Files",
                            order=1,
                            ta="center"
                        ),

                        # Description text
                        dmc.Text(
                            "Upload your exported WhatsApp chat files for analysis. Supports single files, multiple files, ZIP archives, and folders.",
                            c="gray",
                            size="lg",
                            ta="center"
                        ),

                        # Spacing
                        dmc.Space(h="xl"),

                        # Upload section
                        html.Div(id="upload-section", children=[
                            create_upload_section()
                        ]),

                        # Progress section
                        dmc.Collapse(
                            id="progress-collapse",
                            opened=False,
                            children=[
                                dmc.Space(h="lg"),
                                html.Div(id="progress-content")
                            ]
                        ),

                        # Results section
                        dmc.Collapse(
                            id="results-collapse",
                            opened=False,
                            children=[
                                dmc.Space(h="xl"),
                                dmc.Divider(
                                    label="Upload Results",
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


# Callback for handling real file uploads
@callback(
    [Output("progress-collapse", "opened"),
     Output("progress-content", "children"),
     Output("results-collapse", "opened"),
     Output("results-content", "children"),
     Output("notifications-container", "children"),
     Output("upload-results", "data")],
    [Input("file-upload", "contents")],
    [State("file-upload", "filename"),
     State("file-upload", "last_modified")],
    prevent_initial_call=True
)
def handle_file_upload(contents, filenames, last_modified):
    """Handle real file upload and processing"""
    if not contents:
        return False, None, False, None, None, {}

    # Ensure we have lists
    if not isinstance(contents, list):
        contents = [contents]
        filenames = [filenames]
        last_modified = [last_modified]

    # Prepare file data for processing
    uploaded_files = []
    for content, filename, timestamp in zip(contents, filenames, last_modified):
        uploaded_files.append({
            'content': content,
            'name': filename,
            'last_modified': timestamp
        })

    # Show initial progress
    progress_content = create_overall_progress(
        total_files=len(uploaded_files),
        processed_files=0,
        current_operation="Starting upload processing..."
    )

    try:
        # Process the uploaded files
        results = file_processor.process_uploaded_files(uploaded_files)

        # Create results summary
        results_content = create_upload_summary(results)

        # Create success/error notification
        if results['success']:
            notification = create_success_notification(
                results['files_processed'],
                results['total_messages']
            )
        else:
            notification = dmc.Notification(
                title="Upload Failed",
                message=f"Encountered {len(results['errors'])} errors during processing",
                action="show",
                autoClose=7000,
                color="red",
                icon=dmc.Text("❌", size="lg")
            )

        # Final progress showing completion
        final_progress = create_overall_progress(
            total_files=len(uploaded_files),
            processed_files=results['files_processed'],
            current_operation="Upload complete!" if results['success'] else "Upload failed"
        )

        return True, final_progress, True, results_content, notification, results

    except Exception as e:
        # Handle unexpected errors
        error_notification = dmc.Notification(
            title="Processing Error",
            message=f"An unexpected error occurred: {str(e)}",
            action="show",
            autoClose=10000,
            color="red",
            icon=dmc.Text("💥", size="lg")
        )

        error_results = {
            'success': False,
            'files_processed': 0,
            'total_messages': 0,
            'errors': [f"System error: {str(e)}"],
            'file_details': []
        }

        error_content = create_upload_summary(error_results)

        return True, None, True, error_content, error_notification, error_results


# Callback for updating progress during file processing
@callback(
    Output("progress-content", "children", allow_duplicate=True),
    [Input("upload-results", "data")],
    prevent_initial_call=True
)
def update_progress_display(results_data):
    """Update progress display based on processing results"""
    if not results_data:
        return None

    # Show detailed progress if we have processing steps
    if 'processing_steps' in results_data and results_data['processing_steps']:
        steps_content = []
        for step in results_data['processing_steps']:
            steps_content.append(
                dmc.Text(
                    f"✓ {step}",
                    size="sm",
                    c="green"
                )
            )

        return dmc.Stack(
            gap="xs",
            children=steps_content
        )

    return None


if __name__ == "__main__":
    app.run(debug=True)
