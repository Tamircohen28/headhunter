"""
Research prompt construction and deep research step.
Step 3: Uses job metadata (from step 2) to fill the fixed prompt template,
saves it as .md, then runs OpenAI Deep Research in background, polls every
10 seconds, and saves the final result as a .md file.
"""

from typing import Any, Dict
import time

from .base_step import BaseStep
from ..utils.constants import BaseStepEnum, STEP_DETAILS
from ..utils.logger import log
from ..llm_client.openai_client import OpenAIClient


class ResearchPromptStep(BaseStep):
    """Step 3: Construct research prompt and run deep research."""

    def __init__(self, config: Any, file_manager: Any):
        step_enum = BaseStepEnum.RESEARCH_PROMPT
        step_details = STEP_DETAILS[step_enum]
        super().__init__(step_enum, step_details, config, file_manager)
        self.openai_client = OpenAIClient(config)

    def _execute(self, job_metadata: Dict[str, Any]) -> str:
        """Build prompt from job metadata, run research in background, save outputs."""
        # Build prompt text using the fixed template (placeholders mapped from job metadata)
        prompt_text = self._build_prompt(job_metadata)
        
        # Save the constructed prompt
        self._write_additional_file("research_prompt.md", prompt_text, file_type="markdown")
        
        # Start deep research in background
        response_id, started = self.openai_client.start_deep_research(prompt_text)
        if not started:
            raise ValueError(f"Failed to start deep research: {response_id}")
        
        # Poll every 10 seconds (configurable)
        poll_interval = int(self.config.poll_interval) if hasattr(self.config, 'poll_interval') else 10
        log("info", f"🔎 Research started. Polling every {poll_interval}s...", {"response_id": response_id})
        
        final_obj, success = self.openai_client.poll_research_status(response_id, poll_interval=poll_interval)
        if not success:
            raise ValueError(f"Deep research did not complete successfully: {final_obj}")
        
        # Extract full text and save as markdown result
        result_markdown, ok = self.openai_client.get_research_result_markdown(final_obj)
        if not ok:
            raise ValueError(result_markdown)
        
        self._write_additional_file("research_result.md", result_markdown, file_type="markdown")
        
        return result_markdown

    def _process_result(self, result: str) -> str:
        """Return the result markdown as-is (primary step output)."""
        if not isinstance(result, str) or not result.strip():
            raise ValueError("Empty research result")
        return result

    def _build_prompt(self, md: Dict[str, Any]) -> str:
        """
        Fill the provided prompt template with data from job metadata.
        Allowed: minimal placeholder adjustments only. We map fields safely.
        """
        company = md.get("company_name", "")
        role = md.get("job_title", "")
        location = md.get("location", "")
        job_link = md.get("job_url", "")
        
        # Subjects and subtopics: derive from topic_hierarchy if available, fall back to generic placeholders
        subject_lines = []
        topic_hierarchy = md.get("topic_hierarchy") or {}
        if isinstance(topic_hierarchy, dict) and topic_hierarchy:
            for subject_title, subtopics in topic_hierarchy.items():
                subject_lines.append(f"{subject_title}")
                # ensure at least 5 bullets
                sub_list = list(subtopics)[:5] if isinstance(subtopics, list) else []
                while len(sub_list) < 5:
                    sub_list.append("")
                subject_lines.append(f"\t•\t{sub_list[0]}")
                subject_lines.append(f"\t•\t{sub_list[1]}")
                subject_lines.append(f"\t•\t{sub_list[2]}")
                subject_lines.append(f"\t•\t{sub_list[3]}")
                subject_lines.append(f"\t•\t{sub_list[4]}")
                subject_lines.append("")
        else:
            # Single subject fallback from profession/discipline
            subject_title = md.get("discipline") or md.get("profession") or "Core Technical Topics"
            subtopics = (md.get("required_skills") or md.get("study_topics") or [])[:5]
            while len(subtopics) < 5:
                subtopics.append("")
            subject_lines = [
                f"{subject_title}",
                f"\t•\t{subtopics[0]}",
                f"\t•\t{subtopics[1]}",
                f"\t•\t{subtopics[2]}",
                f"\t•\t{subtopics[3]}",
                f"\t•\t{subtopics[4]}",
                ""
            ]
        subject_block = "\n".join(subject_lines).strip()
        
        docs_link = ""
        relevant_tools_or_repos = ""
        # Try to guess company docs or repos if provided in metadata
        # We intentionally keep empty if unknown to avoid altering template semantics
        
        # Build the exact provided template with placeholders filled
        template = f"""Research Agent Prompt: {company} {role} Interview Guide (No Emojis, With TOC & Appendix)

OBJECTIVE:
Generate a full, professional technical preparation document for the role below. The guide should be clean, in Markdown or Word format, with:
	•	No emojis or visual icons
	•	A full table of contents on the first page
	•	A detailed appendix at the end
	•	Full coverage of the subjects listed below, including subtopics
	•	Focused on interview-level knowledge, not academic theory

⸻

1. POSITION DETAILS
	•	Role: {role}
	•	Company: {company}
	•	Location: {location}
	•	Job Link: {job_link}

⸻

2. DOCUMENT STRUCTURE

Each section must include:
	•	Title
	•	Overview/Definition
	•	{company}-Specific Context or Relevance
	•	Key Concepts and Explanations
	•	Threats and Real-World Attack Scenarios
	•	Interview Q&A:
	•	Minimum 3 questions per topic, based on either:
	•	Real {company} candidate reports (Glassdoor, Blind, Reddit, etc.)
	•	Architect-level security interview patterns
	•	Follow-up or probing questions where available

At the beginning of the document, include:
	•	Table of Contents (TOC) with all sections and subsections
	•	Each section should be properly numbered (e.g., 1.1, 1.2…)

At the end of the document, include:
	•	Appendix:
	•	Glossary of terms
	•	Full acronym reference (e.g., PFS, TPM, TEEs)
	•	List of external references (docs, links, sources)
	•	Summary table of all security tools and {company} frameworks mentioned

⸻

3. CORE SUBJECTS TO COVER IN FULL DEPTH

Each of the following items is a required section, with sub-subtopics fully explained and mapped to {company} context. These form the backbone of the interview preparation.

{subject_block}

(Repeat section structure above for each technical topic in your guide.)

⸻

4. DATA SOURCES TO USE

Actively search and synthesize from:
	•	Glassdoor, Blind, Reddit (e.g., r/{company}, r/csMajors, r/netsec)
	•	LinkedIn posts by {company} security engineers or past interviewees
	•	YouTube (especially {company} system architect interview prep)
	•	Technical blogs ({company} Developer, Medium, etc.)
	•	{company} Docs ({docs_link})
	•	GitHub/{company} open-source projects ({relevant_tools_or_repos})

⸻

5. OUTPUT FORMATTING REQUIREMENTS
	•	Use clear headings, numbered sections, and subheadings
	•	No emojis, no bullet icons
	•	Q&A format must look like:
"""
        return template.strip()