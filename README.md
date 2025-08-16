# 🚀 Job4U - AI-Powered Interview Preparation Pipeline

A comprehensive system for automating job interview preparation through:
- Web scraping of job descriptions
- AI-powered analysis and research
- Custom GPT instruction generation
- Multi-agent research task execution
- Comprehensive study material generation

## 🏗️ **Architecture Overview**

Job4U has been refactored into a clean, modular architecture with clear separation of concerns:

```
job4u/                          # Project root
├── main.py                      # Main pipeline orchestration
├── cli.py                       # Command-line interface
├── src/                         # Source code package
│   ├── utils/                   # Shared utilities and configuration
│   ├── llm_client/              # LLM service interface and implementations
│   ├── scraper/                 # Web interactions and scraping
│   ├── prompts/                 # All prompt generation and management
│   ├── tasks_manager/           # LLM task execution and management
│   ├── conversation_manager/    # Conversation handling and state
│   └── storage_manager/         # Storage and persistence
├── requirements.txt              # Python dependencies
├── setup.py                     # Package configuration
├── env_example.txt              # Environment variables template
└── README.md                    # This file
```

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.8+
- OpenAI API key
- Job URL to analyze

### **Installation**
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `env_example.txt` to `.env` and fill in your configuration
4. Run the pipeline: `python3 cli.py` or `python3 main.py`

### **Environment Configuration**
Create a `.env` file with the following variables:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here
TEST_JOB_URL=https://example.com/job-posting

# Optional (with defaults)
OPENAI_MODEL_BROWSING=gpt-4o-mini
OPENAI_MODEL_WRITING=gpt-4o-mini
OPENAI_TEMPERATURE=0.5
OPENAI_MAX_TOKENS=5000
OPENAI_TIMEOUT=30
STUDY_WEEKS=4
HOURS_PER_WEEK=10
OUTPUT_DIR=./output
LOG_LEVEL=INFO
```

## 🔧 **Usage**

### **Command Line Interface**
```bash
# Run the complete pipeline
python3 cli.py

# Or run directly
python3 main.py
```

### **Programmatic Usage**
```python
from main import InterviewPreparationPipeline

# Create and run pipeline
pipeline = InterviewPreparationPipeline()
result = pipeline.run()

if result['success']:
    print(f"Pipeline completed in {result['execution_time']:.2f} seconds")
    print(f"Files generated: {len(result['results']['files_generated'])}")
else:
    print(f"Pipeline failed: {result['error']}")
