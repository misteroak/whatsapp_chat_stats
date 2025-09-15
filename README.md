# whatsapp-chat-stats

Utilities for analyzing WhatsApp chat exports.

Requirements:
- Python 3.13+ (as specified in `pyproject.toml`)
- uv (Python package manager): https://docs.astral.sh/uv/
  - Quick install (macOS/Linux): 
    ```
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

## Setup using uv (virtual environment required)

Do not install dependencies globally. Always use a virtual environment created by uv.

1) Create a virtual environment with uv:
```
uv venv .venv
```

2) Activate it:
```
source .venv/bin/activate
```

3) Verify you are inside the venv (any one of these should work):
- Your shell prompt shows `(.venv)` at the start
- `echo $VIRTUAL_ENV` prints a path
- `which python` points to `.../.venv/bin/python`

If you are not in a venv, go back to step 2. Do not run installs without the venv active.

## Install dependencies (inside the venv only)

With the venv active:
```
uv pip install --upgrade pip
uv pip install -r requirements.txt
```

This project currently requires:
```
dash>=3,<4
```

Note: `uv pip` respects your active virtual environment and will install into `.venv` when it is activated.

## Running

With the venv active:
```
python main.py
```

## Adding or updating dependencies

- Edit `requirements.txt` (e.g., add `somepkg>=1,<2`), then run:
```
uv pip install -r requirements.txt
```
- Keep all required packages listed in `requirements.txt`. Do not install packages globally.

## Troubleshooting

- If your Python version is less than 3.13, recreate the environment with a specific interpreter:
```
rm -rf .venv
uv venv --python 3.13 .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```
- If installs appear to go to a system path, your venv is not active. Re-run:
```
source .venv/bin/activate
```
then install again with `uv pip -r requirements.txt`.
