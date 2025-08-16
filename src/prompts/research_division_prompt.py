"""
Research Division Prompt implementation.
Generates prompts for dividing research topics among agents.
"""

import json
from typing import Dict, Any, Tuple, List
from loguru import logger
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
    
    def validate_research_division(self, division: Dict[str, Any]) -> bool:
        """
        Validate that the research division is properly structured.
        
        Args:
            division: The research division to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check required structure
            if "research_tasks" not in division:
                logger.error("Missing 'research_tasks' in division")
                return False
            
            if "total_topics" not in division:
                logger.error("Missing 'total_topics' in division")
                return False
            
            if "total_agents" not in division:
                logger.error("Missing 'total_agents' in division")
                return False
            
            # Validate each task
            max_topics = self.get_variable('max_topics_per_agent')
            total_topics = 0
            
            for i, task in enumerate(division['research_tasks']):
                # Check required fields
                required_fields = ['agent_id', 'topics', 'topic_indices', 'description']
                for field in required_fields:
                    if field not in task:
                        logger.error(f"Task {i} missing required field: {field}")
                        return False
                
                # Check topic count
                topic_count = len(task['topics'])
                if topic_count > max_topics:
                    logger.error(f"Task {i} has too many topics: {topic_count} > {max_topics}")
                    return False
                
                if topic_count == 0:
                    logger.error(f"Task {i} has no topics")
                    return False
                
                # Check topic indices
                if len(task['topic_indices']) != topic_count:
                    logger.error(f"Task {i} topic count mismatch with indices")
                    return False
                
                total_topics += topic_count
            
            # Check total topics
            if total_topics != division['total_topics']:
                logger.warning(f"Total topics mismatch: calculated {total_topics}, stated {division['total_topics']}. Correcting...")
                # Fix the mismatch by updating the stated total to match the calculated total
                division['total_topics'] = total_topics
            
            # Check agent count
            if len(division['research_tasks']) != division['total_agents']:
                logger.warning(f"Agent count mismatch: tasks {len(division['research_tasks'])}, stated {division['total_agents']}. Correcting...")
                # Fix the mismatch by updating the stated total to match the actual count
                division['total_agents'] = len(division['research_tasks'])
            
            return True
            
        except Exception as e:
            logger.error(f"Research division validation failed: {e}")
            return False
    
    def create_research_prompts(self, division: Dict[str, Any], job_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create individual research prompts for each agent.
        
        Args:
            division: The research division
            job_analysis: The job analysis data
            
        Returns:
            List of research prompts for each agent
        """
        try:
            logger.info("🔍 Creating individual research prompts")
            
            prompts = []
            
            for task in division['research_tasks']:
                prompt = self._build_agent_prompt(task, job_analysis)
                prompts.append({
                    "agent_id": task['agent_id'],
                    "prompt": prompt,
                    "topics": task['topics'],
                    "topic_indices": task['topic_indices'],
                    "description": task['description']
                })
            
            logger.info(f"✅ Created {len(prompts)} research prompts")
            return prompts
            
        except Exception as e:
            logger.error(f"Failed to create research prompts: {e}")
            return []
    
    def _build_agent_prompt(self, task: Dict[str, Any], job_analysis: Dict[str, Any]) -> str:
        """
        Build a research prompt for a specific agent.
        
        Args:
            task: The research task for this agent
            job_analysis: The job analysis data
            
        Returns:
            The research prompt text
        """
        try:
            company = job_analysis.get('company', 'the company')
            role = job_analysis.get('role', 'the position')
            location = job_analysis.get('location', 'the location')
            
            topics_text = ", ".join(task['topics'])
            
            prompt = f"""You are a research analyst specializing in {role} positions. Your task is to research the following topics for a {role} role at {company} in {location}.

**Research Topics:**
{topics_text}

**Research Requirements:**
1. Find current, up-to-date information (within the last 2 years)
2. Focus on practical, interview-relevant details
3. Include specific examples, case studies, or real-world applications
4. Identify key trends, challenges, and opportunities in this domain
5. Provide actionable insights for interview preparation

**Output Format:**
Provide your research findings in a structured format with:
- Executive summary of key findings
- Detailed analysis of each topic
- Relevant statistics, examples, and case studies
- Key takeaways for interview preparation
- Sources and citations

**Focus Areas:**
- Industry trends and developments
- Technical requirements and standards
- Company-specific information (if publicly available)
- Interview preparation strategies
- Common challenges and solutions

Please conduct thorough research and provide comprehensive, well-structured findings that will help prepare for interviews in this role."""
            
            return prompt
            
        except Exception as e:
            logger.error(f"Failed to build agent prompt: {e}")
            return "Research prompt generation failed."
    
    def merge_research_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge research results from multiple agents.
        
        Args:
            results: List of research results from agents
            
        Returns:
            Merged research results
        """
        try:
            logger.info("🔍 Merging research results from agents")
            
            merged_results = {
                "total_agents": len(results),
                "completion_time": None,
                "research_summary": {},
                "detailed_findings": {},
                "key_insights": [],
                "sources": [],
                "recommendations": []
            }
            
            # Process each agent's results
            for result in results:
                agent_id = result.get('agent_id', 'unknown')
                
                if result.get('success', False):
                    # Extract key information
                    content = result.get('content', '')
                    
                    # Add to detailed findings
                    merged_results['detailed_findings'][agent_id] = {
                        'topics': result.get('topics', []),
                        'content': content,
                        'completion_time': result.get('completion_time'),
                        'usage': result.get('usage', {})
                    }
                    
                    # Extract key insights (simple text analysis)
                    if content:
                        # Add to key insights
                        merged_results['key_insights'].append(f"Agent {agent_id}: {content[:200]}...")
                        
                        # Extract sources if present
                        if 'sources:' in content.lower():
                            source_section = content[content.lower().find('sources:'):]
                            merged_results['sources'].append(source_section)
                
                else:
                    # Handle failed research
                    merged_results['detailed_findings'][agent_id] = {
                        'error': result.get('error', 'Unknown error'),
                        'topics': result.get('topics', [])
                    }
            
            # Generate overall summary
            successful_agents = sum(1 for r in results if r.get('success', False))
            merged_results['research_summary'] = {
                'total_agents': len(results),
                'successful_agents': successful_agents,
                'failed_agents': len(results) - successful_agents,
                'success_rate': f"{(successful_agents / len(results)) * 100:.1f}%"
            }
            
            logger.info("✅ Research results merged successfully")
            return merged_results
            
        except Exception as e:
            logger.error(f"Failed to merge research results: {e}")
            return {"error": f"Research merging failed: {str(e)}"}
