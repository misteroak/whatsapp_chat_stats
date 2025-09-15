# AGENTS.md — WhatsApp Chat Stats Dashboard (Dash + Mantine)

## Overview
Python Dash application to analyze one or more WhatsApp chat exports (iOS) with a high-quality Mantine UI. Users can upload a folder or multiple .txt files (or a .zip), which are parsed, normalized, and indexed for real-time interactive queries and visualizations.

Key visuals:
- Top words and emojis
- Messages over time
- Activity heatmap (hour × weekday)
- Participant-level stats
- Search-driven, real-time updates across charts

All custom styles live in `assets/styles.css` (no inline styles). Mantine UI is used via `dash-mantine-components` for a cohesive, modern look.

## Tech Stack
- Python 3.10+
- Dash 3.x + dash-mantine-components (Mantine UI)
- Plotly (charts)
- Pandas / NumPy (data wrangling)
- emoji (emoji detection)
- NLTK stopwords (text normalization)
- Optional: rapidfuzz (fuzzy search), duckdb (columnar queries), diskcache (long callbacks)
- Env and packaging: uv (pyproject.toml, uv.lock)

## Upload and Indexing Strategy
- Input formats:
  - Multiple .txt files (iOS export) via multi-file upload
  - Optional .zip of exports (we’ll extract server-side)
- Parsing:
  - Robust parser for iOS formats, multiline messages, media markers
  - Normalize timestamps with timezone/localization
  - Columns: `timestamp`, `author`, `message`, `emojis`, `date`, `hour`, `weekday`, `is_media`, `file_id`
- Indexing pipeline (in-memory by default):
  1. Normalize text (Unicode NFKC, lowercase, punctuation cleanup; keep emojis)
  2. Tokenize; remove stopwords (NLTK) and short tokens
  3. Build inverted indexes (dict: token -> numpy array of row indices)
  4. Emoji index (emoji -> indices)
  5. Fast access maps (author -> indices), precomputed time buckets
  6. Optional: TF-IDF weights for scoring, cached per token
- Query engine:
  - Boolean modes: AND (all terms), OR (any term), Phrase (quoted)
  - Optional fuzzy matching (rapidfuzz) with adjustable threshold
  - Filters: date range, participants, has media, keyword(s), emojis
  - Returns masks/rows used to update visuals in near real-time
- Caching & session model:
  - Index lives in server memory (per Dash worker) keyed by session id
  - dcc.Store keeps lightweight parameters; heavy data remain server-side
  - Memoization (lru_cache) on (filters, query) to avoid recomputation
  - Optional duckdb index for very large chats (fallback path)

## Long Operations — UX and Feedback
- On upload/indexing:
  - Show overlay (dmc.Loading) and progress bar with status text
  - Disable controls during parse/index step; re-enable when ready
  - Notifications on success/error (dmc.NotificationsProvider)
- During queries:
  - Debounced inputs (300–500ms); lightweight loader in chart cards
  - For heavy ops, use Dash `long_callback` + Diskcache

## UI/UX Principles
- Mantine theme via `dmc.MantineProvider` (colors/typography)
- Responsive layout with `dmc.AppShell` (Header, Navbar)
- Reusable cards/components; all custom CSS in `assets/styles.css`
- Accessible focus states, readable contrasts, ARIA labels

## Core Features
1. Multi-file/folder upload with clear instructions (and optional .zip support)
2. Parsing + normalization for iOS exports
3. Real-time query bar (AND/OR/Phrase, optional fuzzy)
4. Filters: date range, participants, has-media, emoji selection
5. Charts:
   - Top words, top emojis
   - Messages over time (daily)
   - Activity heatmap (weekday × hour)
   - Participant breakdown
6. KPIs: message count, participants, time span, messages/day

## Data Model (conceptual)
DataFrame columns:
- `timestamp` (datetime), `date`, `hour`, `weekday`
- `author` (str), `message` (str)
- `emojis` (list[str])
- `is_media` (bool), `file_id` (str)

Indexes:
- `token_index`: {token: np.ndarray[int]}
- `emoji_index`: {emoji: np.ndarray[int]}
- `author_index`: {author: np.ndarray[int]}
- Optional `tfidf`: {token: weight}, doc_len arrays

## Architecture and Structure
```
whatsapp_chat_stats/
  app.py
  pyproject.toml
  uv.lock
  assets/
    styles.css
  components/
    __init__.py
    layout.py          # AppShell, header, navbar
    upload.py          # multi-file upload UI + instructions
    filters.py         # query bar, date/author controls
    charts.py          # plotly charts in dmc Cards
    kpis.py            # summary metrics cards
  utils/
    parser.py          # parse iOS text exports
    indexing.py        # MessageIndex: build + query inverted indexes
    text_cleaning.py   # normalization, tokenization, stopwords
    emojis.py          # emoji extraction and counting
    aggregations.py    # groupbys for visuals
    sessions.py        # session handling + global cache
```

## Callback Strategy
- Upload -> server stores raw files -> parse -> build `MessageIndex` -> cache keyed by session
- Filters + query -> compute mask via `MessageIndex` -> return data slices to charts
- `dcc.Loading` around charts; disable controls during indexing; progress bar for upload/parse

## Optional SQLite/DuckDB Path
- For very large datasets:
  - DuckDB for aggregations and filtering
  - SQLite FTS5 (if available) for full-text search
- Default remains in-memory for simplicity and speed on typical chat sizes

## Setup with uv
- Install uv:
  - macOS (Homebrew): `brew install uv`
  - Official: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Initialize:
  - `uv init`
- Add dependencies:
  - Core: `uv add "dash>=3,<4" dash-mantine-components plotly pandas emoji nltk`
  - Optional search/scale: `uv add rapidfuzz duckdb diskcache`
- One-time NLTK data:
  - `uv run python -c "import nltk; nltk.download('stopwords')"`
- Run:
  - `uv run python app.py`

## Testing
- Parser tests across sample iOS exports (different locales)
- Indexing tests (tokenization, phrase queries, emoji extraction)
- Callback smoke tests (filters + charts)
- Performance checks (typing latency, query response ≲ ~100ms on typical chats)

## Non-Goals (initial)
- Cross-conversation analytics across many exports simultaneously
- Persistent DB beyond session cache
- Cloud multi-user deployment

## Next steps
- Initialize uv project and add dependencies
- Scaffold modules (utils/components) and assets/styles.css
- Implement parser + MessageIndex MVP with unit tests
- Wire upload -> index -> query pipeline with loaders and progress
