"""
Research Division Prompt implementation.
Generates prompts for dividing research topics among agents.
"""

from .base_prompt import BasePrompt


class ResearchDivisionPrompt(BasePrompt):
    """
    Prompt for dividing research topics among agents.
    
    Required variables:
        - job_analysis: The job analysis data containing skills and topics
        - max_topics_per_agent: Maximum number of topics per agent
    """
    
    def _validate_variables(self) -> None:
        """Validate required variables are present."""
        required_vars = ['job_analysis', 'max_topics_per_agent']
        missing_vars = [var for var in required_vars if not self.has_variable(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")
    
    def _generate_template(self) -> str:
        """Generate the research division prompt template."""
        return """You are dividing research topics among research agents for interview preparation.

**Job Context:**
- Company: {company}
- Role: {role}
- Location: {location}

**Available Topics:**
{all_topics}

**Requirements:**
- Maximum {max_topics_per_agent} topics per agent
- Create logical groupings of related topics
- Ensure balanced workload across agents
- Each topic should appear only once
- Provide clear descriptions for each agent's research focus

**Output Format:**
Return ONLY valid JSON with this schema:
{{
  "total_agents": <number>,
  "total_topics": <number>,
  "research_tasks": [
    {{
      "agent_id": "agent_001",
      "topics": ["topic1", "topic2", ...],
      "topic_indices": [0, 1, ...],
      "description": "Clear description of this agent's research focus"
    }}
  ]
}}

**Guidelines:**
- Group related topics together (e.g., programming languages, cloud technologies, soft skills)
- Ensure each agent has a clear, focused research area
- Make descriptions specific and actionable
- Use topic indices that correspond to the original topic list order

Divide the topics logically and efficiently among the agents."""
    
    def render(self) -> str:
        """Render the prompt with job analysis data."""
        job_analysis = self.get_variable('job_analysis')
        max_topics = self.get_variable('max_topics_per_agent')
        
        # Extract specific fields from job analysis
        company = job_analysis.get('company', 'Unknown Company')
        role = job_analysis.get('role', 'Unknown Role')
        location = job_analysis.get('location', 'Unknown Location')
        
        # Collect all topics from skills and role-specific topics
        all_topics = []
        
        # Add skills
        skills = job_analysis.get('skills', {})
        all_topics.extend(skills.get('core', []))
        all_topics.extend(skills.get('adjacent', []))
        all_topics.extend(skills.get('nice_to_have', []))
        
        # Add role-specific topics
        all_topics.extend(job_analysis.get('role_specific_topics', []))
        
        # Remove duplicates and format
        unique_topics = list(dict.fromkeys(all_topics))  # Preserve order
        topics_text = '\n'.join([f"- {topic}" for topic in unique_topics])
        
        # Update variables for template rendering
        self.variables.update({
            'company': company,
            'role': role,
            'location': location,
            'all_topics': topics_text,
            'max_topics_per_agent': max_topics
        })
        
        return super().render()
