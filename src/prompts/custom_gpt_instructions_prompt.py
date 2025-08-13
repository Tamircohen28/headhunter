"""
Custom GPT Instructions Prompt implementation.
Generates prompts for creating custom GPT instructions.
"""

from .base_prompt import BasePrompt


class CustomGPTInstructionsPrompt(BasePrompt):
    """
    Prompt for generating custom GPT instructions.
    
    Required variables:
        - job_analysis: The job analysis data containing company, role, skills, etc.
    """
    
    def _validate_variables(self) -> None:
        """Validate required variables are present."""
        if not self.has_variable('job_analysis'):
            raise ValueError("Missing required variable: job_analysis")
    
    def _generate_template(self) -> str:
        """Generate the custom GPT instructions prompt template."""
        return """You are an expert at creating custom GPT instructions for job interview preparation. 

Based on the job analysis provided, create comprehensive, detailed instructions for a custom GPT that will help prepare for this specific role.

**Job Details:**
- Company: {company}
- Role: {role}
- Location: {location}

**Required Skills:**
{core_skills}

**Preferred Skills:**
{adjacent_skills}

**Nice to Have:**
{nice_to_have_skills}

**Role-Specific Topics:**
{role_topics}

**Instructions:**
Create detailed custom GPT instructions that include:

1. **Role Context**: Specific context about this company and role
2. **Technical Focus Areas**: Emphasize the key technical skills and technologies
3. **Interview Preparation**: Specific guidance for this type of position
4. **Company-Specific Knowledge**: Any relevant company culture, products, or focus areas
5. **Industry Context**: Relevant industry knowledge and trends
6. **Behavioral Focus**: Key behavioral competencies for this role
7. **Technical Questions**: Types of technical questions to expect
8. **Case Study Preparation**: Relevant case study or problem-solving approaches

Format the response as a comprehensive markdown document with clear sections and actionable guidance.

The instructions should be specific enough to make the GPT highly effective for this particular role, but generic enough to be useful for interview preparation."""
    
    def render(self) -> str:
        """Render the prompt with job analysis data."""
        job_analysis = self.get_variable('job_analysis')
        
        # Extract specific fields from job analysis
        company = job_analysis.get('company', 'Unknown Company')
        role = job_analysis.get('role', 'Unknown Role')
        location = job_analysis.get('location', 'Unknown Location')
        
        skills = job_analysis.get('skills', {})
        core_skills = '\n'.join([f"- {skill}" for skill in skills.get('core', [])])
        adjacent_skills = '\n'.join([f"- {skill}" for skill in skills.get('adjacent', [])])
        nice_to_have_skills = '\n'.join([f"- {skill}" for skill in skills.get('nice_to_have', [])])
        
        role_topics = '\n'.join([f"- {topic}" for topic in job_analysis.get('role_specific_topics', [])])
        
        # Update variables for template rendering
        self.variables.update({
            'company': company,
            'role': role,
            'location': location,
            'core_skills': core_skills,
            'adjacent_skills': adjacent_skills,
            'nice_to_have_skills': nice_to_have_skills,
            'role_topics': role_topics
        })
        
        return super().render()