```

## 📋 **Pipeline Steps**

1. **Job Description Scraping** - Extract job content from web pages
2. **Job Analysis** - AI-powered analysis of requirements and qualifications
3. **Custom GPT Instructions** - Generate tailored interview preparation prompts
4. **Research Division** - Divide research topics among multiple agents
5. **Research Execution** - Execute research tasks using Deep Research API
6. **Results Merging** - Consolidate research results into comprehensive guides
7. **File Generation** - Save all results in organized output structure

## 🏛️ **Component Architecture**

### **Utils Component** (Base Layer)
- **Configuration Management**: Singleton pattern with environment variable loading
- **Logging System**: Centralized logging with file rotation and console output
- **Constants**: All magic numbers and strings replaced with named constants
- **Exceptions**: Custom exception hierarchy for different error types
- **Helpers**: Common utility functions for data processing and validation

### **LLM Client Component**
- **Abstract Interface**: BaseLLMClient defines contracts for all LLM services
- **OpenAI Implementation**: Full OpenAI API integration with conversation context
- **Extensible Design**: Easy to add new providers (Gemini, Claude, etc.)

### **Scraper Component**
- **Multi-Method Extraction**: Playwright, BeautifulSoup, and direct requests
- **Robust Fallbacks**: Automatic fallback when primary methods fail
- **Content Validation**: Quality checks for extracted content
- **JavaScript Support**: Handles modern, dynamic web pages

### **Other Components**
- **Custom Prompt Generation**: Tailored GPT instruction creation
- **Research Management**: Topic division and agent coordination
- **Task Execution**: Research task orchestration and monitoring
- **Conversation Handling**: State persistence and context management
- **Storage Management**: File organization and persistence

## 🔍 **Features**

### **Web Scraping**
- **Multiple Extraction Methods**: Playwright, BeautifulSoup, direct requests
- **Automatic Fallbacks**: Robust content extraction with multiple strategies
- **Content Validation**: Quality checks and length validation
- **JavaScript Support**: Handles modern, dynamic web applications

### **AI Integration**
- **OpenAI API**: Full integration with GPT-4o-mini and Deep Research
- **Conversation Context**: Efficient token usage through conversation history
- **Background Processing**: Deep Research tasks run in background mode
- **Error Handling**: Comprehensive error handling and recovery

### **Research Management**
- **Multi-Agent Architecture**: Parallel research execution across multiple agents
- **Topic Division**: Intelligent division of research topics
- **Progress Tracking**: Real-time monitoring of research progress
- **Result Consolidation**: Merging of research results into comprehensive guides

### **Output Generation**
- **Structured Results**: Organized output with clear file naming
- **Multiple Formats**: Markdown, JSON, and text outputs
- **Run Organization**: Timestamped output directories for each execution
- **State Persistence**: Resume capability for interrupted runs

## 🛠️ **Development**

### **Project Structure**
The application follows a clean, modular architecture:
- **Separation of Concerns**: Each component has a single responsibility
- **Dependency Injection**: Components receive dependencies through constructors
- **Interface-Based Design**: Clear contracts between components
- **Configuration-Driven**: Behavior controlled through environment variables

### **Adding New Components**
1. Create a new directory under `src/`
2. Implement the required interface or base class
3. Add the component to the main pipeline
4. Update configuration and constants as needed

### **Extending LLM Support**
1. Implement the `BaseLLMClient` interface
2. Add configuration options for the new provider
3. Update the main pipeline to use the new client
4. Add any provider-specific constants and helpers

## 📊 **Performance & Scalability**

### **Efficiency Features**
- **Conversation Context**: Reduces token usage through conversation history
- **Background Processing**: Research tasks run asynchronously
- **Lazy Loading**: Components initialized only when needed
- **Resource Management**: Proper cleanup and resource handling

### **Scalability Considerations**
- **Modular Design**: Easy to scale individual components
- **Async Ready**: Architecture supports asynchronous operations
- **Plugin Architecture**: New capabilities can be added without core changes
- **Configuration-Driven**: Behavior scales through configuration

## 🐛 **Troubleshooting**

### **Common Issues**
1. **Configuration Errors**: Ensure all required environment variables are set
2. **API Key Issues**: Verify OpenAI API key is valid and has sufficient credits
3. **Scraping Failures**: Check if the job URL is accessible and contains content
4. **Research Timeouts**: Adjust `MAX_RESEARCH_TIME` for complex research tasks

### **Debug Mode**
Enable detailed logging by setting `LOG_LEVEL=DEBUG` in your `.env` file.

### **Error Recovery**
The pipeline includes comprehensive error handling and can resume from most failure points.

## 📚 **API Reference**

### **Core Classes**
- `InterviewPreparationPipeline`: Main pipeline orchestration
- `Config`: Configuration management singleton
- `BaseLLMClient`: Abstract LLM client interface
- `WebScraper`: Web content extraction
- `OpenAIClient`: OpenAI API integration

### **Key Methods**
- `pipeline.run()`: Execute the complete pipeline
- `config.get_openai_config()`: Get OpenAI configuration
- `scraper.scrape_job_page(url)`: Extract job content
- `llm_client.analyze_job_description(content, url)`: Analyze job requirements

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Implement your changes following the established patterns
4. Add appropriate logging and error handling
5. Update documentation as needed
6. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 **Support**

For issues and questions:
1. Check the troubleshooting section
2. Review the error logs
3. Check configuration settings
4. Open an issue with detailed error information

---

**Job4U** - Making interview preparation smarter, faster, and more effective through AI-powered automation. 🚀 