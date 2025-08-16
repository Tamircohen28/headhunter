"""
Job Metadata Extraction Prompt implementation.
Extracts structured job information from scraped job content.
"""

import json
from typing import Tuple
from .base_prompt import BasePrompt
from .job_metadata_extraction_request import JobMetadataExtractionRequest
from ..utils.job_metadata import JobMetadata


class JobMetadataExtractionPrompt(BasePrompt[JobMetadata]):
    """
    Prompt for extracting structured job metadata from scraped content.
    
    This prompt automatically generates its template from the JobMetadata class,
    ensuring no code duplication and automatic adaptation to class changes.
    """
    
    def __init__(self, request: JobMetadataExtractionRequest):
        """Initialize the prompt with a request object."""
        super().__init__(request)
        # Generate the template automatically from the JobMetadata class
        self._template = self._generate_template_from_class()
    
    def construct(self) -> str:
        """
        Construct the prompt from the input request.
        
        Returns:
            The complete prompt string ready to be sent to the LLM
        """
        # Get data from request
        job_content = self.request.job_content
        job_url = self.request.job_url
        
        # Generate the JSON schema automatically
        json_schema = self._generate_json_schema()
        
        # Construct the prompt
        prompt = f"""You are an expert job posting analyst with access to real-time web search. Your task is to extract structured information from the provided job posting content AND conduct online research to gather comprehensive, up-to-date information about the company, role, and past candidate experiences.

**Job Content to Analyze:**
{job_content}

**Job URL:**
{job_url}

**Your Task:**
1. **Extract Information** from the provided job posting content
2. **Conduct Web Research** to gather additional relevant information
3. **Combine and Structure** all information into a comprehensive JSON format

**Required Output Format:**
Return ONLY valid JSON with this exact schema:

{json_schema}

**Core Research Areas - MUST COVER ALL OF THESE:**

**1. Past Candidate Interview Experiences:**
- Search for interview experiences from same role, similar roles, and same company in different locations
- Look for Glassdoor reviews, interview feedback, candidate insights

**2. Company Hiring Process:**
- Research detailed stage breakdown (phone screen, technical rounds, behavioral, final, etc.)
- Find typical timelines for the hiring process
- Identify evaluation criteria used at each stage

**3. Technical Question Patterns:**
- Research technical questions grouped by domain (networking, security, cloud, embedded systems, etc.)
- Find common question types and formats used by the company

**4. Behavioral Questions:**
- Find common behavioral questions specific to this company
- Research company cultural values that behavioral questions target

**5. Preparation Tips & Pitfalls:**
- Gather insights from successful candidates about what worked
- Research common mistakes and pitfalls from unsuccessful candidates

**6. Keyword & Concept Mastery List:**
- Create comprehensive list of topics to study for the role
- Provide definition for each study topic
- Explain why each topic is relevant to the role
- Find study resources (courses, books, articles, practice problems)

**7. Structured Topic Hierarchy for Interview Preparation (NEW):**
- Create a COMPREHENSIVE and DETAILED topic hierarchy with 15-25 main topics for senior-level positions
- Each main topic should have 5-10 specific, technical sub-topics that demonstrate deep expertise
- Topics that depend on other topics should appear AFTER their prerequisites
- Use this structure: {{"Main Topic": ["sub-topic 1", "sub-topic 2", "sub-topic 3", "sub-topic 4", "sub-topic 5"]}}
- **QUALITY REQUIREMENTS:**
  * Each sub-topic should be specific and technical (e.g., "TLS 1.2 vs 1.3 differences" not just "TLS")
  * Include specific technologies, protocols, tools, and frameworks
  * Cover both theoretical concepts AND practical implementation details
  * Include security considerations, best practices, and common pitfalls
  * For technical roles, include specific vendor technologies (Intel, AMD, NVIDIA, etc.)
  * Include emerging technologies and current industry trends
  * Cover the full spectrum: fundamentals, intermediate, and advanced concepts

**EXAMPLE OF EXPECTED QUALITY:**
"Certificate Authorities (CA) & PKI": [
  "Root vs Intermediate CA hierarchy and trust chains",
  "X.509 certificate structure and extensions",
  "TLS certificate lifecycle management",
  "OCSP, CRL, and OCSP stapling mechanisms",
  "Public vs Private key cryptography fundamentals",
  "Certificate pinning and HSTS implementation",
  "CA compromise recovery procedures",
  "Certificate transparency and monitoring"
]

**TOPIC COVERAGE EXPECTATIONS:**
- **For Senior Technical Roles**: 15-25 main topics with 5-10 sub-topics each
- **For Management Roles**: 10-15 main topics with 3-7 sub-topics each
- **For Specialized Roles**: 20-30 main topics with 5-12 sub-topics each
- **Depth Level**: Each sub-topic should be interview-worthy and demonstrate senior-level expertise
- **Breadth**: Cover the entire domain, not just the most common areas
- **Current Trends**: Include recent technologies, frameworks, and industry developments

**Research Guidelines:**
- Use web search to find company news, Glassdoor reviews, LinkedIn insights, industry reports
- **EXTENSIVE RESEARCH REQUIRED FOR TOPIC HIERARCHY:**
  * Research current industry standards, frameworks, and best practices
  * Find recent technology trends, emerging tools, and vendor-specific solutions
  * Look for senior-level interview questions and technical deep-dives
  * Research domain-specific technologies, protocols, and implementation details
  * Find information about current security threats, vulnerabilities, and mitigation strategies
  * Research industry certifications, training programs, and skill requirements
- Extract every piece of information mentioned in the job posting
- Be accurate and use exact text when possible
- Don't assume this is a technical job - it could be any profession
- Categorize qualifications and skills into required, preferred, and nice-to-have
- Write a comprehensive job summary (2-3 sentences)
- Include any other important information in important_notes
- **Pay special attention to creating a logical topic hierarchy** - this will be used for research planning later

**Output Requirements:**
- Return ONLY valid JSON
- No additional text, explanations, or markdown formatting
- Ensure all JSON syntax is correct
- Include both job posting data AND web research findings
- Cover ALL 6 core research areas thoroughly
- **Create a comprehensive topic hierarchy with logical learning order** - this is critical for research planning
- **TOPIC HIERARCHY MUST BE COMPREHENSIVE**: 
  * Minimum 15 main topics for senior positions
  * Each topic must have 5-10 detailed sub-topics
  * Sub-topics must be specific and technical, not generic
  * Include current technologies, tools, and industry trends
  * Demonstrate senior-level depth and expertise
- **FAILURE TO PROVIDE COMPREHENSIVE TOPICS WILL RESULT IN INCOMPLETE PREPARATION**

Analyze the job content thoroughly, conduct comprehensive web research, and provide a complete, structured representation of all the information."""
        
        return prompt
    
    def deserialize(self, response: str) -> Tuple[bool, JobMetadata]:
        """
        Deserialize the LLM response into a JobMetadata object.
        
        Args:
            response: The raw response from the LLM
            
        Returns:
            Tuple of (success, JobMetadata object)
        """
        try:
            # Extract JSON content from the response
            json_content = self._extract_json_from_response(response)
            
            # Parse the JSON
            metadata_dict = json.loads(json_content)
            
            # Create JobMetadata instance from the dictionary
            job_metadata = JobMetadata.from_dict(metadata_dict)
            
            return True, job_metadata
            
        except json.JSONDecodeError as e:
            # Log the JSON parsing error
            from ..utils.logger import log
            log("error", f"❌ JSON parsing failed: {e}")
            log("error", f"❌ Attempted to parse: {json_content[:1000] if 'json_content' in locals() else 'No content extracted'}")
            
            # Try to create a basic JobMetadata object from the response text
            fallback_metadata = self._create_fallback_metadata(response)
            return False, fallback_metadata
            
        except Exception as e:
            # Log any other errors
            from ..utils.logger import log
            log("error", f"❌ Deserialization error: {e}")
            log("error", f"❌ Response was: {response[:1000]}...")
            
            # Try to create a basic JobMetadata object from the response text
            fallback_metadata = self._create_fallback_metadata(response)
            return False, fallback_metadata
    
    def _create_fallback_metadata(self, response: str) -> JobMetadata:
        """
        Create a basic JobMetadata object when deserialization fails.
        This extracts whatever information we can from the text response.
        
        Args:
            response: The raw LLM response
            
        Returns:
            A basic JobMetadata object with extracted information
        """
        from ..utils.job_metadata import JobMetadata
        
        # Create empty metadata object
        metadata = JobMetadata()
        
        # Try to extract basic information from the response text
        try:
            # Look for common patterns in the response
            if "job_title" in response.lower() or "title" in response.lower():
                # Try to find job title
                import re
                title_match = re.search(r'["\']?job_title["\']?\s*:\s*["\']([^"\']+)["\']', response, re.IGNORECASE)
                if title_match:
                    metadata.job_title = title_match.group(1)
                
                company_match = re.search(r'["\']?company_name["\']?\s*:\s*["\']([^"\']+)["\']', response, re.IGNORECASE)
                if company_match:
                    metadata.company_name = company_match.group(1)
            
            # Store the raw response for manual review
            metadata.raw_content = response
            metadata.important_notes = f"Deserialization failed. Raw response stored in raw_content. Response length: {len(response)} characters"
            
        except Exception as e:
            # If even fallback extraction fails, just store the response
            metadata.raw_content = response
            metadata.important_notes = f"Complete deserialization failure. Raw response stored. Error: {str(e)}"
        
        return metadata
    
    def _generate_template_from_class(self) -> str:
        """
        Automatically generate the prompt template from the JobMetadata class.
        This ensures the prompt always matches the current class structure.
        """
        # Create a sample instance to get field information
        sample_metadata = JobMetadata()
        
        # Get all fields and their types from the class
        fields_info = self._get_class_fields_info(sample_metadata)
        
        # Generate the JSON schema automatically
        json_schema = self._generate_json_schema_from_fields(fields_info)
        
        return json_schema
    
    def _generate_json_schema(self) -> str:
        """Generate JSON schema automatically from JobMetadata class fields."""
        # Create a sample instance to get field information
        sample_metadata = JobMetadata()
        fields_info = self._get_class_fields_info(sample_metadata)
        return self._generate_json_schema_from_fields(fields_info)
    
    def _get_class_fields_info(self, metadata_instance: JobMetadata) -> dict:
        """Get information about all fields in the JobMetadata class."""
        fields_info = {}
        
        for field_name, field_value in metadata_instance.__dict__.items():
            field_type = type(field_value).__name__
            fields_info[field_name] = {
                'name': field_name,
                'type': field_type,
                'value': field_value,
                'is_list': isinstance(field_value, list),
                'is_optional': field_name in ['application_deadline', 'start_date']
            }
        
        return fields_info
    
    def _generate_json_schema_from_fields(self, fields_info: dict) -> str:
        """Generate JSON schema automatically from class fields."""
        schema_lines = []
        schema_lines.append("{")
        
        for field_name, field_info in fields_info.items():
            field_type = field_info['type']
            is_list = field_info['is_list']
            is_optional = field_info['is_optional']
            
            if is_list:
                schema_lines.append(f'  "{field_name}": ["item1", "item2"],')
            elif field_type == 'str':
                if field_name == 'job_url':
                    schema_lines.append(f'  "{field_name}": "{{job_url}}",')
                elif field_name == 'job_summary':
                    schema_lines.append(f'  "{field_name}": "Your comprehensive summary of this job posting",')
                elif field_name == 'important_notes':
                    schema_lines.append(f'  "{field_name}": "Any other important information not captured above",')
                else:
                    schema_lines.append(f'  "{field_name}": "Value if mentioned, empty string otherwise",')
            elif field_type == 'NoneType' or is_optional:
                schema_lines.append(f'  "{field_name}": "value if mentioned, null otherwise",')
            else:
                schema_lines.append(f'  "{field_name}": "value",')
        
        # Remove trailing comma from last line
        if schema_lines:
            last_line = schema_lines[-1]
            if last_line.endswith(','):
                schema_lines[-1] = last_line[:-1]
        
        schema_lines.append("}")
        
        return '\n'.join(schema_lines)
    
    def _extract_json_from_response(self, response: str) -> str:
        """
        Extract JSON content from the LLM response.
        
        Args:
            response: The raw response from the LLM
            
        Returns:
            The extracted JSON string
            
        Raises:
            ValueError: If no valid JSON is found
        """
        # Remove any markdown formatting
        response = response.replace('```json', '').replace('```', '')
        
        # Try to find JSON content between curly braces
        # Look for the largest JSON block
        json_blocks = []
        brace_count = 0
        start_index = -1
        
        for i, char in enumerate(response):
            if char == '{':
                if brace_count == 0:
                    start_index = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and start_index != -1:
                    json_blocks.append(response[start_index:i+1])
                    start_index = -1
        
        if not json_blocks:
            # If no JSON blocks found, try to extract any content that looks like JSON
            import re
            # Look for content that starts with { and ends with }
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            matches = re.findall(json_pattern, response, re.DOTALL)
            if matches:
                # Use the longest match
                json_blocks = [max(matches, key=len)]
        
        if not json_blocks:
            raise ValueError("No JSON content found in response")
        
        # Use the largest JSON block
        largest_block = max(json_blocks, key=len)
        
        # Validate that it's actually valid JSON
        try:
            json.loads(largest_block)
            return largest_block
        except json.JSONDecodeError:
            # If the largest block isn't valid, try to clean it up
            # Remove any trailing commas or invalid characters
            cleaned_block = largest_block.rstrip(', \n\r\t')
            try:
                json.loads(cleaned_block)
                return cleaned_block
            except json.JSONDecodeError:
                # If still not valid, try to find a smaller valid block
                for block in sorted(json_blocks, key=len, reverse=True):
                    try:
                        json.loads(block)
                        return block
                    except json.JSONDecodeError:
                        continue
                
                # If all else fails, raise an error
                raise ValueError("No valid JSON found in response")
