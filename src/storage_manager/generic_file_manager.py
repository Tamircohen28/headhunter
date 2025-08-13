"""
Generic file manager for handling file operations.
Does not know about specific business logic like steps or runs.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime

from ..utils.logger import log


class GenericFileManager:
    """
    Generic file manager for handling file operations.
    
    This class provides basic file operations without knowing
    about specific business logic like steps or runs.
    """
    
    def __init__(self, base_dir: str):
        """
        Initialize the file manager.
        
        Args:
            base_dir: Base directory for all operations
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        log("info", "🔧 Generic file manager initialized", {"base_dir": str(self.base_dir)})
    
    def create_directory(self, path: str) -> str:
        """
        Create a directory at the specified path.
        
        Args:
            path: Directory path (relative to base_dir)
            
        Returns:
            Full path to created directory
        """
        try:
            full_path = self.base_dir / path
            full_path.mkdir(parents=True, exist_ok=True)
            
            log("debug", f"📁 Created directory: {full_path}")
            return str(full_path)
            
        except Exception as e:
            log("error", f"Failed to create directory {path}: {e}")
            raise
    
    def save_file(self, directory: str, filename: str, content: Any, file_type: str = "text") -> str:
        """
        Save content to a file.
        
        Args:
            directory: Directory to save file in
            filename: Name of the file
            content: Content to save
            file_type: Type of content (text, json, markdown)
            
        Returns:
            Full path to saved file
        """
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
            
            file_path = dir_path / filename
            
            if file_type == "json":
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(content, f, indent=2, ensure_ascii=False)
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(str(content))
            
            log("debug", f"💾 Saved {file_type} file: {file_path}")
            return str(file_path)
            
        except Exception as e:
            log("error", f"Failed to save file {filename}: {e}")
            raise
    
    def load_file(self, file_path: str, file_type: str = "text") -> Any:
        """
        Load content from a file.
        
        Args:
            file_path: Path to the file
            file_type: Type of content to load
            
        Returns:
            Loaded content
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            if file_type == "json":
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
                    
        except Exception as e:
            log("error", f"Failed to load file {file_path}: {e}")
            return None
    
    def file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file exists, False otherwise
        """
        return Path(file_path).exists()
    
    def directory_exists(self, dir_path: str) -> bool:
        """
        Check if a directory exists.
        
        Args:
            dir_path: Path to check
            
        Returns:
            True if directory exists, False otherwise
        """
        return Path(dir_path).is_dir()
    
    def list_files(self, directory: str, pattern: str = "*") -> list:
        """
        List files in a directory.
        
        Args:
            directory: Directory to list
            pattern: File pattern to match
            
        Returns:
            List of file paths
        """
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                return []
            
            return [str(f) for f in dir_path.glob(pattern)]
            
        except Exception as e:
            log("error", f"Failed to list files in {directory}: {e}")
            return []
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file.
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                log("debug", f"🗑️ Deleted file: {file_path}")
                return True
            return False
            
        except Exception as e:
            log("error", f"Failed to delete file {file_path}: {e}")
            return False
    
    def copy_file(self, source: str, destination: str) -> bool:
        """
        Copy a file from source to destination.
        
        Args:
            source: Source file path
            destination: Destination file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import shutil
            shutil.copy2(source, destination)
            log("debug", f"📋 Copied file: {source} -> {destination}")
            return True
            
        except Exception as e:
            log("error", f"Failed to copy file {source} -> {destination}: {e}")
            return False
