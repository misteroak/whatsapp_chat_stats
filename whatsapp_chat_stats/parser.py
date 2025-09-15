from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional, Tuple
import re

import pandas as pd


# Very lightweight WhatsApp parser supporting common export formats.
# Merges multiple .txt files from a folder into a single DataFrame.


_PATTERNS = (
    # US month-first with AM/PM
    ("us_ampm", "%m/%d/%y, %I:%M %p"),
    ("us_ampm_long_year", "%m/%d/%Y, %I:%M %p"),
    ("us_ampm_seconds", "%m/%d/%y, %I:%M:%S %p"),
    ("us_ampm_long_year_seconds", "%m/%d/%Y, %I:%M:%S %p"),
    # EU day-first 24h
    ("eu_24h", "%d/%m/%y, %H:%M"),
    ("eu_24h_long_year", "%d/%m/%Y, %H:%M"),
    ("eu_24h_seconds", "%d/%m/%y, %H:%M:%S"),
    ("eu_24h_long_year_seconds", "%d/%m/%Y, %H:%M:%S"),
    # Dot-separated locales (common on iOS/Android in DE/PL etc.)
    ("eu_dot_24h", "%d.%m.%y, %H:%M"),
    ("eu_dot_24h_long_year", "%d.%m.%Y, %H:%M"),
    ("eu_dot_24h_seconds", "%d.%m.%y, %H:%M:%S"),
    ("eu_dot_24h_long_year_seconds", "%d.%m.%Y, %H:%M:%S"),
    ("eu_dot_ampm", "%d.%m.%y, %I:%M %p"),
    ("eu_dot_ampm_long_year", "%d.%m.%Y, %I:%M %p"),
)


def _split_header_and_body(line: str) -> Optional[Tuple[str, str]]:
    """Split a line into the leading date/time part and the rest.

    Supports both hyphen style:
      "12/31/20, 10:23 PM - John: Hello"
    and bracket style (older exports on iOS/Android):
      "[12/31/20, 10:23:01 PM] John: Hello"
    """
    # Hyphen style
    if " - " in line:
        head, sep, rest = line.partition(" - ")
        if sep:
            return head, rest

    # Bracket style
    if line.startswith("["):
        close = line.find("]")
        if close > 1:
            head = line[1:close]
            # common pattern is "] " then body
            rest = line[close + 1:]
            if rest.startswith(" "):
                rest = rest[1:]
            return head, rest

    return None


def _parse_timestamp(head: str) -> Optional[datetime]:
    # head should look like "12/31/20, 10:23 PM" or "31/12/20, 22:23" or dot-separated
    head = _normalize_ts_head(head)
    for _, fmt in _PATTERNS:
        try:
            return datetime.strptime(head, fmt)
        except ValueError:
            continue
    return None


def _normalize_ts_head(s: str) -> str:
    """Normalize timestamp head for iOS/locale quirks.

    - Replace narrow/regular no-break spaces with regular spaces
    - Drop zero-width and directionality marks
    - Collapse repeated spaces
    """
    s = s.replace("\u202f", " ")  # narrow no-break space
    s = s.replace("\u00a0", " ")  # no-break space
    # Remove zero-width/directionality marks
    s = s.replace("\u200e", "").replace("\u200f", "").replace("\u2060", "")
    s = s.replace("\u200b", "").replace("\u200c", "").replace("\u200d", "")
    # Normalize spacing
    s = re.sub(r"\s+", " ", s.strip())
    return s


def _split_sender_and_text(body: str) -> Tuple[str, str]:
    # Expected: "Sender: Message". System messages often lack a colon.
    if ": " in body:
        sender, _, text = body.partition(": ")
        return sender.strip(), _clean_text(text.rstrip("\n"))
    return "SYSTEM", _clean_text(body.rstrip("\n"))


def _clean_text(s: str) -> str:
    """Remove invisible control chars commonly found in exports."""
    return (
        s.replace("\u200e", "")
        .replace("\u200f", "")
        .replace("\u2060", "")
        .replace("\u200b", "")
        .replace("\u200c", "")
        .replace("\u200d", "")
    )


@dataclass
class Message:
    timestamp: datetime
    sender: str
    text: str
    source_file: str


def parse_whatsapp_exports(input_dir: Path | str) -> pd.DataFrame:
    """Parse all WhatsApp export .txt files in a folder into a DataFrame.

    Columns: timestamp (datetime), sender (str), message (str), source_file (str)
    """
    folder = Path(input_dir)
    if not folder.exists() or not folder.is_dir():
        return pd.DataFrame(columns=["timestamp", "sender", "message", "source_file"]).astype(
            {"timestamp": "datetime64[ns]"}
        )

    messages: List[Message] = []
    for path in sorted(folder.glob("*.txt")):
        messages.extend(_parse_single_export(path))

    if not messages:
        return pd.DataFrame(columns=["timestamp", "sender", "message", "source_file"]).astype(
            {"timestamp": "datetime64[ns]"}
        )

    df = pd.DataFrame(
        {
            "timestamp": [m.timestamp for m in messages],
            "sender": [m.sender for m in messages],
            "message": [m.text for m in messages],
            "source_file": [m.source_file for m in messages],
        }
    )
    df.sort_values("timestamp", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def _parse_single_export(path: Path) -> List[Message]:
    out: List[Message] = []
    current: Optional[Message] = None

    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.rstrip("\n")
            head_body = _split_header_and_body(line)
            if head_body is None:
                # continuation of previous message if present
                if current is not None:
                    current.text += "\n" + line
                continue

            head, body = head_body
            ts = _parse_timestamp(head)
            if ts is None:
                # Not a new message line; append
                if current is not None:
                    current.text += "\n" + line
                continue

            sender, text = _split_sender_and_text(body)
            # flush previous
            if current is not None:
                out.append(current)
            current = Message(timestamp=ts, sender=sender,
                              text=text, source_file=path.name)

    if current is not None:
        out.append(current)

    return out
