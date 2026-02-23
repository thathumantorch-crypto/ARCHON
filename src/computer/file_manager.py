import os
import shutil
import json
import time
from typing import List, Dict, Optional, Any, Union
from pathlib import Path
import stat
from datetime import datetime
import mimetypes

class FileManager:
    """
    Advanced file management system with AI-friendly interface
    """
    
    def __init__(self, base_directory: str = None):
        self.base_directory = base_directory or os.getcwd()
        self.supported_formats = {
            'text': ['.txt', '.py', '.js', '.html', '.css', '.json', '.xml', '.md', '.csv'],
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico'],
            'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'],
            'video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
            'document': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.ods', '.odp']
        }
    
    def list_directory(self, path: str = None, include_hidden: bool = False) -> List[Dict[str, Any]]:
        """
        List directory contents with detailed information
        
        Args:
            path: Directory path to list (default: current directory)
            include_hidden: Whether to include hidden files
            
        Returns:
            List of file/directory information dictionaries
        """
        target_path = Path(path) if path else Path(self.base_directory)
        
        if not target_path.exists():
            raise FileNotFoundError(f"Directory not found: {target_path}")
        
        if not target_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {target_path}")
        
        items = []
        
        try:
            for item in target_path.iterdir():
                # Skip hidden files if not requested
                if not include_hidden and item.name.startswith('.'):
                    continue
                
                try:
                    stat_info = item.stat()
                    item_info = {
                        'name': item.name,
                        'path': str(item),
                        'type': 'directory' if item.is_dir() else 'file',
                        'size': stat_info.st_size,
                        'created': datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                        'modified': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                        'accessed': datetime.fromtimestamp(stat_info.st_atime).isoformat(),
                        'permissions': oct(stat_info.st_mode)[-3:],
                        'extension': item.suffix.lower() if item.is_file() else '',
                        'mime_type': mimetypes.guess_type(str(item))[0] if item.is_file() else None
                    }
                    
                    # Add file category
                    if item.is_file():
                        item_info['category'] = self._categorize_file(item.suffix.lower())
                    
                    items.append(item_info)
                    
                except (PermissionError, OSError) as e:
                    # Add entry for inaccessible items
                    items.append({
                        'name': item.name,
                        'path': str(item),
                        'type': 'directory' if item.is_dir() else 'file',
                        'error': f"Access denied: {str(e)}"
                    })
        
        except PermissionError as e:
            raise PermissionError(f"Permission denied accessing directory: {target_path}")
        
        # Sort by name, directories first
        items.sort(key=lambda x: (x['type'] != 'directory', x['name'].lower()))
        
        return items
    
    def _categorize_file(self, extension: str) -> str:
        """Categorize file based on extension"""
        for category, extensions in self.supported_formats.items():
            if extension in extensions:
                return category
        return 'other'
    
    def create_file(self, file_path: str, content: str = "", overwrite: bool = False) -> Dict[str, Any]:
        """
        Create a new file with optional content
        
        Args:
            file_path: Path to the file to create
            content: Initial content for the file
            overwrite: Whether to overwrite existing file
            
        Returns:
            Dictionary with operation result
        """
        path = Path(file_path)
        
        # Check if file exists
        if path.exists() and not overwrite:
            raise FileExistsError(f"File already exists: {file_path}")
        
        try:
            # Create parent directories if they don't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content to file
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                'success': True,
                'message': f"File created: {file_path}",
                'path': str(path),
                'size': len(content.encode('utf-8'))
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f"Error creating file: {str(e)}",
                'path': file_path
            }
    
    def create_directory(self, dir_path: str, exist_ok: bool = False) -> Dict[str, Any]:
        """
        Create a new directory
        
        Args:
            dir_path: Path to the directory to create
            exist_ok: Whether to ignore if directory already exists
            
        Returns:
            Dictionary with operation result
        """
        path = Path(dir_path)
        
        try:
            path.mkdir(parents=True, exist_ok=exist_ok)
            
            return {
                'success': True,
                'message': f"Directory created: {dir_path}",
                'path': str(path)
            }
        
        except FileExistsError:
            return {
                'success': False,
                'message': f"Directory already exists: {dir_path}",
                'path': dir_path
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Error creating directory: {str(e)}",
                'path': dir_path
            }
    
    def delete_file(self, file_path: str, permanent: bool = False) -> Dict[str, Any]:
        """
        Delete a file
        
        Args:
            file_path: Path to the file to delete
            permanent: Whether to permanently delete (no recycle bin)
            
        Returns:
            Dictionary with operation result
        """
        path = Path(file_path)
        
        if not path.exists():
            return {
                'success': False,
                'message': f"File not found: {file_path}",
                'path': file_path
            }
        
        if not path.is_file():
            return {
                'success': False,
                'message': f"Path is not a file: {file_path}",
                'path': file_path
            }
        
        try:
            # Get file size before deletion
            file_size = path.stat().st_size
            
            # Delete the file
            path.unlink()
            
            return {
                'success': True,
                'message': f"File deleted: {file_path}",
                'path': file_path,
                'size_freed': file_size
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f"Error deleting file: {str(e)}",
                'path': file_path
            }
    
    def delete_directory(self, dir_path: str, recursive: bool = False) -> Dict[str, Any]:
        """
        Delete a directory
        
        Args:
            dir_path: Path to the directory to delete
            recursive: Whether to delete directory and all contents
            
        Returns:
            Dictionary with operation result
        """
        path = Path(dir_path)
        
        if not path.exists():
            return {
                'success': False,
                'message': f"Directory not found: {dir_path}",
                'path': dir_path
            }
        
        if not path.is_dir():
            return {
                'success': False,
                'message': f"Path is not a directory: {dir_path}",
                'path': dir_path
            }
        
        try:
            if recursive:
                # Count items before deletion
                item_count = len(list(path.rglob('*')))
                path.rmdir() if any(path.iterdir()) else path.rmdir()
                # Actually remove recursively
                shutil.rmtree(str(path))
                items_deleted = item_count
            else:
                # Check if directory is empty
                if any(path.iterdir()):
                    return {
                        'success': False,
                        'message': f"Directory not empty: {dir_path}. Use recursive=True to delete with contents.",
                        'path': dir_path
                    }
                path.rmdir()
                items_deleted = 0
            
            return {
                'success': True,
                'message': f"Directory deleted: {dir_path}",
                'path': dir_path,
                'items_deleted': items_deleted
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f"Error deleting directory: {str(e)}",
                'path': dir_path
            }
    
    def copy_file(self, source_path: str, destination_path: str, overwrite: bool = False) -> Dict[str, Any]:
        """
        Copy a file from source to destination
        
        Args:
            source_path: Path to the source file
            destination_path: Path to the destination
            overwrite: Whether to overwrite existing file
            
        Returns:
            Dictionary with operation result
        """
        source = Path(source_path)
        destination = Path(destination_path)
        
        if not source.exists():
            return {
                'success': False,
                'message': f"Source file not found: {source_path}",
                'source': source_path,
                'destination': destination_path
            }
        
        if not source.is_file():
            return {
                'success': False,
                'message': f"Source is not a file: {source_path}",
                'source': source_path,
                'destination': destination_path
            }
        
        if destination.exists() and not overwrite:
            return {
                'success': False,
                'message': f"Destination already exists: {destination_path}",
                'source': source_path,
                'destination': destination_path
            }
        
        try:
            # Create parent directories if needed
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy the file
            shutil.copy2(source, destination)
            
            return {
                'success': True,
                'message': f"File copied from {source_path} to {destination_path}",
                'source': source_path,
                'destination': destination_path,
                'size': destination.stat().st_size
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f"Error copying file: {str(e)}",
                'source': source_path,
                'destination': destination_path
            }
    
    def move_file(self, source_path: str, destination_path: str, overwrite: bool = False) -> Dict[str, Any]:
        """
        Move a file from source to destination
        
        Args:
            source_path: Path to the source file
            destination_path: Path to the destination
            overwrite: Whether to overwrite existing file
            
        Returns:
            Dictionary with operation result
        """
        source = Path(source_path)
        destination = Path(destination_path)
        
        if not source.exists():
            return {
                'success': False,
                'message': f"Source file not found: {source_path}",
                'source': source_path,
                'destination': destination_path
            }
        
        if destination.exists() and not overwrite:
            return {
                'success': False,
                'message': f"Destination already exists: {destination_path}",
                'source': source_path,
                'destination': destination_path
            }
        
        try:
            # Create parent directories if needed
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Move the file
            shutil.move(str(source), str(destination))
            
            return {
                'success': True,
                'message': f"File moved from {source_path} to {destination_path}",
                'source': source_path,
                'destination': destination_path
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f"Error moving file: {str(e)}",
                'source': source_path,
                'destination': destination_path
            }
    
    def rename_file(self, old_path: str, new_name: str) -> Dict[str, Any]:
        """
        Rename a file
        
        Args:
            old_path: Current path to the file
            new_name: New name for the file
            
        Returns:
            Dictionary with operation result
        """
        old_path_obj = Path(old_path)
        new_path = old_path_obj.parent / new_name
        
        if not old_path_obj.exists():
            return {
                'success': False,
                'message': f"File not found: {old_path}",
                'old_path': old_path,
                'new_name': new_name
            }
        
        if new_path.exists():
            return {
                'success': False,
                'message': f"File with name '{new_name}' already exists",
                'old_path': old_path,
                'new_name': new_name
            }
        
        try:
            old_path_obj.rename(new_path)
            
            return {
                'success': True,
                'message': f"File renamed from {old_path_obj.name} to {new_name}",
                'old_path': old_path,
                'new_path': str(new_path)
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f"Error renaming file: {str(e)}",
                'old_path': old_path,
                'new_name': new_name
            }
    
    def read_file(self, file_path: str, encoding: str = 'utf-8', max_size: int = 10*1024*1024) -> Dict[str, Any]:
        """
        Read file contents
        
        Args:
            file_path: Path to the file to read
            encoding: File encoding
            max_size: Maximum file size to read (10MB default)
            
        Returns:
            Dictionary with file contents and metadata
        """
        path = Path(file_path)
        
        if not path.exists():
            return {
                'success': False,
                'message': f"File not found: {file_path}",
                'path': file_path
            }
        
        if not path.is_file():
            return {
                'success': False,
                'message': f"Path is not a file: {file_path}",
                'path': file_path
            }
        
        try:
            file_size = path.stat().st_size
            
            if file_size > max_size:
                return {
                    'success': False,
                    'message': f"File too large ({file_size} bytes). Maximum size: {max_size} bytes",
                    'path': file_path,
                    'size': file_size
                }
            
            # Try to detect if it's a text file
            mime_type, _ = mimetypes.guess_type(str(path))
            is_text = mime_type and mime_type.startswith('text/') or path.suffix in self.supported_formats['text']
            
            if is_text:
                with open(path, 'r', encoding=encoding) as f:
                    content = f.read()
            else:
                # Read as binary for non-text files
                with open(path, 'rb') as f:
                    content = f.read()
                content = f"[Binary file - {file_size} bytes]"
            
            return {
                'success': True,
                'content': content,
                'path': file_path,
                'size': file_size,
                'encoding': encoding if is_text else 'binary',
                'mime_type': mime_type
            }
        
        except UnicodeDecodeError:
            return {
                'success': False,
                'message': f"Could not decode file with encoding: {encoding}",
                'path': file_path
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Error reading file: {str(e)}",
                'path': file_path
            }
    
    def write_file(self, file_path: str, content: str, encoding: str = 'utf-8', 
                   append: bool = False) -> Dict[str, Any]:
        """
        Write content to a file
        
        Args:
            file_path: Path to the file to write
            content: Content to write
            encoding: File encoding
            append: Whether to append to existing file
            
        Returns:
            Dictionary with operation result
        """
        path = Path(file_path)
        
        try:
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content
            mode = 'a' if append else 'w'
            with open(path, mode, encoding=encoding) as f:
                f.write(content)
            
            file_size = path.stat().st_size
            
            return {
                'success': True,
                'message': f"Content {'appended to' if append else 'written to'} {file_path}",
                'path': file_path,
                'size': file_size,
                'bytes_written': len(content.encode(encoding))
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f"Error writing file: {str(e)}",
                'path': file_path
            }
    
    def find_files(self, pattern: str, search_path: str = None, recursive: bool = True,
                   case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """
        Find files matching a pattern
        
        Args:
            pattern: Search pattern (supports wildcards)
            search_path: Path to search in (default: current directory)
            recursive: Whether to search recursively
            case_sensitive: Whether search is case sensitive
            
        Returns:
            List of matching files with information
        """
        search_dir = Path(search_path) if search_path else Path(self.base_directory)
        
        if not search_dir.exists():
            raise FileNotFoundError(f"Search directory not found: {search_path}")
        
        matches = []
        
        try:
            if recursive:
                glob_pattern = f"**/{pattern}"
                files = search_dir.glob(glob_pattern)
            else:
                files = search_dir.glob(pattern)
            
            for file_path in files:
                if file_path.is_file():
                    try:
                        stat_info = file_path.stat()
                        matches.append({
                            'name': file_path.name,
                            'path': str(file_path),
                            'size': stat_info.st_size,
                            'modified': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                            'extension': file_path.suffix.lower()
                        })
                    except (PermissionError, OSError):
                        # Skip inaccessible files
                        continue
        
        except Exception as e:
            raise RuntimeError(f"Error searching for files: {str(e)}")
        
        return matches
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get detailed information about a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file information
        """
        path = Path(file_path)
        
        if not path.exists():
            return {
                'success': False,
                'message': f"File not found: {file_path}",
                'path': file_path
            }
        
        try:
            stat_info = path.stat()
            
            info = {
                'success': True,
                'name': path.name,
                'path': str(path),
                'type': 'directory' if path.is_dir() else 'file',
                'size': stat_info.st_size,
                'created': datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                'accessed': datetime.fromtimestamp(stat_info.st_atime).isoformat(),
                'permissions': oct(stat_info.st_mode)[-3:],
                'extension': path.suffix.lower() if path.is_file() else '',
                'parent': str(path.parent),
                'absolute_path': str(path.absolute())
            }
            
            # Add file-specific info
            if path.is_file():
                info['mime_type'] = mimetypes.guess_type(str(path))[0]
                info['category'] = self._categorize_file(path.suffix.lower())
                
                # Check if file is readable
                try:
                    with open(path, 'rb') as f:
                        f.read(1)  # Try to read first byte
                    info['readable'] = True
                except:
                    info['readable'] = False
            else:
                # Directory-specific info
                try:
                    info['item_count'] = len(list(path.iterdir()))
                except PermissionError:
                    info['item_count'] = 'unknown'
            
            return info
        
        except Exception as e:
            return {
                'success': False,
                'message': f"Error getting file info: {str(e)}",
                'path': file_path
            }
    
    def get_directory_tree(self, root_path: str = None, max_depth: int = 3, 
                          include_files: bool = True) -> Dict[str, Any]:
        """
        Get directory tree structure
        
        Args:
            root_path: Root directory path
            max_depth: Maximum depth to traverse
            include_files: Whether to include files in tree
            
        Returns:
            Dictionary representing directory tree
        """
        root = Path(root_path) if root_path else Path(self.base_directory)
        
        if not root.exists():
            raise FileNotFoundError(f"Directory not found: {root_path}")
        
        def build_tree(path: Path, current_depth: int = 0) -> Dict[str, Any]:
            if current_depth > max_depth:
                return None
            
            try:
                node = {
                    'name': path.name,
                    'path': str(path),
                    'type': 'directory' if path.is_dir() else 'file'
                }
                
                if path.is_dir():
                    children = []
                    try:
                        for item in sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower())):
                            if include_files or item.is_dir():
                                child_node = build_tree(item, current_depth + 1)
                                if child_node:
                                    children.append(child_node)
                        
                        if children:
                            node['children'] = children
                            node['item_count'] = len(children)
                    
                    except PermissionError:
                        node['error'] = 'Access denied'
                
                elif path.is_file():
                    node['size'] = path.stat().st_size
                    node['extension'] = path.suffix.lower()
                
                return node
            
            except (PermissionError, OSError):
                return None
        
        return build_tree(root)
