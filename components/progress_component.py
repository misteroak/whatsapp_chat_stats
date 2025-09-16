"""
Progress indicator components for WhatsApp Chat Stats
"""
import dash_mantine_components as dmc


def create_processing_stepper(current_step: int = 0, steps: list = None):
    """Create a multi-step progress indicator"""
    if steps is None:
        steps = [
            "Upload Files",
            "Validate Content",
            "Parse Messages",
            "Build Index",
            "Complete"
        ]

    stepper_steps = []
    for i, step in enumerate(steps):
        stepper_steps.append(
            dmc.StepperStep(
                label=step,
                description=f"Step {i + 1}",
                loading=i == current_step,
                color="blue"
            )
        )

    return dmc.Stepper(
        active=current_step,
        color="blue",
        size="sm",
        children=stepper_steps
    )


def create_file_progress_card(filename: str, status: str, progress: int = 0,
                              message: str = ""):
    """Create progress card for individual file processing"""
    status_colors = {
        'waiting': 'gray',
        'processing': 'blue',
        'parsing': 'orange',
        'indexing': 'yellow',
        'complete': 'green',
        'error': 'red'
    }

    status_icons = {
        'waiting': '⏳',
        'processing': '⚙️',
        'parsing': '📖',
        'indexing': '🔍',
        'complete': '✅',
        'error': '❌'
    }

    color = status_colors.get(status, 'gray')
    icon = status_icons.get(status, '⏳')

    return dmc.Card(
        children=[
            dmc.Group(
                justify="space-between",
                children=[
                    dmc.Group(
                        gap="sm",
                        children=[
                            dmc.ThemeIcon(
                                dmc.Text(icon, size="sm"),
                                size="sm",
                                variant="light",
                                color=color
                            ),
                            dmc.Stack(
                                gap="xs",
                                children=[
                                    dmc.Text(
                                        filename,
                                        fw="bold",
                                        size="sm"
                                    ),
                                    dmc.Text(
                                        message or status.title(),
                                        size="xs",
                                        c="gray"
                                    )
                                ]
                            )
                        ]
                    ),
                    dmc.Text(
                        f"{progress}%",
                        size="sm",
                        fw="bold",
                        c=color
                    )
                ]
            ),
            dmc.Space(h="xs"),
            dmc.Progress(
                value=progress,
                color=color,
                size="sm",
                animated=status in ['processing', 'parsing', 'indexing']
            )
        ],
        p="md",
        radius="md",
        withBorder=True,
        className="file-progress-card"
    )


def create_overall_progress(total_files: int, processed_files: int,
                            current_operation: str = "Processing files..."):
    """Create overall progress indicator"""
    progress_percent = int((processed_files / total_files)
                           * 100) if total_files > 0 else 0

    return dmc.Stack(
        gap="sm",
        children=[
            dmc.Group(
                justify="space-between",
                children=[
                    dmc.Text(
                        current_operation,
                        fw="bold",
                        size="md"
                    ),
                    dmc.Text(
                        f"{processed_files}/{total_files} files",
                        size="sm",
                        c="gray"
                    )
                ]
            ),
            dmc.Progress(
                value=progress_percent,
                size="lg",
                color="blue",
                animated=processed_files < total_files,
                striped=True
            ),
            dmc.Text(
                f"{progress_percent}% complete",
                size="sm",
                ta="center",
                c="gray"
            )
        ]
    )


def create_processing_timeline(steps: list):
    """Create a timeline showing processing steps"""
    timeline_items = []

    for i, step in enumerate(steps):
        timeline_items.append(
            dmc.TimelineItem(
                title=step.get('title', f'Step {i + 1}'),
                children=[
                    dmc.Text(
                        step.get('description', ''),
                        size="sm",
                        c="gray"
                    )
                ],
                bullet=dmc.ThemeIcon(
                    dmc.Text(step.get('icon', '•'), size="xs"),
                    size="sm",
                    variant="light",
                    color=step.get('color', 'blue')
                )
            )
        )

    return dmc.Timeline(
        active=len([s for s in steps if s.get('completed', False)]),
        color="blue",
        children=timeline_items
    )


def create_upload_summary(results: dict):
    """Create summary card showing upload results"""
    if not results:
        return None

    success = results.get('success', False)
    files_processed = results.get('files_processed', 0)
    total_messages = results.get('total_messages', 0)
    errors = results.get('errors', [])

    summary_color = 'green' if success else 'red'
    summary_icon = '🎉' if success else '⚠️'

    return dmc.Card(
        children=[
            dmc.Group(
                gap="sm",
                children=[
                    dmc.ThemeIcon(
                        dmc.Text(summary_icon, size="lg"),
                        size="lg",
                        variant="light",
                        color=summary_color
                    ),
                    dmc.Stack(
                        gap="xs",
                        children=[
                            dmc.Text(
                                "Upload Complete!" if success else "Upload Failed",
                                fw="bold",
                                size="lg",
                                c=summary_color
                            ),
                            dmc.Group(
                                gap="lg",
                                children=[
                                    dmc.Text(
                                        f"📁 {files_processed} files",
                                        size="sm"
                                    ),
                                    dmc.Text(
                                        f"💬 {total_messages} messages",
                                        size="sm"
                                    )
                                ]
                            )
                        ]
                    )
                ]
            ),

            # Show errors if any
            dmc.Space(h="sm") if errors else None,
            dmc.Alert(
                title="Errors encountered:",
                color="red",
                variant="light",
                children=[
                    dmc.List(
                        children=[
                            # Show max 5 errors
                            dmc.ListItem(error) for error in errors[:5]
                        ]
                    ),
                    dmc.Text(
                        f"... and {len(errors) - 5} more errors",
                        size="xs",
                        c="gray"
                    ) if len(errors) > 5 else None
                ]
            ) if errors else None
        ],
        p="lg",
        radius="md",
        withBorder=True,
        className="upload-summary-card"
    )


def create_loading_overlay(visible: bool = False, message: str = "Processing..."):
    """Create loading overlay for the entire upload section"""
    return dmc.LoadingOverlay(
        visible=visible,
        overlayProps={"radius": "sm", "blur": 2},
        loaderProps={"color": "blue", "type": "bars"},
        children=[
            dmc.Text(
                message,
                ta="center",
                mt="md",
                fw="bold"
            )
        ]
    )
