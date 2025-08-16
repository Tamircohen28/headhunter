"""
Research Planning Prompt implementation.
Generates prompts for planning research based on job content analysis.
"""

from .base_prompt import BasePrompt


class ResearchPlanningPrompt(BasePrompt):
    """
    Prompt for planning research based on job content analysis.
    
    Required variables:
        - job_content: The scraped job description content
        - company: The company name (if available)
        - role: The job role/title (if available)
    """
    
    def _validate_variables(self) -> None:
        """Validate required variables are present."""
        if not self.has_variable('job_content'):
            raise ValueError("Missing required variable: job_content")
    
    def _generate_template(self) -> str:
        """Generate the research planning prompt template."""
        return """You are an expert research planner for job interview preparation. Based on the provided job description, create a comprehensive research plan that will guide interview preparation research.

**Job Content to Analyze:**
{job_content}

**Company Information:**
Company: {company}
Role: {role}

**Your Task:**
Create a detailed research plan that establishes exactly what research will look for. The plan should be comprehensive and actionable.

**Core Research Areas (Always Include):**

1. **Past Candidate Interview Experiences**
   - Same role at this company
   - Similar roles at this company
   - Same role at different company locations
   - Similar roles at competitor companies

2. **Company Hiring Process**
   - Stage breakdown (phone screen, technical rounds, onsite, etc.)
   - Typical timelines for each stage
   - Evaluation criteria and scoring methods
   - Decision-making process

3. **Technical Question Patterns**
   - Grouped by domain (e.g., networking, security, cloud, embedded systems)
   - Specific technical areas mentioned in the job description
   - Difficulty levels and complexity
   - Practical vs. theoretical focus

4. **Behavioral Questions**
   - Common behavioral questions for this company
   - Questions tied to company cultural values
   - Leadership and teamwork scenarios
   - Problem-solving and decision-making situations

5. **Preparation Tips & Pitfalls**
   - Insights from successful candidates
   - Common mistakes and how to avoid them
   - Specific preparation strategies for this role
   - Resources and study materials

6. **Keyword & Concept Mastery List**
   - Comprehensive set of topics to study
   - Each topic should include:
     * Definition and explanation
     * Relevance to the role
     * Study resources and references
     * Priority level (High/Medium/Low)

**Output Format:**
Provide a structured research plan with clear sections for each research area. For each area, include:
- Specific research questions to answer
- Key information to gather
- Sources to investigate
- Expected outcomes

**Focus Areas:**
- Make the plan specific to this company and role
- Include technical domains mentioned in the job description
- Consider the company's industry and technology stack
- Address both technical and cultural aspects
- Provide actionable research directions

The research plan should be comprehensive enough to guide multiple research agents and ensure complete coverage of all interview preparation needs."""
    
    def render(self) -> str:
        """Render the prompt with job content data."""
        job_content = self.get_variable('job_content')
        
        # Extract company and role from job content if not provided
        company = self.get_variable('company', 'Unknown Company')
        role = self.get_variable('role', 'Unknown Role')
        
        # If company/role not provided, try to extract from job content
        if company == 'Unknown Company':
            # Look for company indicators in the content
            company_indicators = ['Microsoft', 'Google', 'Apple', 'Amazon', 'Meta', 'Netflix', 'Twitter', 'LinkedIn']
            for indicator in company_indicators:
                if indicator.lower() in job_content.lower():
                    company = indicator
                    break
        
        if role == 'Unknown Role':
            # Look for role indicators in the content
            role_indicators = ['Engineer', 'Developer', 'Manager', 'Analyst', 'Architect', 'Scientist', 'Consultant']
            for indicator in role_indicators:
                if indicator.lower() in job_content.lower():
                    role = indicator
                    break
        
        # Update variables for template rendering
        self.variables.update({
            'job_content': job_content,
            'company': company,
            'role': role
        })
        
        return super().render()
