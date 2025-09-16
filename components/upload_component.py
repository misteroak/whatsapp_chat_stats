"""
Reusable upload UI components for WhatsApp Chat Stats
"""
from dash import dcc
import dash_mantine_components as dmc


def create_upload_section():
    """Create the main file upload section with drag-and-drop support"""
    return dmc.Stack(
        align="center",
        gap="lg",
        children=[
            # Upload area with drag-and-drop
            dcc.Upload(
                id="file-upload",
                children=dmc.Paper(
                    className="upload-dropzone",
                    children=[
                        dmc.Stack(
                            align="center",
                            gap="md",
                            children=[
                                dmc.ThemeIcon(
                                    dmc.Text("📁", size="xl"),
                                    size="xl",
                                    variant="light",
                                    color="blue"
                                ),
                                dmc.Title(
                                    "Drop files here or click to browse",
                                    order=3,
                                    ta="center"
                                ),
                                dmc.Text(
                                    "Supports: .txt files, .zip archives, or folders",
                                    size="sm",
                                    c="dimmed",
                                    ta="center"
                                ),
                                dmc.Group(
                                    gap="xs",
                                    justify="center",
                                    children=[
                                        dmc.Badge(
                                            "Single .txt", variant="light", color="green"),
                                        dmc.Badge(
                                            "Multiple .txt", variant="light", color="blue"),
                                        dmc.Badge(
                                            ".zip archive", variant="light", color="orange"),
                                        dmc.Badge(
                                            "Folder", variant="light", color="purple")
                                    ]
                                )
                            ]
                        )
                    ],
                    p="xl",
                    radius="md",
                    withBorder=True,
                    style={
                        "borderStyle": "dashed",
                        "borderWidth": "2px",
                        "minHeight": "200px",
                        "cursor": "pointer",
                        "transition": "all 0.2s ease"
                    }
                ),
                multiple=True,
                accept=".txt,.zip",
                style={"width": "100%"}
            ),

            # Upload instructions
            dmc.Alert(
                title="Upload Instructions",
                color="blue",
                variant="light",
                children=[
                    dmc.List(
                        children=[
                            dmc.ListItem(
                                "Single .txt file: Upload your WhatsApp chat export"),
                            dmc.ListItem(
                                "Multiple .txt files: Select multiple chat files at once"),
                            dmc.ListItem(
                                ".zip archive: Upload a zip containing multiple chat files"),
                            dmc.ListItem(
                                "Folder: Drag and drop a folder containing .txt files")
                        ]
                    )
                ]
            )
        ]
    )


def create_file_preview_card(file_info: dict):
    """Create a preview card for an uploaded file"""
    return dmc.Card(
        className="file-preview-card",
        children=[
            dmc.Group(
                justify="space-between",
                children=[
                    dmc.Group(
                        gap="sm",
                        children=[
                            dmc.ThemeIcon(
                                dmc.Text("📄" if file_info.get('type')
                                         == 'txt' else "📦", size="lg"),
                                size="lg",
                                variant="light",
                                color="blue"
                            ),
                            dmc.Stack(
                                gap="xs",
                                children=[
                                    dmc.Text(
                                        file_info.get('filename', 'Unknown'),
                                        fw="bold",
                                        size="sm"
                                    ),
                                    dmc.Text(
                                        f"{file_info.get('size_mb', 0):.1f} MB",
                                        size="xs",
                                        c="dimmed"
                                    )
                                ]
                            )
                        ]
                    ),
                    dmc.Badge(
                        f"{file_info.get('messages', 0)} messages",
                        variant="light",
                        color="green"
                    )
                ]
            ),

            # File statistics
            dmc.Space(h="sm"),
            dmc.Group(
                gap="lg",
                children=[
                    dmc.Text(
                        f"👥 {file_info.get('senders', 0)} senders",
                        size="xs",
                        c="dimmed"
                    ),
                    dmc.Text(
                        f"📅 {_format_date_range(file_info.get('date_range'))}",
                        size="xs",
                        c="dimmed"
                    ) if file_info.get('date_range') else None
                ]
            )
        ],
        p="md",
        radius="md",
        withBorder=True
    )


def create_upload_status_indicator(status: str, progress: int = 0):
    """Create upload status indicator with progress"""
    status_colors = {
        'uploading': 'blue',
        'processing': 'orange',
        'success': 'green',
        'error': 'red',
        'idle': 'gray'
    }

    status_icons = {
        'uploading': '⬆️',
        'processing': '⚙️',
        'success': '✅',
        'error': '❌',
        'idle': '📁'
    }

    color = status_colors.get(status, 'gray')
    icon = status_icons.get(status, '📁')

    return dmc.Group(
        gap="sm",
        children=[
            dmc.ThemeIcon(
                dmc.Text(icon, size="sm"),
                size="sm",
                variant="light",
                color=color
            ),
            dmc.Text(
                status.title(),
                size="sm",
                fw="bold",
                c=color
            ),
            dmc.Progress(
                value=progress,
                size="sm",
                color=color,
                style={"flex": 1}
            ) if status in ['uploading', 'processing'] else None
        ]
    )


def create_error_alert(errors: list):
    """Create error alert for upload failures"""
    if not errors:
        return None

    return dmc.Alert(
        title="Upload Errors",
        color="red",
        variant="light",
        children=[
            dmc.List(
                children=[
                    dmc.ListItem(error) for error in errors
                ]
            )
        ]
    )


def create_success_notification(file_count: int, message_count: int):
    """Create success notification for completed uploads"""
    return dmc.Notification(
        title="Upload Complete!",
        message=f"Successfully processed {file_count} files with {message_count} messages",
        action="show",
        autoClose=5000,
        color="green",
        icon=dmc.Text("🎉", size="lg")
    )


def _format_date_range(date_range):
    """Format date range for display"""
    if not date_range or len(date_range) != 2:
        return "Unknown dates"

    start_date, end_date = date_range
    if hasattr(start_date, 'strftime') and hasattr(end_date, 'strftime'):
        return f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"

    return "Unknown dates"
