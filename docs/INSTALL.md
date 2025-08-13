# Job4U Installation Guide

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8 or higher
- OpenAI API key
- (Optional) Google Drive API credentials

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>
cd job4u

# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY="your_api_key_here"
```

### 3. Test Installation

```bash
# Run the demo
python -m job4u.test_demo

# Run the test suite
python -m job4u.test_scraper

# Check configuration
python -m job4u.cli config
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional - Model Configuration
OPENAI_MODEL_BROWSING=gpt-4o
OPENAI_MODEL_WRITING=gpt-4o

# Optional - Google Drive Integration
GOOGLE_DRIVE_CREDENTIALS_FILE=credentials.json
GOOGLE_DRIVE_TOKEN_FILE=token.json

# Optional - Application Settings
OUTPUT_DIR=./output
LOG_LEVEL=INFO
```

### OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Create a new API key
5. Set the environment variable:
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```

## 📖 Usage Examples

### Complete Pipeline
```bash
python -m job4u.cli run -u "https://example.com/job-posting" -w 6 -h 15
```

### Interactive Mode
```bash
python -m job4u.cli interactive
```

### Individual Components
```bash
# Scrape job description
python -m job4u.cli scrape -u "https://example.com/job"

# Analyze job description
python -m job4u.cli analyze -u "https://example.com/job"

# Generate interview guide
python -m job4u.cli generate-guide -i research.json

# Create study timeline
python -m job4u.cli create-timeline -i research.json -g guide.md -w 6 -h 15
```

## 🌐 Google Drive Integration (Optional)

### 1. Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Google Drive API

### 2. Create Credentials
1. Go to APIs & Services > Credentials
2. Create OAuth 2.0 Client ID
3. Download the credentials file as `credentials.json`

### 3. Set Environment Variables
```env
GOOGLE_DRIVE_CREDENTIALS_FILE=credentials.json
GOOGLE_DRIVE_TOKEN_FILE=token.json
```

## 🔍 Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Make sure you're in the correct directory
2. **OpenAI API errors**: Check your API key and billing
3. **Import errors**: Verify all dependencies are installed
4. **Permission errors**: Check file permissions and paths

### Debug Mode

Enable verbose logging:
```bash
python -m job4u.cli --verbose run -u "https://example.com/job"
```

### Logs

Check log files in the `logs/` directory for detailed error information.

## 📊 Performance

Typical execution times:
- **Job scraping**: 5-15 seconds
- **Job analysis**: 30-60 seconds
- **Custom GPT instructions**: 20-40 seconds
- **Deep research**: 2-10 minutes
- **Study timeline**: 20-40 seconds

**Total pipeline time**: 3-12 minutes

## 🧪 Testing

### Run Tests
```bash
# Test scraper functionality
python -m job4u.test_scraper

# Test package import
python -c "from job4u import InterviewPreparationPipeline; print('Success!')"
```

### Verify Installation
```bash
# Check configuration
python -m job4u.cli config

# Run demo
python -m job4u.test_demo
```

## 📁 Project Structure

```
job4u/
├── config.py              # Configuration management
├── models.py              # Data models and validation
├── scraper.py             # Web scraping functionality
├── openai_client.py       # OpenAI API integration
├── storage.py             # Local and cloud storage
├── pipeline.py            # Main orchestration logic
├── cli.py                 # Command-line interface
├── __init__.py            # Package initialization
├── setup.py               # Installation configuration
├── requirements.txt       # Dependencies
├── README.md              # Documentation
├── test_demo.py           # Demo script
├── test_scraper.py        # Test suite
└── logs/                  # Log files
```

## 🎯 Next Steps

1. **Set your OpenAI API key**
2. **Test the installation** with the demo scripts
3. **Try the interactive mode** with a real job URL
4. **Explore individual components** for specific use cases
5. **Customize the configuration** for your needs

## 📞 Support

- Check the README.md for comprehensive documentation
- Review the troubleshooting section
- Open an issue on GitHub for bugs or feature requests

---

**Happy interviewing! 🎉** 