"""
Job Metadata class for structured job information.
Represents all the key information extracted from a job posting.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class JobMetadata:
    """
    Structured representation of job posting information.
    
    This class captures all the essential information from a job posting
    in a structured format that can be used throughout the pipeline.
    Designed to be generic and work with any profession or industry.
    """
    
    # Basic job information
    job_title: str = ""
    company_name: str = ""
    location: str = ""
    job_url: str = ""
    
    # Employment details
    employment_type: str = ""  # Full-time, Part-time, Contract, etc.
    work_site: str = ""        # Remote, On-site, Hybrid
    travel_percentage: str = "" # 0-25%, 25-50%, etc.
    
    # Role classification
    role_type: str = ""        # Individual Contributor, Manager, etc.
    profession: str = ""       # Any profession: Software Engineering, Law, HR, Medicine, etc.
    discipline: str = ""       # Specific discipline within profession
    
    # Experience and seniority (common across all jobs)
    experience_level: str = "" # Entry, Mid, Senior, Lead, etc.
    years_experience: str = "" # 0-2 years, 5+ years, etc.
    
    # Education requirements
    education_level: str = ""  # High School, Bachelor's, Master's, PhD
    education_field: str = ""  # Any field: Computer Science, Law, Business, etc.
    
    # Qualifications and requirements (generic approach)
    required_qualifications: List[str] = field(default_factory=list)  # Any required qualifications
    preferred_qualifications: List[str] = field(default_factory=list) # Any preferred qualifications
    nice_to_have_qualifications: List[str] = field(default_factory=list) # Any nice-to-have qualifications
    
    # Skills (generic - could be technical, soft skills, domain-specific, etc.)
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    nice_to_have_skills: List[str] = field(default_factory=list)
    
    # Technical requirements (optional - only if relevant to the job)
    technical_requirements: List[str] = field(default_factory=list)  # Any technical requirements
    tools_and_technologies: List[str] = field(default_factory=list)  # Any tools, software, technologies
    
    # Industry and domain knowledge
    industry: str = ""         # Technology, Healthcare, Finance, Law, Education, etc.
    domain_knowledge: List[str] = field(default_factory=list)  # Any domain-specific knowledge
    
    # Company information
    company_size: str = ""     # Startup, Mid-size, Enterprise
    company_industry: str = "" # Technology, Healthcare, Law, etc.
    company_culture: List[str] = field(default_factory=list)   # Values, work style, etc.
    
    # Job details
    job_description: str = ""  # Full job description text
    key_responsibilities: List[str] = field(default_factory=list)
    benefits: List[str] = field(default_factory=list)
    
    # Hiring process information
    hiring_process: List[str] = field(default_factory=list)    # Interview stages, timeline
    target_interview_stages: List[str] = field(default_factory=list)  # Specific interview stages mentioned
    application_deadline: Optional[str] = None
    start_date: Optional[str] = None
    
    # Interview and assessment information
    interview_topics: List[str] = field(default_factory=list)  # Topics that might come up in interviews
    assessment_methods: List[str] = field(default_factory=list)  # How candidates will be evaluated
    
    # Core Research Areas - Enhanced metadata for comprehensive research
    # 1. Past candidate interview experiences
    past_candidate_experiences: List[str] = field(default_factory=list)  # Same role, similar roles, same company different locations
    candidate_feedback: List[str] = field(default_factory=list)  # Glassdoor, interview reviews, candidate insights
    
    # 2. Company hiring process details
    hiring_stages: List[str] = field(default_factory=list)  # Detailed stage breakdown
    hiring_timeline: str = ""  # Typical timeline for the hiring process
    evaluation_criteria: List[str] = field(default_factory=list)  # How candidates are evaluated at each stage
    
    # 3. Technical question patterns
    technical_question_domains: List[str] = field(default_factory=list)  # Networking, security, cloud, embedded systems, etc.
    technical_question_patterns: List[str] = field(default_factory=list)  # Common question types and formats
    domain_specific_questions: Dict[str, List[str]] = field(default_factory=dict)  # Questions grouped by domain
    
    # 4. Behavioral questions
    behavioral_questions: List[str] = field(default_factory=list)  # Common behavioral questions for the company
    cultural_values: List[str] = field(default_factory=list)  # Company values that behavioral questions target
    leadership_questions: List[str] = field(default_factory=list)  # Leadership and management questions if applicable
    
    # 5. Preparation tips & pitfalls
    preparation_tips: List[str] = field(default_factory=list)  # Insights from successful candidates
    common_pitfalls: List[str] = field(default_factory=list)  # What unsuccessful candidates did wrong
    success_strategies: List[str] = field(default_factory=list)  # Strategies that worked for others
    
    # 6. Keyword & concept mastery list
    study_topics: List[str] = field(default_factory=list)  # Comprehensive list of topics to study
    topic_definitions: Dict[str, str] = field(default_factory=dict)  # Definition of each study topic
    topic_relevance: Dict[str, str] = field(default_factory=dict)  # Why each topic is relevant to the role
    study_resources: Dict[str, List[str]] = field(default_factory=dict)  # Resources for studying each topic
    
    # 7. Structured Topic Hierarchy for Interview Preparation (NEW)
    # This represents the logical learning order - topics that depend on others appear later
    topic_hierarchy: Dict[str, List[str]] = field(default_factory=dict)  # Main topic -> list of sub-topics
    topic_dependencies: Dict[str, List[str]] = field(default_factory=dict)  # Topic -> list of prerequisite topics
    topic_learning_order: List[str] = field(default_factory=list)  # Topics in logical learning sequence
    
    # Additional context
    job_summary: str = ""      # LLM-generated summary of the job
    important_notes: str = ""  # Any other important information not captured above
    extracted_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Raw data preservation
    raw_content: str = ""      # Original scraped content for reference
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the JobMetadata to a dictionary."""
        return {
            "job_title": self.job_title,
            "company_name": self.company_name,
            "location": self.location,
            "job_url": self.job_url,
            "employment_type": self.employment_type,
            "work_site": self.work_site,
            "travel_percentage": self.travel_percentage,
            "role_type": self.role_type,
            "profession": self.profession,
            "discipline": self.discipline,
            "experience_level": self.experience_level,
            "years_experience": self.years_experience,
            "education_level": self.education_level,
            "education_field": self.education_field,
            "required_qualifications": self.required_qualifications,
            "preferred_qualifications": self.preferred_qualifications,
            "nice_to_have_qualifications": self.nice_to_have_qualifications,
            "required_skills": self.required_skills,
            "preferred_skills": self.preferred_skills,
            "nice_to_have_skills": self.nice_to_have_skills,
            "technical_requirements": self.technical_requirements,
            "tools_and_technologies": self.tools_and_technologies,
            "industry": self.industry,
            "domain_knowledge": self.domain_knowledge,
            "company_size": self.company_size,
            "company_industry": self.company_industry,
            "company_culture": self.company_culture,
            "job_description": self.job_description,
            "key_responsibilities": self.key_responsibilities,
            "benefits": self.benefits,
            "hiring_process": self.hiring_process,
            "target_interview_stages": self.target_interview_stages,
            "application_deadline": self.application_deadline,
            "start_date": self.start_date,
            "interview_topics": self.interview_topics,
            "assessment_methods": self.assessment_methods,
            "past_candidate_experiences": self.past_candidate_experiences,
            "candidate_feedback": self.candidate_feedback,
            "hiring_stages": self.hiring_stages,
            "hiring_timeline": self.hiring_timeline,
            "evaluation_criteria": self.evaluation_criteria,
            "technical_question_domains": self.technical_question_domains,
            "technical_question_patterns": self.technical_question_patterns,
            "domain_specific_questions": self.domain_specific_questions,
            "behavioral_questions": self.behavioral_questions,
            "cultural_values": self.cultural_values,
            "leadership_questions": self.leadership_questions,
            "preparation_tips": self.preparation_tips,
            "common_pitfalls": self.common_pitfalls,
            "success_strategies": self.success_strategies,
            "study_topics": self.study_topics,
            "topic_definitions": self.topic_definitions,
            "topic_relevance": self.topic_relevance,
            "study_resources": self.study_resources,
            "topic_hierarchy": self.topic_hierarchy,
            "topic_dependencies": self.topic_dependencies,
            "topic_learning_order": self.topic_learning_order,
            "job_summary": self.job_summary,
            "important_notes": self.important_notes,
            "extracted_at": self.extracted_at,
            "raw_content": self.raw_content
        }
    
    def to_json(self) -> str:
        """Convert the JobMetadata to a JSON string."""
        import json
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JobMetadata':
        """Create a JobMetadata instance from a dictionary."""
        return cls(**data)
    
    def get_qualifications_by_priority(self) -> Dict[str, List[str]]:
        """Get qualifications organized by priority level."""
        return {
            "required": self.required_qualifications,
            "preferred": self.preferred_qualifications,
            "nice_to_have": self.nice_to_have_qualifications
        }
    
    def get_skills_by_priority(self) -> Dict[str, List[str]]:
        """Get skills organized by priority level."""
        return {
            "required": self.required_skills,
            "preferred": self.preferred_skills,
            "nice_to_have": self.nice_to_have_skills
        }
    
    def get_all_qualifications(self) -> List[str]:
        """Get all qualifications combined into a single list."""
        all_qualifications = []
        all_qualifications.extend(self.required_qualifications)
        all_qualifications.extend(self.preferred_qualifications)
        all_qualifications.extend(self.nice_to_have_qualifications)
        return list(set(all_qualifications))  # Remove duplicates
    
    def get_all_skills(self) -> List[str]:
        """Get all skills combined into a single list."""
        all_skills = []
        all_skills.extend(self.required_skills)
        all_skills.extend(self.preferred_skills)
        all_skills.extend(self.nice_to_have_skills)
        return list(set(all_skills))  # Remove duplicates
    
    def get_technical_requirements(self) -> Dict[str, List[str]]:
        """Get technical requirements organized by category."""
        return {
            "requirements": self.technical_requirements,
            "tools_and_technologies": self.tools_and_technologies
        }
    
    def is_complete(self) -> bool:
        """Check if the JobMetadata has essential information."""
        essential_fields = [
            self.job_title,
            self.company_name,
            self.job_description
        ]
        return all(field.strip() for field in essential_fields)
    
    def get_missing_fields(self) -> List[str]:
        """Get list of fields that are empty or missing."""
        missing = []
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, str) and not field_value.strip():
                missing.append(field_name)
            elif isinstance(field_value, list) and not field_value:
                missing.append(field_name)
        return missing
    
    def get_results_class_data(self) -> Dict[str, Any]:
        """
        Get data formatted for the results class requirements.
        
        Returns:
            Dictionary with the specific fields needed for results class
        """
        return {
            # 1. Job role – Title, seniority level, and key domain
            "job_role": {
                "title": self.job_title,
                "seniority_level": self.experience_level,
                "key_domain": self.discipline or self.profession
            },
            
            # 2. Company – Name, industry, location(s)
            "company": {
                "name": self.company_name,
                "industry": self.company_industry or self.industry,
                "location": self.location
            },
            
            # 3. Official job description – URL or text
            "job_description": {
                "url": self.job_url,
                "text": self.job_description
            },
            
            # 4. Target interview stage(s)
            "target_interview_stages": self.target_interview_stages or self.hiring_process,
            
            # 5. Known technical keywords (optional)
            "technical_keywords": {
                "skills": self.get_all_skills(),
                "qualifications": self.get_all_qualifications(),
                "technical_requirements": self.technical_requirements,
                "tools_and_technologies": self.tools_and_technologies
            },
            
            # 6. Potential interviewer info (optional)
            "potential_interviewer_info": {
                "interview_topics": self.interview_topics,
                "assessment_methods": self.assessment_methods,
                "domain_knowledge": self.domain_knowledge
            },
            
            # Enhanced Research Areas for comprehensive interview preparation
            "core_research_areas": {
                # 1. Past candidate interview experiences
                "past_candidate_experiences": {
                    "experiences": self.past_candidate_experiences,
                    "feedback": self.candidate_feedback
                },
                
                # 2. Company hiring process
                "hiring_process_details": {
                    "stages": self.hiring_stages,
                    "timeline": self.hiring_timeline,
                    "evaluation_criteria": self.evaluation_criteria
                },
                
                # 3. Technical question patterns
                "technical_questions": {
                    "domains": self.technical_question_domains,
                    "patterns": self.technical_question_patterns,
                    "domain_specific": self.domain_specific_questions
                },
                
                # 4. Behavioral questions
                "behavioral_questions": {
                    "questions": self.behavioral_questions,
                    "cultural_values": self.cultural_values,
                    "leadership_questions": self.leadership_questions
                },
                
                # 5. Preparation tips & pitfalls
                "preparation_insights": {
                    "tips": self.preparation_tips,
                    "pitfalls": self.common_pitfalls,
                    "success_strategies": self.success_strategies
                },
                
                # 6. Keyword & concept mastery
                "study_mastery": {
                    "topics": self.study_topics,
                    "definitions": self.topic_definitions,
                    "relevance": self.topic_relevance,
                    "resources": self.study_resources
                },
                
                # 7. Structured Topic Hierarchy for Research (NEW)
                "topic_hierarchy": {
                    "hierarchy": self.topic_hierarchy,  # Main topic -> list of sub-topics
                    "dependencies": self.topic_dependencies,  # Topic -> prerequisite topics
                    "learning_order": self.topic_learning_order  # Logical learning sequence
                }
            }
        }
