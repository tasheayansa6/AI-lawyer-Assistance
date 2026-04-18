# AI Lawyer Assistant

A professional AI-powered legal information assistant built with Streamlit and Groq API. This application provides general legal information, document analysis, and case law summarization capabilities.

## Features

### Core Functionality
- **Legal Q&A**: Ask legal questions and get AI-powered answers with confidence levels
- **Document Analysis**: Upload and analyze legal documents (PDF, DOCX) with AI insights
- **Case Law Summarizer**: Analyze and summarize legal cases with metadata extraction
- **Multi-Jurisdiction Support**: US, UK, India, Canada, Australia, Ethiopia

### Advanced Features
- **Dark/Light Mode Toggle**: Switch between light and dark themes
- **Loading Animations**: Professional loading spinners during processing
- **Comprehensive Error Handling**: Graceful handling of API errors and timeouts
- **Chat History**: Persistent conversation history with save/load functionality
- **Document Library**: Manage multiple uploaded documents
- **Case History**: Track and export case summaries

### Safety Features
- **Disclaimer System**: Mandatory legal disclaimer on first visit
- **Content Filtering**: PII detection and inappropriate content filtering
- **Rate Limiting**: Built-in rate limiting to prevent abuse
- **Input Validation**: Comprehensive input validation and sanitization

## Installation

### Prerequisites
- Python 3.8 or higher
- Groq API key (required for AI functionality)

### Setup Instructions

1. **Clone or Download** the project files to your local directory

2. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On macOS/Linux
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**:
   Create a `.env` file in the project root:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

5. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

## Usage

### Getting Started
1. Launch the application using `streamlit run app.py`
2. Read and accept the disclaimer on your first visit
3. Select your jurisdiction from the dropdown menu
4. Start using the features through the tabbed interface

### Tab Overview

#### Q&A Tab
- Ask legal questions in natural language
- Adjust response length with the slider
- View conversation history
- Get confidence levels for AI responses

#### Documents Tab
- Upload PDF or DOCX files for analysis
- Extract key clauses and summaries
- Ask questions about uploaded documents
- Manage document library

#### Cases Tab
- Paste case text or fetch from URLs
- Generate AI-powered summaries
- Compare multiple cases
- Export case summaries

#### Settings Tab
- Toggle between dark and light modes
- Access lawyer referral links by jurisdiction
- View system information and usage statistics
- Get help and support information

## Configuration

### API Configuration
The application uses the Groq API for AI responses. You need to:
1. Sign up for a Groq account at https://groq.com
2. Generate an API key
3. Set the `GROQ_API_KEY` environment variable

### Supported Jurisdictions
- United States (US)
- United Kingdom (UK)
- India
- Canada
- Australia
- Ethiopia

## File Structure

```
AI lawyer Assistance/
|-- app.py                 # Main Streamlit application
|-- chat.py                # AI chat functionality
|-- prompts.py             # Prompt templates
|-- document_parser.py     # Document processing
|-- case_summarizer.py     # Case analysis tools
|-- legal_ai_tools.py      # Legal AI tool recommendations
|-- requirements.txt       # Python dependencies
|-- README.md             # This file
|-- .env                  # Environment variables (create this)
```

## API Limits and Usage

### Rate Limiting
- Built-in rate limiting to prevent API abuse
- Automatic retry logic for failed requests
- Graceful handling of rate limit errors

### Token Limits
- Configurable response length (100-1000 tokens)
- Automatic truncation of long queries
- Optimized prompt engineering for efficiency

## Security and Privacy

### Data Protection
- No user data is stored permanently
- Local session storage only
- Optional chat history export functionality

### Content Safety
- PII detection and filtering
- Inappropriate content rejection
- Legal disclaimer enforcement

## Troubleshooting

### Common Issues

1. **API Key Errors**:
   - Ensure your Groq API key is valid
   - Check environment variable setup
   - Verify API key permissions

2. **Document Upload Issues**:
   - Supported formats: PDF, DOCX
   - Maximum file size: 10MB
   - Ensure documents are not password-protected

3. **Performance Issues**:
   - Check internet connection
   - Verify API service status
   - Try shorter queries for faster responses

### Error Messages
- **Rate Limit Error**: Wait 1 minute before trying again
- **Connection Error**: Check your internet connection
- **Authentication Error**: Verify your API key
- **Timeout Error**: Try with shorter queries

## Legal Disclaimer

**IMPORTANT**: This AI assistant provides general legal information only and does not constitute legal advice. 

- Information may be incorrect or outdated
- Laws vary by jurisdiction and change frequently
- Always consult a qualified licensed attorney for specific legal advice
- Do not share confidential or sensitive information
- This is for educational purposes only
- No attorney-client relationship is formed

## Support

### Getting Help
- Use the Settings tab for help and support information
- Access lawyer referral links by jurisdiction
- Check system status in the application

### Contributing
This is a demonstration project. For issues or suggestions:
1. Check the troubleshooting section
2. Verify your configuration
3. Contact support through provided channels

## License

© 2024 AI Legal Assistant. All rights reserved.

## Technologies Used

- **Frontend**: Streamlit
- **Backend**: Python
- **AI API**: Groq
- **Document Processing**: PyPDF2, python-docx
- **Web Scraping**: BeautifulSoup4
- **Styling**: Custom CSS

## Version History

- **v1.0**: Initial release with core functionality
- **v1.1**: Added dark mode and enhanced error handling
- **v1.2**: Improved UI with 4-tab layout
- **v1.3**: Enhanced document and case analysis features

---

**For Educational Purposes Only** | **Powered by Groq API**
