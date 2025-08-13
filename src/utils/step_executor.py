"""
Generic step executor utility for the job4u application.
Provides standardized step execution with logging, file saving, and state management.
"""

import time
from typing import Dict, Any, Callable, Optional, Tuple
from loguru import logger

from .exceptions import Job4UException
from ..storage_manager.file_manager import RunState


class StepExecutor:
    """
    Generic step executor that handles common step execution patterns.
    """
    
    def __init__(self, file_manager, conversation_handler):
        """
        Initialize the step executor.
        
        Args:
            file_manager: File manager instance
            conversation_handler: Conversation handler instance
        """
        self.file_manager = file_manager
        self.conversation_handler = conversation_handler
    
    def execute_step(self, run_dir: str, run_state: RunState, step_number: int, 
                    step_name: str, step_function: Callable, *args, **kwargs) -> Tuple[Any, bool]:
        """
        Execute a pipeline step with standardized logging, state management, and file saving.
        
        Args:
            run_dir: Path to the run directory
            run_state: Current run state
            step_number: The step number
            step_name: The step name
            step_function: Function to execute for this step
            *args: Arguments to pass to step function
            **kwargs: Keyword arguments to pass to step function
            
        Returns:
            Tuple of (step_result, success_status)
        """
        step_key = f"step_{step_number}"
        
        try:
            # Update run state - mark step as started
            logger.info(f"🔍 Step {step_number}: Starting {step_name}...")
            run_state.mark_step_started(step_number)
            self.file_manager.update_run_state(run_dir, run_state)
            
            # Execute the step
            start_time = time.time()
            step_result = step_function(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Check if step returned a tuple (result, success)
            if isinstance(step_result, tuple) and len(step_result) == 2:
                result, success = step_result
            else:
                result = step_result
                success = True
            
            if success:
                # Step completed successfully
                logger.info(f"✅ Step {step_number} completed: {step_name} ({execution_time:.2f}s)")
                
                # Save step result to file
                if result is not None:
                    file_path = self.file_manager.save_step_result(
                        run_dir, step_number, step_name, result
                    )
                    logger.debug(f"💾 Step result saved to: {file_path}")
                
                # Update run state - mark step as completed
                run_state.update_step(step_number, "completed")
                self.file_manager.update_run_state(run_dir, run_state)
                
                return result, True
            else:
                # Step failed
                error_msg = f"Step {step_name} failed"
                if isinstance(result, str):
                    error_msg = result
                
                logger.error(f"❌ Step {step_number} failed: {error_msg}")
                
                # Update run state - mark step as failed
                run_state.update_step(step_number, "failed", error=error_msg)
                self.file_manager.update_run_state(run_dir, run_state)
                
                return error_msg, False
                
        except Exception as e:
            # Step execution error
            error_msg = f"Step {step_name} execution error: {str(e)}"
            logger.error(f"❌ Step {step_number} error: {error_msg}")
            
            # Update run state - mark step as failed
            run_state.update_step(step_number, "failed", error=error_msg)
            self.file_manager.update_run_state(run_dir, run_state)
            
            return error_msg, False
    
    def execute_step_with_conversation(self, run_dir: str, run_state: RunState, 
                                     step_number: int, step_name: str, 
                                     step_function: Callable, conversation_id: str,
                                     *args, **kwargs) -> Tuple[Any, bool]:
        """
        Execute a step that requires conversation context.
        
        Args:
            run_dir: Path to the run directory
            run_state: Current run state
            step_number: The step number
            step_name: The step name
            step_function: Function to execute for this step
            conversation_id: Conversation ID to use
            *args: Arguments to pass to step function
            **kwargs: Keyword arguments to pass to step function
            
        Returns:
            Tuple of (step_result, success_status)
        """
        try:
            # Set conversation context
            self.conversation_handler.set_conversation_context(conversation_id)
            
            # Execute the step
            result, success = self.execute_step(
                run_dir, run_state, step_number, step_name, 
                step_function, *args, **kwargs
            )
            
            # Update conversation ID in run state if successful
            if success and run_state.conversation_id != conversation_id:
                run_state.conversation_id = conversation_id
                self.file_manager.update_run_state(run_dir, run_state)
            
            return result, success
            
        except Exception as e:
            error_msg = f"Step {step_name} conversation error: {str(e)}"
            logger.error(f"❌ Step {step_number} conversation error: {error_msg}")
            
            # Update run state - mark step as failed
            run_state.update_step(step_number, "failed", error=error_msg)
            self.file_manager.update_run_state(run_dir, run_state)
            
            return error_msg, False
    
    def execute_step_with_validation(self, run_dir: str, run_state: RunState,
                                   step_number: int, step_name: str,
                                   step_function: Callable, validation_function: Callable,
                                   *args, **kwargs) -> Tuple[Any, bool]:
        """
        Execute a step with result validation.
        
        Args:
            run_dir: Path to the run directory
            run_state: Current run state
            step_number: The step number
            step_name: The step name
            step_function: Function to execute for this step
            validation_function: Function to validate step result
            *args: Arguments to pass to step function
            **kwargs: Keyword arguments to pass to step function
            
        Returns:
            Tuple of (step_result, success_status)
        """
        try:
            # Execute the step
            result, success = self.execute_step(
                run_dir, run_state, step_number, step_name,
                step_function, *args, **kwargs
            )
            
            if success and result is not None:
                # Validate the result
                try:
                    validation_result = validation_function(result)
                    if not validation_result:
                        error_msg = f"Step {step_name} result validation failed"
                        logger.error(f"❌ Step {step_number} validation failed: {error_msg}")
                        
                        # Update run state - mark step as failed
                        run_state.update_step(step_number, "failed", error=error_msg)
                        self.file_manager.update_run_state(run_dir, run_state)
                        
                        return error_msg, False
                    
                    logger.debug(f"✅ Step {step_number} result validation passed")
                    
                except Exception as e:
                    error_msg = f"Step {step_name} validation error: {str(e)}"
                    logger.error(f"❌ Step {step_number} validation error: {error_msg}")
                    
                    # Update run state - mark step as failed
                    run_state.update_step(step_number, "failed", error=error_msg)
                    self.file_manager.update_run_state(run_dir, run_state)
                    
                    return error_msg, False
            
            return result, success
            
        except Exception as e:
            error_msg = f"Step {step_name} validation execution error: {str(e)}"
            logger.error(f"❌ Step {step_number} validation execution error: {error_msg}")
            
            # Update run state - mark step as failed
            run_state.update_step(step_number, "failed", error=error_msg)
            self.file_manager.update_run_state(run_dir, run_state)
            
            return error_msg, False
    
    def execute_step_with_retry(self, run_dir: str, run_state: RunState,
                               step_number: int, step_name: str,
                               step_function: Callable, max_retries: int = 3,
                               *args, **kwargs) -> Tuple[Any, bool]:
        """
        Execute a step with retry logic.
        
        Args:
            run_dir: Path to the run directory
            run_state: Current run state
            step_number: The step number
            step_name: The step name
            step_function: Function to execute for this step
            max_retries: Maximum number of retry attempts
            *args: Arguments to pass to step function
            **kwargs: Keyword arguments to pass to step function
            
        Returns:
            Tuple of (step_result, success_status)
        """
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    logger.warning(f"🔄 Step {step_number} retry attempt {attempt}/{max_retries}")
                
                # Execute the step
                result, success = self.execute_step(
                    run_dir, run_state, step_number, step_name,
                    step_function, *args, **kwargs
                )
                
                if success:
                    return result, True
                
                # If this was the last attempt, return the failure
                if attempt == max_retries:
                    return result, False
                
                # Wait before retry (exponential backoff)
                wait_time = 2 ** attempt
                logger.info(f"⏳ Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
                
            except Exception as e:
                error_msg = f"Step {step_name} retry attempt {attempt + 1} error: {str(e)}"
                logger.error(f"❌ Step {step_number} retry error: {error_msg}")
                
                # If this was the last attempt, return the failure
                if attempt == max_retries:
                    run_state.update_step(step_number, "failed", error=error_msg)
                    self.file_manager.update_run_state(run_dir, run_state)
                    return error_msg, False
                
                # Wait before retry
                wait_time = 2 ** attempt
                logger.info(f"⏳ Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
        
        # This should never be reached, but just in case
        error_msg = f"Step {step_name} exceeded maximum retry attempts"
        logger.error(f"❌ Step {step_number} exceeded retry attempts: {error_msg}")
        
        run_state.update_step(step_number, "failed", error=error_msg)
        self.file_manager.update_run_state(run_dir, run_state)
        
        return error_msg, False
    
    def check_step_prerequisites(self, run_state: RunState, step_number: int, 
                               required_steps: list) -> bool:
        """
        Check if all required steps have been completed before executing a step.
        
        Args:
            run_state: Current run state
            step_number: The step number to check
            required_steps: List of required step numbers
            
        Returns:
            True if all prerequisites are met, False otherwise
        """
        try:
            for req_step in required_steps:
                step_key = f"step_{req_step}"
                if step_key not in run_state.step_statuses:
                    logger.error(f"❌ Step {step_number} prerequisite missing: {step_key}")
                    return False
                
                step_status = run_state.step_statuses[step_key]
                if step_status.get("status") != "completed":
                    logger.error(f"❌ Step {step_number} prerequisite not completed: {step_key} ({step_status.get('status')})")
                    return False
            
            logger.debug(f"✅ Step {step_number} prerequisites met")
            return True
            
        except Exception as e:
            logger.error(f"❌ Step {step_number} prerequisite check error: {e}")
            return False
    
    def get_step_progress(self, run_state: RunState) -> Dict[str, Any]:
        """Get progress information for the run."""
        return {
            "current_step": run_state.current_step,
            "total_steps": run_state.total_steps,
            "status": run_state.status,
            "step_statuses": run_state.step_statuses
        }
    
    def get_step_name(self, step_number: int) -> str:
        """Get the step name for a given step number."""
        step_names = {
            1: "job_description_scraping",
            2: "job_analysis",
            3: "custom_gpt_instructions",
            4: "research_prompt_division",
            5: "research_execution",
            6: "interview_guide",
            7: "study_timeline"
        }
        return step_names.get(step_number, f"step_{step_number}")
