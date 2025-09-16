"""
WhatsApp chat message parsing utilities
"""
import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ChatMessage:
    """Represents a single WhatsApp message"""
    timestamp: datetime
    sender: str
    content: str
    filename: str
    line_number: int
    is_media: bool = False
    media_type: Optional[str] = None


class WhatsAppParser:
    """Parser for WhatsApp chat export files"""

    def __init__(self):
        # Common WhatsApp timestamp and message patterns
        self.patterns = [
            # Format: [DD/MM/YY, HH:MM:SS AM/PM] Name: Message
            {
                'regex': r'^\[(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}:\d{2}\s[AP]M)\]\s(.+?):\s(.*)$',
                'date_format': '%d/%m/%y',
                'time_format': '%I:%M:%S %p'
            },
            # Format: [DD/MM/YY, HH:MM:SS] Name: Message
            {
                'regex': r'^\[(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}:\d{2})\]\s(.+?):\s(.*)$',
                'date_format': '%d/%m/%y',
                'time_format': '%H:%M:%S'
            },
            # Format: DD/MM/YYYY, HH:MM - Name: Message
            {
                'regex': r'^(\d{1,2}/\d{1,2}/\d{4}),\s(\d{1,2}:\d{2})\s-\s(.+?):\s(.*)$',
                'date_format': '%d/%m/%Y',
                'time_format': '%H:%M'
            },
            # Format: MM/DD/YY, HH:MM AM/PM - Name: Message
            {
                'regex': r'^(\d{1,2}/\d{1,2}/\d{2}),\s(\d{1,2}:\d{2}\s[AP]M)\s-\s(.+?):\s(.*)$',
                'date_format': '%m/%d/%y',
                'time_format': '%I:%M %p'
            },
            # Format: YYYY-MM-DD HH:MM:SS - Name: Message
            {
                'regex': r'^(\d{4}-\d{2}-\d{2})\s(\d{2}:\d{2}:\d{2})\s-\s(.+?):\s(.*)$',
                'date_format': '%Y-%m-%d',
                'time_format': '%H:%M:%S'
            }
        ]

        # Media message indicators
        self.media_patterns = {
            'image': r'<Media omitted>|image omitted|IMG-\d+|\.jpg|\.jpeg|\.png|\.gif',
            'video': r'video omitted|VID-\d+|\.mp4|\.mov|\.avi',
            'audio': r'audio omitted|AUD-\d+|\.mp3|\.wav|\.m4a|voice message',
            'document': r'document omitted|\.pdf|\.doc|\.docx|\.txt',
            'sticker': r'sticker omitted|STK-\d+',
            'location': r'location:|Live location shared|Location:'
        }

    def parse_line(self, line: str, line_number: int, filename: str) -> Optional[ChatMessage]:
        """Parse a single line from WhatsApp chat export"""
        line = line.strip()
        if not line:
            return None

        # Try each pattern
        for pattern in self.patterns:
            match = re.match(pattern['regex'], line)
            if match:
                try:
                    date_str = match.group(1)
                    time_str = match.group(2)
                    sender = match.group(3).strip()
                    content = match.group(4).strip()

                    # Parse timestamp
                    timestamp = self._parse_timestamp(
                        date_str, time_str,
                        pattern['date_format'],
                        pattern['time_format']
                    )

                    if timestamp is None:
                        continue

                    # Check if it's a media message
                    is_media, media_type = self._detect_media(content)

                    return ChatMessage(
                        timestamp=timestamp,
                        sender=sender,
                        content=content,
                        filename=filename,
                        line_number=line_number,
                        is_media=is_media,
                        media_type=media_type
                    )

                except (ValueError, IndexError):
                    continue

        return None

    def _parse_timestamp(self, date_str: str, time_str: str,
                         date_format: str, time_format: str) -> Optional[datetime]:
        """Parse timestamp from date and time strings"""
        try:
            # Handle 2-digit years
            if date_format == '%d/%m/%y' or date_format == '%m/%d/%y':
                # Convert 2-digit year to 4-digit
                parts = date_str.split('/')
                if len(parts) == 3 and len(parts[2]) == 2:
                    year = int(parts[2])
                    # Assume years 00-30 are 2000-2030, 31-99 are 1931-1999
                    if year <= 30:
                        parts[2] = str(2000 + year)
                    else:
                        parts[2] = str(1900 + year)
                    date_str = '/'.join(parts)
                    date_format = date_format.replace('%y', '%Y')

            datetime_str = f"{date_str} {time_str}"
            datetime_format = f"{date_format} {time_format}"

            return datetime.strptime(datetime_str, datetime_format)
        except ValueError:
            return None

    def _detect_media(self, content: str) -> Tuple[bool, Optional[str]]:
        """Detect if message contains media and determine type"""
        content_lower = content.lower()

        for media_type, pattern in self.media_patterns.items():
            if re.search(pattern, content_lower):
                return True, media_type

        return False, None

    def parse_file(self, content: str, filename: str) -> List[ChatMessage]:
        """Parse entire WhatsApp chat file"""
        messages = []
        lines = content.split('\n')
        current_message = None

        for line_num, line in enumerate(lines, 1):
            # Try to parse as new message
            parsed_message = self.parse_line(line, line_num, filename)

            if parsed_message:
                # Save previous message if exists
                if current_message:
                    messages.append(current_message)
                current_message = parsed_message
            else:
                # This might be a continuation of the previous message
                if current_message and line.strip():
                    # Append to current message content
                    current_message.content += '\n' + line.strip()

        # Don't forget the last message
        if current_message:
            messages.append(current_message)

        return messages

    def get_chat_statistics(self, messages: List[ChatMessage]) -> Dict:
        """Generate basic statistics from parsed messages"""
        if not messages:
            return {}

        senders = set(msg.sender for msg in messages)
        media_count = sum(1 for msg in messages if msg.is_media)

        # Message count by sender
        sender_counts = {}
        for msg in messages:
            sender_counts[msg.sender] = sender_counts.get(msg.sender, 0) + 1

        # Date range
        timestamps = [msg.timestamp for msg in messages]
        date_range = (min(timestamps), max(timestamps))

        return {
            'total_messages': len(messages),
            'unique_senders': len(senders),
            'senders': list(senders),
            'media_messages': media_count,
            'text_messages': len(messages) - media_count,
            'date_range': date_range,
            'sender_message_counts': sender_counts,
            'filename': messages[0].filename if messages else None
        }


def parse_whatsapp_file(content: str, filename: str) -> Tuple[List[ChatMessage], Dict]:
    """
    Convenience function to parse WhatsApp file and return messages with stats
    Returns (messages, statistics)
    """
    parser = WhatsAppParser()
    messages = parser.parse_file(content, filename)
    stats = parser.get_chat_statistics(messages)
    return messages, stats
