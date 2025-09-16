# Coding Standards & Guidelines

## Tech Stack

### Core Technologies
- **Dash 3.0** - Web application framework
- **Python 3.13** - Runtime environment
- **Dash Mantine Components (dmc)** - Primary UI component library
- **CSS Files** - External stylesheets for styling

### Dependencies
- Dash >= 3.0, < 4.0
- dash-mantine-components for UI components
- Additional packages as needed for data processing

## UI/UX Standards

### High-Quality UI Requirements
- Use Mantine components for consistent, professional appearance
- Maintain design system consistency (colors, typography, spacing)
- Implement responsive design for mobile and desktop
- Follow accessibility best practices (ARIA labels, keyboard navigation)
- Use semantic HTML structure

### Interactive Experience
- **Progress Indicators**: Always show progress bars for operations > 2 seconds
- **Loading States**: Use Mantine Loading components during async operations
- **User Feedback**: Provide clear success/error notifications
- **Responsive Actions**: Immediate visual feedback for user interactions
- **Smooth Transitions**: Use CSS transitions for state changes

### Progress Bar Standards
```python
# Example: Use dmc.Progress for long-running tasks
dmc.Progress(
    value=progress_value,
    label=f"{progress_value}%",
    size="lg",
    radius="xl",
    animate=True
)
```

## Code Organization

### File Structure
```
/
├── app.py                 # Main application entry
├── assets/
│   ├── styles.css        # Main stylesheet
│   ├── components.css    # Component-specific styles
│   └── animations.css    # Transitions and animations
├── components/           # Reusable Dash components
├── utils/               # Helper functions
└── data/               # Data processing modules
```

### CSS Guidelines
- **NO inline styling** - Use CSS classes instead
- **External stylesheets** - Keep all styles in `/assets/` directory
- **BEM methodology** - Use Block-Element-Modifier naming
- **CSS custom properties** - For theme consistency
- **Mobile-first** - Responsive design approach

### Example CSS Structure
```css
/* assets/styles.css */
:root {
  --primary-color: #4c6ef5;
  --secondary-color: #15aabf;
  --background-gradient: radial-gradient(1200px 600px at 100% 0%, #e7f5ff 0%, #f8f9fa 40%, #ffffff 100%);
}

.app-container {
  min-height: 100vh;
  background: var(--background-gradient);
}

.card-container {
  backdrop-filter: blur(6px);
  background: rgba(255, 255, 255, 0.7);
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}
```

## Component Standards

### Mantine Theme Configuration
```python
# Consistent theme across app
MANTINE_THEME = {
    "primaryColor": "indigo",
    "fontFamily": "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
    "components": {
        "Button": {"defaultProps": {"radius": "xl"}},
        "Card": {"defaultProps": {"shadow": "sm", "radius": "md"}},
    }
}
```

### Component Patterns
- **Container Hierarchy**: MantineProvider > Container > Components
- **Spacing**: Use dmc.Space() for consistent vertical spacing
- **Loading States**: Wrap async components with dmc.LoadingOverlay
- **Error Boundaries**: Implement error handling for all data operations

### Progress Feedback Examples
```python
# File upload with progress
dmc.Group([
    dmc.Button("Upload File", id="upload-btn"),
    dmc.Progress(
        id="upload-progress",
        value=0,
        label="Uploading...",
        style={"display": "none"}
    )
])

# Long processing with steps
dmc.Stepper(
    active=current_step,
    children=[
        dmc.StepperStep(label="Parse File"),
        dmc.StepperStep(label="Analyze Data"),
        dmc.StepperStep(label="Generate Stats"),
    ]
)
```

## Code Quality

### Python Standards
- **Type hints** - Use for all function parameters and returns
- **Docstrings** - Document all functions and classes
- **Error handling** - Graceful error messages for users
- **Logging** - Use Python logging for debugging
- **Code formatting** - Follow PEP 8 standards

### Dash-Specific Guidelines
- **Callback organization** - Group related callbacks together
- **State management** - Use dcc.Store for complex state
- **Component IDs** - Use descriptive, kebab-case IDs
- **Prevent initial call** - Use prevent_initial_call=True when appropriate

### Performance Considerations
- **Lazy loading** - Load components only when needed
- **Efficient callbacks** - Minimize callback complexity
- **Caching** - Cache expensive computations
- **Asset optimization** - Compress CSS and minimize HTTP requests

## Interactive Features

### Required User Feedback
1. **File Operations**: Show upload progress and validation status
2. **Data Processing**: Display step-by-step progress with estimated time
3. **Error States**: Clear, actionable error messages with retry options
4. **Success States**: Confirmation messages with next steps
5. **Loading States**: Skeleton screens or spinners for better UX

### Animation Guidelines
- **Subtle transitions** - 200-300ms duration for most interactions
- **Meaningful motion** - Animations should guide user attention
- **Performance** - Use CSS transforms over layout changes
- **Accessibility** - Respect prefers-reduced-motion settings

## Example Implementation

### Good: External CSS with Classes
```python
# app.py
dmc.Container(
    className="main-container",
    children=[
        dmc.Card(
            className="upload-card",
            children=[...]
        )
    ]
)
```

```css
/* assets/styles.css */
.main-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px;
}

.upload-card {
    max-width: 640px;
    width: 100%;
    padding: 32px 24px;
}
```

### Avoid: Inline Styling
```python
# Don't do this
dmc.Container(
    style={
        "minHeight": "100vh",
        "display": "flex",
        "alignItems": "center"
    }
)
```

This coding standard ensures consistent, maintainable, and user-friendly applications that leverage the full power of Dash 3.0 and Mantine components while providing excellent user experience through proper progress feedback and interactive design.
