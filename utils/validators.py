"""
File validation utilities for WhatsApp Chat Stats
"""
import re
from typing import List, Tuple, Optional
from pathlib import Path


def is_valid_file_type(filename: str) -> bool:
    """Check if file has a valid extension (.txt or .zip)"""
    valid_extensions = {'.txt', '.zip'}
    return Path(filename).suffix.lower() in valid_extensions


def is_whatsapp_chat_format(content: str) -> Tuple[bool, Optional[str]]:
    """
    Validate if content follows WhatsApp chat export format
    Returns (is_valid, error_message)
    """
    if not content or not content.strip():
        return False, "File is empty"

    lines = content.strip().split('\n')
    if len(lines) < 1:
        return False, "File has no content"

    # Common WhatsApp timestamp patterns
    whatsapp_patterns = [
        # Format: [DD/MM/YY, HH:MM:SS AM/PM] Name: Message
        r'^\[\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\s[AP]M\]\s.+?:\s',
        # Format: [DD/MM/YY, HH:MM:SS] Name: Message
        r'^\[\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\]\s.+?:\s',
        # Format: DD/MM/YYYY, HH:MM - Name: Message
        r'^\d{1,2}/\d{1,2}/\d{4},\s\d{1,2}:\d{2}\s-\s.+?:\s',
        # Format: MM/DD/YY, HH:MM AM/PM - Name: Message
        r'^\d{1,2}/\d{1,2}/\d{2},\s\d{1,2}:\d{2}\s[AP]M\s-\s.+?:\s',
        # Format: YYYY-MM-DD HH:MM:SS - Name: Message
        r'^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\s-\s.+?:\s'
    ]

    # WhatsApp system message patterns (these are valid but don't follow user message format)
    system_message_patterns = [
        # System messages often start with invisible characters or special formatting
        r'^\s*‎.*',  # Messages starting with invisible characters
        r'^\s*\[.*\]\s.*:\s‎.*',  # System messages with timestamps
        r'.*end-to-end encrypted.*',
        r'.*disappearing messages.*',
        r'.*image omitted.*',
        r'.*video omitted.*',
        r'.*audio omitted.*',
        r'.*document omitted.*',
        r'.*created group.*',
        r'.*changed the subject to.*',  # More specific subject change pattern
        r'.*changed this group\'s icon.*',  # Group icon changes
        r'.*security code changed.*',
        r'.*joined using.*invite link.*',
        # Additional specific WhatsApp system message patterns
        r'.*removed.*from.*group.*',  # "Admin removed John from group"
        r'.*made.*admin.*',  # "John made Mary an admin"
        r'.*no longer.*admin.*',  # "John is no longer an admin"
        r'.*group description.*',  # Group description changes
        r'.*pinned.*message.*',  # Pinned messages
        r'.*unpinned.*message.*',  # Unpinned messages
        r'.*deleted.*message.*',  # Deleted messages
        r'.*call.*duration.*',  # Call duration messages
        r'.*missed.*call.*',  # Missed call notifications
        r'.*you.*blocked.*contact.*',  # Block notifications
        r'.*contact.*blocked.*you.*'  # Block notifications
    ]

    # Check first 20 lines for WhatsApp format (increased from 10)
    valid_lines = 0
    total_checked = min(20, len(lines))

    for line in lines[:total_checked]:
        original_line = line
        line = line.strip()
        if not line:
            continue

        # Check if it's a system message first
        is_system_message = False
        for pattern in system_message_patterns:
            if re.search(pattern, original_line, re.IGNORECASE):
                valid_lines += 1
                is_system_message = True
                break

        if is_system_message:
            continue

        # Check if line matches any WhatsApp user message pattern
        for pattern in whatsapp_patterns:
            if re.match(pattern, line):
                valid_lines += 1
                break

    # At least 20% of checked lines should match WhatsApp format (lowered threshold)
    if total_checked > 0 and valid_lines / total_checked >= 0.2:
        return True, None
    else:
        return False, "File doesn't appear to be a WhatsApp chat export"


def validate_file_size(content: bytes, max_size_mb: int = 50) -> Tuple[bool, Optional[str]]:
    """Validate file size is within acceptable limits"""
    size_mb = len(content) / (1024 * 1024)
    if size_mb > max_size_mb:
        return False, f"File size ({size_mb:.1f}MB) exceeds maximum allowed size ({max_size_mb}MB)"
    return True, None


def get_file_info(filename: str, content: bytes) -> dict:
    """Get basic file information"""
    return {
        'name': filename,
        'size_bytes': len(content),
        'size_mb': len(content) / (1024 * 1024),
        'extension': Path(filename).suffix.lower(),
        'is_valid_type': is_valid_file_type(filename)
    }


def validate_uploaded_file(filename: str, content: bytes) -> Tuple[bool, List[str], dict]:
    """
    Comprehensive file validation
    Returns (is_valid, error_messages, file_info)
    """
    errors = []
    file_info = get_file_info(filename, content)

    # Check file type
    if not file_info['is_valid_type']:
        errors.append(
            f"Invalid file type. Only .txt and .zip files are supported.")

    # Check file size
    size_valid, size_error = validate_file_size(content)
    if not size_valid:
        errors.append(size_error)

    # For .txt files, validate WhatsApp format
    if file_info['extension'] == '.txt' and not errors:
        try:
            text_content = content.decode('utf-8')
            format_valid, format_error = is_whatsapp_chat_format(text_content)
            if not format_valid:
                errors.append(format_error)
        except UnicodeDecodeError:
            errors.append(
                "File encoding not supported. Please ensure the file is UTF-8 encoded.")

    return len(errors) == 0, errors, file_info
