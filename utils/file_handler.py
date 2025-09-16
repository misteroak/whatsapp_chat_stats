"""
File upload and processing utilities for WhatsApp Chat Stats
"""
import base64
import zipfile
import tempfile
import os
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import shutil

from .validators import validate_uploaded_file
from .chat_parser import parse_whatsapp_file, ChatMessage
from .indexer import create_chat_indexer


class FileProcessor:
    """Handles file upload, extraction, and processing"""

    def __init__(self, upload_dir: str = "data/uploads", index_dir: str = "data/index"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.indexer = create_chat_indexer(index_dir)

    def process_uploaded_files(self, uploaded_files: List[Dict]) -> Dict:
        """
        Process uploaded files from Dash dcc.Upload component
        Returns processing results with statistics and errors
        """
        results = {
            'success': False,
            'files_processed': 0,
            'total_messages': 0,
            'errors': [],
            'file_details': [],
            'processing_steps': []
        }

        if not uploaded_files:
            results['errors'].append("No files uploaded")
            return results

        # Process each uploaded file
        for file_data in uploaded_files:
            try:
                filename = file_data['name']
                content = base64.b64decode(file_data['content'].split(',')[1])

                results['processing_steps'].append(f"Processing {filename}...")

                # Validate file
                is_valid, errors, file_info = validate_uploaded_file(
                    filename, content)

                if not is_valid:
                    results['errors'].extend(
                        [f"{filename}: {error}" for error in errors])
                    continue

                # Process based on file type
                if file_info['extension'] == '.txt':
                    file_result = self._process_txt_file(filename, content)
                elif file_info['extension'] == '.zip':
                    file_result = self._process_zip_file(filename, content)
                else:
                    results['errors'].append(
                        f"{filename}: Unsupported file type")
                    continue

                # Update results
                if file_result['success']:
                    results['files_processed'] += file_result['files_processed']
                    results['total_messages'] += file_result['messages_count']
                    results['file_details'].extend(file_result['file_details'])
                    results['processing_steps'].extend(
                        file_result['processing_steps'])
                else:
                    results['errors'].extend(file_result['errors'])

            except Exception as e:
                results['errors'].append(
                    f"Error processing {filename}: {str(e)}")

        results['success'] = results['files_processed'] > 0
        return results

    def _process_txt_file(self, filename: str, content: bytes) -> Dict:
        """Process a single .txt file"""
        result = {
            'success': False,
            'files_processed': 0,
            'messages_count': 0,
            'file_details': [],
            'processing_steps': [],
            'errors': []
        }

        try:
            # Decode content
            text_content = content.decode('utf-8')

            # Parse WhatsApp messages
            result['processing_steps'].append(
                f"Parsing messages from {filename}...")
            messages, stats = parse_whatsapp_file(text_content, filename)

            if not messages:
                result['errors'].append(
                    f"No valid messages found in {filename}")
                return result

            # Add to search index
            result['processing_steps'].append(
                f"Indexing {len(messages)} messages...")
            indexed_count = self.indexer.add_messages(messages)

            if indexed_count != len(messages):
                result['errors'].append(
                    f"Only {indexed_count}/{len(messages)} messages indexed")

            # Save file info
            file_detail = {
                'filename': filename,
                'type': 'txt',
                'messages': len(messages),
                'senders': stats.get('unique_senders', 0),
                'date_range': stats.get('date_range'),
                'size_mb': len(content) / (1024 * 1024)
            }

            result['success'] = True
            result['files_processed'] = 1
            result['messages_count'] = len(messages)
            result['file_details'].append(file_detail)
            result['processing_steps'].append(
                f"Successfully processed {filename}")

        except UnicodeDecodeError:
            result['errors'].append(
                f"Cannot decode {filename} - invalid encoding")
        except Exception as e:
            result['errors'].append(f"Error processing {filename}: {str(e)}")

        return result

    def _process_zip_file(self, filename: str, content: bytes) -> Dict:
        """Process a ZIP file containing .txt files"""
        result = {
            'success': False,
            'files_processed': 0,
            'messages_count': 0,
            'file_details': [],
            'processing_steps': [],
            'errors': []
        }

        # Create temporary directory for extraction
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Save ZIP file temporarily
                zip_path = Path(temp_dir) / filename
                with open(zip_path, 'wb') as f:
                    f.write(content)

                result['processing_steps'].append(f"Extracting {filename}...")

                # Extract ZIP file
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)

                # Find all .txt files in extracted content
                txt_files = list(Path(temp_dir).rglob("*.txt"))

                if not txt_files:
                    result['errors'].append(
                        f"No .txt files found in {filename}")
                    return result

                result['processing_steps'].append(
                    f"Found {len(txt_files)} .txt files in archive")

                # Process each .txt file
                for txt_file in txt_files:
                    try:
                        with open(txt_file, 'rb') as f:
                            txt_content = f.read()

                        # Get relative filename for better identification
                        relative_name = str(txt_file.relative_to(temp_dir))
                        display_name = f"{filename}:{relative_name}"

                        # Process the txt file
                        txt_result = self._process_txt_file(
                            display_name, txt_content)

                        # Merge results
                        if txt_result['success']:
                            result['files_processed'] += txt_result['files_processed']
                            result['messages_count'] += txt_result['messages_count']
                            result['file_details'].extend(
                                txt_result['file_details'])
                            result['processing_steps'].extend(
                                txt_result['processing_steps'])
                        else:
                            result['errors'].extend(txt_result['errors'])

                    except Exception as e:
                        result['errors'].append(
                            f"Error processing {txt_file.name}: {str(e)}")

                result['success'] = result['files_processed'] > 0

            except zipfile.BadZipFile:
                result['errors'].append(f"{filename} is not a valid ZIP file")
            except Exception as e:
                result['errors'].append(
                    f"Error extracting {filename}: {str(e)}")

        return result

    def process_folder_upload(self, folder_files: List[Dict]) -> Dict:
        """
        Process folder upload containing multiple files
        This handles the case where user uploads a folder via drag-and-drop
        """
        # Filter for .txt files only
        txt_files = [
            f for f in folder_files if f['name'].lower().endswith('.txt')]

        if not txt_files:
            return {
                'success': False,
                'files_processed': 0,
                'total_messages': 0,
                'errors': ['No .txt files found in uploaded folder'],
                'file_details': [],
                'processing_steps': []
            }

        # Process as regular file upload
        return self.process_uploaded_files(txt_files)

    def get_processing_progress(self, total_files: int, current_file: int,
                                current_step: str) -> Dict:
        """Generate progress information for UI updates"""
        progress_percent = int((current_file / total_files)
                               * 100) if total_files > 0 else 0

        return {
            'percent': progress_percent,
            'current_file': current_file,
            'total_files': total_files,
            'current_step': current_step,
            'status': f"Processing file {current_file} of {total_files}: {current_step}"
        }

    def clear_uploads(self):
        """Clear uploaded files and reset index"""
        try:
            # Clear upload directory
            if self.upload_dir.exists():
                shutil.rmtree(self.upload_dir)
                self.upload_dir.mkdir(parents=True, exist_ok=True)

            # Clear search index
            self.indexer.clear_index()

            return True
        except Exception as e:
            print(f"Error clearing uploads: {e}")
            return False

    def get_upload_stats(self) -> Dict:
        """Get statistics about uploaded and indexed data"""
        try:
            index_stats = self.indexer.get_index_stats()

            # Add upload directory info
            upload_size = 0
            file_count = 0
            if self.upload_dir.exists():
                for file_path in self.upload_dir.rglob("*"):
                    if file_path.is_file():
                        upload_size += file_path.stat().st_size
                        file_count += 1

            return {
                **index_stats,
                'upload_files': file_count,
                'upload_size_mb': upload_size / (1024 * 1024)
            }
        except Exception as e:
            print(f"Error getting upload stats: {e}")
            return {}


def create_file_processor(upload_dir: str = "data/uploads",
                          index_dir: str = "data/index") -> FileProcessor:
    """Factory function to create a FileProcessor instance"""
    return FileProcessor(upload_dir, index_dir)
