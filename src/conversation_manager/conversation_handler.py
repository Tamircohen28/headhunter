"""
Conversation handler component for job4u application.
Manages conversation context and state for LLM interactions.
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from loguru import logger

from ..utils.config import Config
from ..utils.helpers import generate_unique_id


class ConversationHandler:
    """
    Manages conversation context and state for LLM interactions.
    """
    
    def __init__(self, config: Config):
        """
        Initialize the conversation handler.
        
        Args:
            config: Configuration instance
        """
        self.config = config
        self.output_config = config.get_output_config()
        
        # Conversation state
        self.current_conversation_id = None
        self.conversation_messages = []
        self.conversation_metadata = {}
        
        # Conversation history
        self.conversation_history = {}
        
        logger.info("🔧 Conversation handler initialized successfully")
    
    def create_new_conversation(self, job_url: str, job_analysis: Dict[str, Any] = None) -> str:
        """
        Create a new conversation session.
        
        Args:
            job_url: The URL of the job being discussed
            job_analysis: Optional job analysis data
            
        Returns:
            The new conversation ID
        """
        try:
            # Generate unique conversation ID
            conversation_id = generate_unique_id()
            
            # Initialize conversation
            self.current_conversation_id = conversation_id
            self.conversation_messages = []
            self.conversation_metadata = {
                'conversation_id': conversation_id,
                'job_url': job_url,
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'message_count': 0,
                'total_tokens': 0,
                'status': 'active'
            }
            
            # Add initial context if job analysis is provided
            if job_analysis:
                self.add_system_message("Job Analysis Context", json.dumps(job_analysis, indent=2))
            
            # Store in history
            self.conversation_history[conversation_id] = {
                'metadata': self.conversation_metadata.copy(),
                'messages': self.conversation_messages.copy()
            }
            
            logger.info(f"💬 Created new conversation: {conversation_id}")
            return conversation_id
            
        except Exception as e:
            logger.error(f"Failed to create new conversation: {e}")
            raise
    
    def load_conversation(self, conversation_id: str) -> bool:
        """
        Load an existing conversation.
        
        Args:
            conversation_id: The ID of the conversation to load
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            if conversation_id not in self.conversation_history:
                logger.warning(f"Conversation {conversation_id} not found in history")
                return False
            
            # Load conversation data
            conversation_data = self.conversation_history[conversation_id]
            self.current_conversation_id = conversation_id
            self.conversation_messages = conversation_data['messages'].copy()
            self.conversation_metadata = conversation_data['metadata'].copy()
            
            # Update last accessed time
            self.conversation_metadata['last_accessed'] = datetime.now().isoformat()
            
            logger.info(f"💬 Loaded conversation: {conversation_id} ({len(self.conversation_messages)} messages)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load conversation {conversation_id}: {e}")
            return False
    
    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None) -> str:
        """
        Add a message to the current conversation.
        
        Args:
            role: The role of the message sender (user, assistant, system)
            content: The message content
            metadata: Optional metadata for the message
            
        Returns:
            The message ID
        """
        try:
            if not self.current_conversation_id:
                logger.warning("No active conversation. Creating new one.")
                self.create_new_conversation("unknown")
            
            # Generate message ID
            message_id = generate_unique_id()
            
            # Create message object
            message = {
                'id': message_id,
                'role': role,
                'content': content,
                'timestamp': datetime.now().isoformat(),
                'metadata': metadata or {}
            }
            
            # Add to conversation
            self.conversation_messages.append(message)
            
            # Update metadata
            self.conversation_metadata['message_count'] = len(self.conversation_messages)
            self.conversation_metadata['last_updated'] = datetime.now().isoformat()
            
            # Update history
            if self.current_conversation_id in self.conversation_history:
                self.conversation_history[self.current_conversation_id]['messages'] = self.conversation_messages.copy()
                self.conversation_history[self.current_conversation_id]['metadata'] = self.conversation_metadata.copy()
            
            logger.debug(f"💬 Added {role} message to conversation {self.current_conversation_id}")
            return message_id
            
        except Exception as e:
            logger.error(f"Failed to add message: {e}")
            raise
    
    def add_system_message(self, title: str, content: str) -> str:
        """
        Add a system message to provide context.
        
        Args:
            title: Title/description of the system message
            content: The system message content
            
        Returns:
            The message ID
        """
        return self.add_message("system", f"{title}: {content}")
    
    def add_user_message(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """
        Add a user message to the conversation.
        
        Args:
            content: The user message content
            metadata: Optional metadata
            
        Returns:
            The message ID
        """
        return self.add_message("user", content, metadata)
    
    def add_assistant_message(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """
        Add an assistant message to the conversation.
        
        Args:
            content: The assistant message content
            metadata: Optional metadata
            
        Returns:
            The message ID
        """
        return self.add_message("assistant", content, metadata)
    
    def set_conversation_context(self, conversation_id: str) -> None:
        """
        Set the conversation context for subsequent operations.
        
        Args:
            conversation_id: The conversation ID to set as current
        """
        try:
            if conversation_id in self.conversation_history:
                # Load existing conversation
                self.load_conversation(conversation_id)
                logger.debug(f"💬 Set conversation context to existing: {conversation_id}")
            else:
                # Create new conversation if it doesn't exist
                self.current_conversation_id = conversation_id
                logger.debug(f"💬 Set conversation context to new: {conversation_id}")
                
        except Exception as e:
            logger.error(f"Failed to set conversation context: {e}")
            raise
    
    def get_conversation_messages(self, conversation_id: Optional[str] = None, 
                                 max_messages: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get messages from a conversation.
        
        Args:
            conversation_id: The conversation ID (defaults to current)
            max_messages: Maximum number of messages to return
            
        Returns:
            List of conversation messages
        """
        try:
            target_conversation_id = conversation_id or self.current_conversation_id
            
            if not target_conversation_id:
                return []
            
            if target_conversation_id not in self.conversation_history:
                logger.warning(f"Conversation {target_conversation_id} not found")
                return []
            
            messages = self.conversation_history[target_conversation_id]['messages']
            
            if max_messages:
                messages = messages[-max_messages:]
            
            return messages.copy()
            
        except Exception as e:
            logger.error(f"Failed to get conversation messages: {e}")
            return []
    
    def get_conversation_context(self, conversation_id: Optional[str] = None, 
                                context_length: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent conversation context for LLM interactions.
        
        Args:
            conversation_id: The conversation ID (defaults to current)
            context_length: Number of recent messages to include
            
        Returns:
            List of recent messages for context
        """
        try:
            messages = self.get_conversation_messages(conversation_id, context_length)
            
            # Filter out system messages that are too long
            filtered_messages = []
            for message in messages:
                if message['role'] == 'system':
                    # Truncate long system messages
                    content = message['content']
                    if len(content) > 1000:
                        content = content[:1000] + "..."
                    
                    filtered_messages.append({
                        'role': message['role'],
                        'content': content
                    })
                else:
                    filtered_messages.append({
                        'role': message['role'],
                        'content': message['content']
                    })
            
            return filtered_messages
            
        except Exception as e:
            logger.error(f"Failed to get conversation context: {e}")
            return []
    
    def get_conversation_summary(self, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a summary of a conversation.
        
        Args:
            conversation_id: The conversation ID (defaults to current)
            
        Returns:
            Dictionary containing conversation summary
        """
        try:
            target_conversation_id = conversation_id or self.current_conversation_id
            
            if not target_conversation_id or target_conversation_id not in self.conversation_history:
                return {"error": "Conversation not found"}
            
            conversation_data = self.conversation_history[target_conversation_id]
            metadata = conversation_data['metadata']
            messages = conversation_data['messages']
            
            # Count message types
            message_counts = {}
            for message in messages:
                role = message['role']
                message_counts[role] = message_counts.get(role, 0) + 1
            
            # Calculate conversation duration
            created_at = datetime.fromisoformat(metadata['created_at'])
            last_updated = datetime.fromisoformat(metadata['last_updated'])
            duration = (last_updated - created_at).total_seconds()
            
            summary = {
                'conversation_id': target_conversation_id,
                'job_url': metadata.get('job_url', 'Unknown'),
                'created_at': metadata['created_at'],
                'last_updated': metadata['last_updated'],
                'duration_seconds': duration,
                'total_messages': metadata['message_count'],
                'message_breakdown': message_counts,
                'status': metadata['status'],
                'total_tokens': metadata.get('total_tokens', 0)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get conversation summary: {e}")
            return {"error": str(e)}
    
    def update_conversation_metadata(self, updates: Dict[str, Any]) -> bool:
        """
        Update conversation metadata.
        
        Args:
            updates: Dictionary of metadata updates
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            if not self.current_conversation_id:
                logger.warning("No active conversation to update")
                return False
            
            # Update metadata
            self.conversation_metadata.update(updates)
            self.conversation_metadata['last_updated'] = datetime.now().isoformat()
            
            # Update history
            if self.current_conversation_id in self.conversation_history:
                self.conversation_history[self.current_conversation_id]['metadata'] = self.conversation_metadata.copy()
            
            logger.debug(f"💬 Updated conversation metadata: {updates}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update conversation metadata: {e}")
            return False
    
    def save_conversation(self, conversation_id: Optional[str] = None) -> str:
        """
        Save a conversation to disk.
        
        Args:
            conversation_id: The conversation ID to save (defaults to current)
            
        Returns:
            Path to the saved conversation file
        """
        try:
            target_conversation_id = conversation_id or self.current_conversation_id
            
            if not target_conversation_id:
                logger.warning("No conversation to save")
                return ""
            
            if target_conversation_id not in self.conversation_history:
                logger.warning(f"Conversation {target_conversation_id} not found")
                return ""
            
            # Create conversations directory
            conversations_dir = Path(self.output_config['output_dir']) / "conversations"
            conversations_dir.mkdir(parents=True, exist_ok=True)
            
            # Save conversation file
            conversation_file = conversations_dir / f"{target_conversation_id}.json"
            
            conversation_data = {
                'metadata': self.conversation_history[target_conversation_id]['metadata'],
                'messages': self.conversation_history[target_conversation_id]['messages']
            }
            
            with open(conversation_file, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=2, default=str)
            
            logger.info(f"💾 Saved conversation {target_conversation_id} to {conversation_file}")
            return str(conversation_file)
            
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
            return ""
    
    def load_conversation_from_file(self, conversation_file: str) -> bool:
        """
        Load a conversation from a saved file.
        
        Args:
            conversation_file: Path to the conversation file
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            file_path = Path(conversation_file)
            if not file_path.exists():
                logger.warning(f"Conversation file not found: {conversation_file}")
                return False
            
            # Load conversation data
            with open(file_path, 'r', encoding='utf-8') as f:
                conversation_data = json.load(f)
            
            # Extract conversation ID
            conversation_id = conversation_data['metadata']['conversation_id']
            
            # Store in history
            self.conversation_history[conversation_id] = conversation_data
            
            # Set as current conversation
            self.current_conversation_id = conversation_id
            self.conversation_messages = conversation_data['messages'].copy()
            self.conversation_metadata = conversation_data['metadata'].copy()
            
            logger.info(f"💬 Loaded conversation {conversation_id} from {conversation_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load conversation from file: {e}")
            return False
    
    def close_conversation(self, conversation_id: Optional[str] = None) -> bool:
        """
        Close a conversation and save it.
        
        Args:
            conversation_id: The conversation ID to close (defaults to current)
            
        Returns:
            True if closed successfully, False otherwise
        """
        try:
            target_conversation_id = conversation_id or self.current_conversation_id
            
            if not target_conversation_id:
                logger.warning("No conversation to close")
                return False
            
            # Update status
            self.update_conversation_metadata({'status': 'closed'})
            
            # Save conversation
            self.save_conversation(target_conversation_id)
            
            # Clear current conversation if it's the one being closed
            if target_conversation_id == self.current_conversation_id:
                self.current_conversation_id = None
                self.conversation_messages = []
                self.conversation_metadata = {}
            
            logger.info(f"💬 Closed conversation: {target_conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to close conversation: {e}")
            return False
    
    def get_all_conversations(self) -> List[Dict[str, Any]]:
        """
        Get summary of all conversations.
        
        Returns:
            List of conversation summaries
        """
        try:
            summaries = []
            
            for conversation_id in self.conversation_history:
                summary = self.get_conversation_summary(conversation_id)
                if 'error' not in summary:
                    summaries.append(summary)
            
            # Sort by last updated time
            summaries.sort(key=lambda x: x['last_updated'], reverse=True)
            
            return summaries
            
        except Exception as e:
            logger.error(f"Failed to get all conversations: {e}")
            return []
    
    def cleanup_old_conversations(self, max_age_hours: int = 24) -> int:
        """
        Clean up old conversations.
        
        Args:
            max_age_hours: Maximum age in hours before cleanup
            
        Returns:
            Number of conversations cleaned up
        """
        try:
            current_time = datetime.now()
            cutoff_time = current_time.timestamp() - (max_age_hours * 3600)
            
            cleaned_count = 0
            
            for conversation_id in list(self.conversation_history.keys()):
                conversation_data = self.conversation_history[conversation_id]
                last_updated = datetime.fromisoformat(conversation_data['metadata']['last_updated'])
                
                if last_updated.timestamp() < cutoff_time:
                    # Close and remove old conversation
                    self.close_conversation(conversation_id)
                    del self.conversation_history[conversation_id]
                    cleaned_count += 1
            
            if cleaned_count > 0:
                logger.info(f"🧹 Cleaned up {cleaned_count} old conversations")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old conversations: {e}")
            return 0
