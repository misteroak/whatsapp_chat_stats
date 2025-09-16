"""
Simple indexing system for WhatsApp chat messages
Using basic Python data structures for now
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path

from .chat_parser import ChatMessage


class ChatIndexer:
    """Simple indexer for WhatsApp chat messages using JSON storage"""

    def __init__(self, index_dir: str = "data/index"):
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.index_dir / "messages.json"
        self.messages = []
        self.word_index = {}
        self.sender_index = {}
        self._load_index()

    def _load_index(self):
        """Load existing index from file"""
        try:
            if self.index_file.exists():
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.messages = data.get('messages', [])
                    self.word_index = data.get('word_index', {})
                    self.sender_index = data.get('sender_index', {})
        except Exception as e:
            print(f"Error loading index: {e}")
            self.messages = []
            self.word_index = {}
            self.sender_index = {}

    def _save_index(self):
        """Save index to file"""
        try:
            data = {
                'messages': self.messages,
                'word_index': self.word_index,
                'sender_index': self.sender_index
            }
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"Error saving index: {e}")

    def add_messages(self, messages: List[ChatMessage]) -> int:
        """
        Add messages to the search index
        Returns number of messages successfully indexed
        """
        if not messages:
            return 0

        indexed_count = 0

        for msg in messages:
            try:
                # Create message dict
                msg_dict = {
                    'id': f"{msg.filename}:{msg.line_number}",
                    'content': msg.content,
                    'sender': msg.sender,
                    'timestamp': msg.timestamp.isoformat(),
                    'filename': msg.filename,
                    'line_number': msg.line_number,
                    'is_media': msg.is_media,
                    'media_type': msg.media_type or ""
                }

                # Add to messages list
                self.messages.append(msg_dict)

                # Index words for search
                words = msg.content.lower().split()
                for word in words:
                    # Clean word
                    word = ''.join(c for c in word if c.isalnum())
                    if word and len(word) > 2:  # Skip very short words
                        if word not in self.word_index:
                            self.word_index[word] = []
                        self.word_index[word].append(len(self.messages) - 1)

                # Index by sender
                sender = msg.sender.lower()
                if sender not in self.sender_index:
                    self.sender_index[sender] = []
                self.sender_index[sender].append(len(self.messages) - 1)

                indexed_count += 1

            except Exception as e:
                print(f"Error indexing message: {e}")
                continue

        # Save the updated index
        self._save_index()
        return indexed_count

    def search_messages(self, query_text: str, limit: int = 50) -> List[Dict]:
        """
        Search messages by content
        Returns list of matching messages with metadata
        """
        if not query_text.strip():
            return []

        query_words = [word.lower().strip() for word in query_text.split()]
        query_words = [w for w in query_words if len(w) > 2]

        if not query_words:
            return []

        # Find messages containing any of the query words
        matching_indices = set()
        for word in query_words:
            # Clean word
            word = ''.join(c for c in word if c.isalnum())
            if word in self.word_index:
                matching_indices.update(self.word_index[word])

        # Get matching messages
        results = []
        for idx in sorted(matching_indices):
            if idx < len(self.messages):
                msg = self.messages[idx].copy()
                # Add a simple score based on word matches
                score = sum(1 for word in query_words
                            if word in msg['content'].lower())
                msg['score'] = score
                results.append(msg)

        # Sort by score and limit results
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]

    def search_by_sender(self, sender: str, limit: int = 50) -> List[Dict]:
        """Search messages by sender name"""
        sender_key = sender.lower()

        if sender_key not in self.sender_index:
            return []

        # Get messages by this sender
        results = []
        for idx in self.sender_index[sender_key]:
            if idx < len(self.messages):
                msg = self.messages[idx].copy()
                msg['score'] = 1.0  # All matches are equally relevant
                results.append(msg)

        return results[:limit]

    def advanced_search(self, content: str = "", sender: str = "",
                        date_from: Optional[datetime] = None,
                        date_to: Optional[datetime] = None,
                        limit: int = 50) -> List[Dict]:
        """
        Advanced search with multiple criteria
        """
        results = []

        # Start with all messages if no content filter
        if content.strip():
            results = self.search_messages(
                content, limit=1000)  # Get more for filtering
        else:
            results = [msg.copy() for msg in self.messages]
            for msg in results:
                msg['score'] = 1.0

        # Filter by sender
        if sender.strip():
            sender_lower = sender.lower()
            results = [msg for msg in results
                       if sender_lower in msg['sender'].lower()]

        # Filter by date range
        if date_from or date_to:
            filtered_results = []
            for msg in results:
                try:
                    msg_date = datetime.fromisoformat(msg['timestamp'])
                    if date_from and msg_date < date_from:
                        continue
                    if date_to and msg_date > date_to:
                        continue
                    filtered_results.append(msg)
                except:
                    continue
            results = filtered_results

        # Sort by score and limit
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]

    def get_all_senders(self) -> List[str]:
        """Get list of all unique senders in the index"""
        return sorted(list(self.sender_index.keys()))

    def get_index_stats(self) -> Dict:
        """Get statistics about the current index"""
        if not self.messages:
            return {}

        # Get date range
        dates = []
        for msg in self.messages:
            try:
                dates.append(datetime.fromisoformat(msg['timestamp']))
            except:
                continue

        date_range = None
        if dates:
            date_range = (min(dates), max(dates))

        return {
            'total_messages': len(self.messages),
            'unique_senders': len(self.sender_index),
            'date_range': date_range,
            'index_size_mb': self._get_index_size()
        }

    def _get_index_size(self) -> float:
        """Get approximate index size in MB"""
        try:
            if self.index_file.exists():
                size_bytes = self.index_file.stat().st_size
                return size_bytes / (1024 * 1024)
            return 0.0
        except:
            return 0.0

    def clear_index(self):
        """Clear all documents from the index"""
        try:
            self.messages = []
            self.word_index = {}
            self.sender_index = {}
            self._save_index()
        except Exception as e:
            print(f"Error clearing index: {e}")

    def remove_file_messages(self, filename: str) -> int:
        """
        Remove all messages from a specific file
        Returns number of messages removed
        """
        try:
            # Find messages from this file
            messages_to_remove = []
            for i, msg in enumerate(self.messages):
                if msg['filename'] == filename:
                    messages_to_remove.append(i)

            # Remove messages (in reverse order to maintain indices)
            for i in reversed(messages_to_remove):
                del self.messages[i]

            # Rebuild indices
            self._rebuild_indices()
            self._save_index()

            return len(messages_to_remove)

        except Exception as e:
            print(f"Error removing file messages: {e}")
            return 0

    def _rebuild_indices(self):
        """Rebuild word and sender indices"""
        self.word_index = {}
        self.sender_index = {}

        for i, msg in enumerate(self.messages):
            # Rebuild word index
            words = msg['content'].lower().split()
            for word in words:
                word = ''.join(c for c in word if c.isalnum())
                if word and len(word) > 2:
                    if word not in self.word_index:
                        self.word_index[word] = []
                    self.word_index[word].append(i)

            # Rebuild sender index
            sender = msg['sender'].lower()
            if sender not in self.sender_index:
                self.sender_index[sender] = []
            self.sender_index[sender].append(i)


def create_chat_indexer(index_dir: str = "data/index") -> ChatIndexer:
    """Factory function to create a ChatIndexer instance"""
    return ChatIndexer(index_dir)
