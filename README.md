# whatsapp_chat_stats

WhatsApp chat analytics dashboard built with Python and Dash. Input is a
folder of exported chats; if a chat is split across multiple files, the
parser will merge them.

## Status
- Scaffold only for now; app code to be generated next.
- Local virtual environment `.venv/` exists.

## Environment Setup
- Python: 3.10+ recommended.
- Activate existing env:
  - macOS/Linux: `source .venv/bin/activate`
  - Windows: `.\\.venv\\Scripts\\activate`
- If you need to create it:
  - Standard: `python -m venv .venv`
  - Using uv: `uv venv .venv`
- Install dependencies (after scaffolding adds `requirements.txt`):
  - pip: `pip install -r requirements.txt`
  - uv: `uv pip install -r requirements.txt`
- Deactivate: `deactivate`

## Run The App
- Ensure your `.venv` is active and deps installed:
  - `pip install -r requirements.txt` (or `uv pip install -r requirements.txt`)
- Start the server: `python app.py`
- Open the app URL shown in the terminal (typically `http://127.0.0.1:8050`).
- Upload your WhatsApp export files:
  - Drag-and-drop `.txt` files directly, or
  - Upload a `.zip` containing multiple `.txt` exports.

## Next Steps
- Enhance the parser to support more export formats and edge cases.
- Add more visualizations: emoji frequency, hourly/day-of-week activity, word clouds.

## Contributing
- Keep changes minimal and focused.
- See `AGENTS.md` for collaboration, approvals, and coding conventions.

## License
- Add a license of your choice when ready.
