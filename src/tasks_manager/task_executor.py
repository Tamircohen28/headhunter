"""
Task executor component for job4u application.
Manages and executes research tasks using multiple research agents.
"""

import time
import json
from typing import Dict, Any, List, Tuple
from loguru import logger

from ..utils.config import Config
from ..llm_client.base_client import BaseLLMClient


class TaskExecutor:
    """
    Executes research tasks using multiple research agents.
    """
    
    def __init__(self, config: Config, llm_client: BaseLLMClient):
        """
        Initialize the task executor.
        
        Args:
            config: Configuration instance
            llm_client: LLM client for executing research tasks
        """
        self.config = config
        self.llm_client = llm_client
        self.research_config = config.get_research_config()
        self.deep_research_config = config.get_deep_research_config()
        
        # Task tracking
        self.active_tasks = {}
        self.completed_tasks = {}
        self.failed_tasks = {}
        
        logger.info("🔧 Task executor initialized successfully")
    
    def execute_research_tasks(self, research_prompts: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], bool]:
        """
        Execute multiple research tasks using research agents.
        
        Args:
            research_prompts: List of research prompts for each agent
            
        Returns:
            Tuple of (research_results, success_status)
        """
        try:
            logger.info(f"🚀 Starting execution of {len(research_prompts)} research tasks")
            
            # Start all research tasks
            for prompt_data in research_prompts:
                self._start_research_task(prompt_data)
            
            # Wait for all tasks to complete
            results = self._wait_for_all_tasks_completion()
            
            if results:
                logger.info("✅ All research tasks completed successfully")
                return results, True
            else:
                logger.error("❌ Some research tasks failed to complete")
                return {"error": "Some research tasks failed"}, False
                
        except Exception as e:
            error_msg = f"Research task execution failed: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}, False
    
    def _start_research_task(self, prompt_data: Dict[str, Any]) -> None:
        """
        Start a single research task.
        
        Args:
            prompt_data: The research prompt data for this task
        """
        try:
            agent_id = prompt_data['agent_id']
            prompt = prompt_data['prompt']
            topics = prompt_data['topics']
            
            logger.info(f"🚀 Starting research task for agent {agent_id}")
            
            # Start Deep Research
            response_id, success = self.llm_client.start_deep_research(prompt, {
                'agent_id': agent_id,
                'topics': topics,
                'start_time': time.time()
            })
            
            if success:
                # Track the active task
                self.active_tasks[agent_id] = {
                    'response_id': response_id,
                    'prompt': prompt,
                    'topics': topics,
                    'start_time': time.time(),
                    'status': 'running',
                    'last_poll_time': time.time(),
                    'poll_count': 0
                }
                
                logger.info(f"✅ Research task started for agent {agent_id} with response_id: {response_id}")
            else:
                # Mark as failed
                self.failed_tasks[agent_id] = {
                    'error': 'Failed to start research',
                    'topics': topics,
                    'start_time': time.time()
                }
                logger.error(f"❌ Failed to start research task for agent {agent_id}")
                
        except Exception as e:
            logger.error(f"Error starting research task for agent {prompt_data.get('agent_id', 'unknown')}: {e}")
            self.failed_tasks[prompt_data.get('agent_id', 'unknown')] = {
                'error': str(e),
                'topics': prompt_data.get('topics', []),
                'start_time': time.time()
            }
    
    def _wait_for_all_tasks_completion(self) -> Dict[str, Any]:
        """
        Wait for all active research tasks to complete.
        
        Returns:
            Dictionary containing all research results
        """
        try:
            max_wait_time = self.research_config['max_research_time']
            poll_interval = self.research_config['poll_interval']
            start_time = time.time()
            
            logger.info(f"⏳ Waiting for {len(self.active_tasks)} research tasks to complete (max {max_wait_time}s)")
            
            while self.active_tasks and (time.time() - start_time) < max_wait_time:
                # Poll all active tasks
                self._poll_all_active_tasks()
                
                # Check for completed tasks
                self._check_completed_tasks()
                
                # If all tasks are done, break
                if not self.active_tasks:
                    break
                
                # Wait before next poll
                time.sleep(poll_interval)
            
            # Handle timeout
            if self.active_tasks:
                logger.warning(f"⚠️ Research timeout reached. {len(self.active_tasks)} tasks still running")
                self._handle_timeout_tasks()
            
            # Compile final results
            return self._compile_final_results()
            
        except Exception as e:
            logger.error(f"Error waiting for task completion: {e}")
            return {"error": f"Task completion monitoring failed: {str(e)}"}
    
    def _poll_all_active_tasks(self) -> None:
        """Poll all active research tasks for status updates."""
        try:
            current_time = time.time()
            
            for agent_id, task_info in list(self.active_tasks.items()):
                # Check if we should poll this task
                if (current_time - task_info['last_poll_time']) >= self.research_config['poll_interval']:
                    self._poll_single_task(agent_id, task_info)
                    
        except Exception as e:
            logger.error(f"Error polling active tasks: {e}")
    
    def _poll_single_task(self, agent_id: str, task_info: Dict[str, Any]) -> None:
        """Poll a single research task for status updates."""
        try:
            response_id = task_info['response_id']
            
            # Poll the research status
            status_info, success = self.llm_client.poll_research_status(response_id)
            
            if success:
                # Update task info
                task_info['status'] = status_info.get('status', 'unknown')
                task_info['last_poll_time'] = time.time()
                task_info['poll_count'] += 1
                
                logger.debug(f"Agent {agent_id} status: {status_info.get('status', 'unknown')} (poll #{task_info['poll_count']})")
                
                # Check if task is complete
                if status_info.get('status') == 'completed':
                    self._complete_research_task(agent_id, response_id)
                elif status_info.get('status') in ['failed', 'cancelled']:
                    self._fail_research_task(agent_id, f"Research {status_info.get('status')}")
            else:
                logger.warning(f"Failed to poll status for agent {agent_id}: {status_info.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Error polling task for agent {agent_id}: {e}")
    
    def _complete_research_task(self, agent_id: str, response_id: str) -> None:
        """Mark a research task as completed and retrieve results."""
        try:
            logger.info(f"✅ Research task completed for agent {agent_id}")
            
            # Get the research result
            result, success = self.llm_client.get_research_result(response_id)
            
            if success:
                # Move to completed tasks
                task_info = self.active_tasks.pop(agent_id)
                self.completed_tasks[agent_id] = {
                    'agent_id': agent_id,
                    'topics': task_info['topics'],
                    'content': result.get('content', ''),
                    'usage': result.get('usage', {}),
                    'completion_time': result.get('completed_at'),
                    'start_time': task_info['start_time'],
                    'success': True
                }
                
                logger.info(f"✅ Research results retrieved for agent {agent_id}")
            else:
                # Mark as failed
                self._fail_research_task(agent_id, f"Failed to retrieve results: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Error completing research task for agent {agent_id}: {e}")
            self._fail_research_task(agent_id, str(e))
    
    def _fail_research_task(self, agent_id: str, error: str) -> None:
        """Mark a research task as failed."""
        try:
            logger.error(f"❌ Research task failed for agent {agent_id}: {error}")
            
            # Move to failed tasks
            task_info = self.active_tasks.pop(agent_id)
            self.failed_tasks[agent_id] = {
                'agent_id': agent_id,
                'topics': task_info['topics'],
                'error': error,
                'start_time': task_info['start_time'],
                'success': False
            }
            
        except Exception as e:
            logger.error(f"Error failing research task for agent {agent_id}: {e}")
    
    def _handle_timeout_tasks(self) -> None:
        """Handle tasks that have timed out."""
        try:
            logger.warning(f"⏰ Handling {len(self.active_tasks)} timed out tasks")
            
            for agent_id, task_info in list(self.active_tasks.items()):
                self._fail_research_task(agent_id, "Research timeout exceeded")
                
        except Exception as e:
            logger.error(f"Error handling timeout tasks: {e}")
    
    def _compile_final_results(self) -> Dict[str, Any]:
        """Compile final results from all completed and failed tasks."""
        try:
            total_tasks = len(self.completed_tasks) + len(self.failed_tasks)
            successful_tasks = len(self.completed_tasks)
            failed_tasks = len(self.failed_tasks)
            
            results = {
                'summary': {
                    'total_tasks': total_tasks,
                    'successful_tasks': successful_tasks,
                    'failed_tasks': failed_tasks,
                    'success_rate': f"{(successful_tasks / total_tasks) * 100:.1f}%" if total_tasks > 0 else "0%"
                },
                'completed_tasks': self.completed_tasks,
                'failed_tasks': self.failed_tasks,
                'execution_time': time.time() - getattr(self, '_start_time', time.time())
            }
            
            logger.info(f"📊 Final results compiled: {successful_tasks}/{total_tasks} tasks successful")
            return results
            
        except Exception as e:
            logger.error(f"Error compiling final results: {e}")
            return {"error": f"Results compilation failed: {str(e)}"}
    
    def get_task_status(self) -> Dict[str, Any]:
        """Get current status of all tasks."""
        return {
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len(self.completed_tasks),
            'failed_tasks': len(self.failed_tasks),
            'total_tasks': len(self.active_tasks) + len(self.completed_tasks) + len(self.failed_tasks)
        }
    
    def cancel_all_tasks(self) -> None:
        """Cancel all active research tasks."""
        try:
            logger.warning(f"🚫 Cancelling {len(self.active_tasks)} active research tasks")
            
            for agent_id in list(self.active_tasks.keys()):
                self._fail_research_task(agent_id, "Task cancelled by user")
                
        except Exception as e:
            logger.error(f"Error cancelling tasks: {e}")
    
    def retry_failed_task(self, agent_id: str) -> bool:
        """Retry a failed research task."""
        try:
            if agent_id not in self.failed_tasks:
                logger.warning(f"Agent {agent_id} not found in failed tasks")
                return False
            
            # Get the failed task info
            failed_task = self.failed_tasks.pop(agent_id)
            
            # Restart the task
            self._start_research_task({
                'agent_id': agent_id,
                'prompt': failed_task.get('prompt', ''),
                'topics': failed_task.get('topics', [])
            })
            
            logger.info(f"🔄 Retrying failed task for agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error retrying failed task for agent {agent_id}: {e}")
            return False
