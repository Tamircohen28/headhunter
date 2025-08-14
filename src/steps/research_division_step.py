"""
Research division step implementation.
"""

import json
from typing import Any, Dict
from .base_step import BaseStep
from ..prompts import ResearchDivisionPrompt
from ..llm_client.openai_client import OpenAIClient
from ..utils.constants import BaseStepEnum, STEP_DETAILS


class ResearchDivisionStep(BaseStep):
    """Step 4: Divide research topics among agents."""
    
    def __init__(self, config: Any, file_manager: Any):
        step_enum = BaseStepEnum.RESEARCH_DIVISION
        step_details = STEP_DETAILS[step_enum]
        super().__init__(step_enum, step_details, config, file_manager)
        self.openai_client = OpenAIClient(config)
        self.max_topics_per_agent = config.max_topics_per_agent
    
    def _execute(self, job_analysis: Dict[str, Any]) -> str:
        """Execute research topic division."""
        prompt = ResearchDivisionPrompt(
            job_analysis=job_analysis,
            max_topics_per_agent=self.max_topics_per_agent
        )
        
        result, success = self.openai_client.execute_prompt(prompt)
        if not success:
            raise ValueError(f"Research topic division failed: {result}")
        
        return result
    
    def _process_result(self, result: str) -> str:
        """Process research division result and convert to Markdown."""
        try:
            # Parse JSON response
            if "```json" in result:
                json_start = result.find("```json") + 7
                json_end = result.find("```", json_start)
                json_content = result[json_start:json_end].strip()
            else:
                json_start = result.find("{")
                json_end = result.rfind("}") + 1
                json_content = result[json_start:json_end]
            
            research_division = json.loads(json_content)
            
            # Convert to Markdown format and return directly
            markdown_content = self._convert_to_markdown(research_division)
            return markdown_content
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse research division response: {e}")
    
    def _convert_to_markdown(self, research_division: Dict[str, Any]) -> str:
        """Convert research division JSON to Markdown format."""
        try:
            markdown_lines = []
            
            # Add summary information
            total_agents = research_division.get('total_agents', 0)
            total_topics = research_division.get('total_topics', 0)
            
            markdown_lines.append(f"## total agents {total_agents}")
            markdown_lines.append("")
            markdown_lines.append(f"## total topics {total_topics}")
            markdown_lines.append("")
            
            # Process each research task
            for task in research_division.get('research_tasks', []):
                agent_id = task.get('agent_id', 'Unknown')
                topics = task.get('topics', [])
                topic_indices = task.get('topic_indices', [])
                prompt = task.get('prompt', '')
                
                # Agent header
                markdown_lines.append(f"## AGENT {agent_id}")
                markdown_lines.append("### Topics:")
                
                # Topics with indices
                for i, topic in enumerate(topics):
                    index = topic_indices[i] if i < len(topic_indices) else 'N/A'
                    markdown_lines.append(f"[{index}]: {topic}")
                
                markdown_lines.append("")
                
                # Full prompt for this agent
                markdown_lines.append(prompt)
                markdown_lines.append("")
                markdown_lines.append("--")
                markdown_lines.append("")
            
            # Join with proper blank lines (not \n)
            return "\n".join(markdown_lines)
            
        except Exception as e:
            return f"## Error converting to Markdown\n\n{str(e)}"
