"""
Job Analysis Prompt implementation.
Generates prompts for analyzing job descriptions.
"""

from .base_prompt import BasePrompt


class JobAnalysisPrompt(BasePrompt):
    """
    Prompt for job description analysis.
    
    Required variables:
        - job_description: The job description text
        - job_url: The URL of the job posting
    """
    
    def _validate_variables(self) -> None:
        """Validate required variables are present."""
        required_vars = ['job_description', 'job_url']
        missing_vars = [var for var in required_vars if not self.has_variable(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")
    
    def _generate_template(self) -> str:
        """Generate the job analysis prompt template."""
        return """You are analyzing a job description to prepare interview research. You MAY browse the web. Your tasks:
1) Identify company, role, location, job_link (prefer the given URL if unsure).
2) Derive/up-to-date hiring process (stages, assessments, timelines).
3) Extract skills: core, adjacent, nice_to_have.
4) List role_specific_topics (technologies, frameworks, domain themes).
5) If any prominent interviewer information is publicly known and relevant, include it (optional). Do not fabricate.
6) Determine geography_context (e.g., Israel/US/EU/Remote) when clear.
7) Include a citations[] array of source URLs used for your findings.

Return ONLY valid JSON with this schema:
{{
  "company": "string",
  "role": "string",
  "location": "string",
  "job_link": "string",
  "hiring_process": [
    {{
      "stage": "string",
      "what_to_expect": "string",
      "evaluation_focus": ["list of phrases"]
    }}
  ],
  "skills": {{
    "core": ["list"],
    "adjacent": ["list"],
    "nice_to_have": ["list"]
  }},
  "role_specific_topics": ["list"],
  "interviewer_notes": {{
    "name": "string or empty",
    "interests": ["list"],
    "use_sparingly": true
  }},
  "geography_context": "string",
  "citations": ["list of source links (if none, empty array)"]
}}

Guidelines:
- Be conservative. If unsure, leave fields empty or use best inference grounded in JD + credible sources.
- Concise, information-dense text.
- No prose outside JSON.

Job URL: {job_url}
Job Description: {job_description}"""
