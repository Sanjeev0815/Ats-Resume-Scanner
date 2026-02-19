# ResumeScan AI - Smart ATS Resume Scanner

## Overview

ResumeScan AI is a Streamlit-based web application that analyzes resumes against job descriptions to provide ATS (Applicant Tracking System) compatibility scores and actionable recommendations. The application helps job seekers optimize their resumes by identifying skill gaps, evaluating formatting, and providing AI-powered feedback through a conversational chatbot interface.

The system processes resumes in multiple formats (PDF, DOCX, TXT), extracts structured information using NLP techniques, and compares them against job requirements to generate comprehensive analysis reports with visualizations.

## Recent Changes (October 2025)

### Database Removed
- Removed SQLite database dependency entirely
- All data now stored in Streamlit session state
- Simplified architecture and improved privacy (no data persistence)

### New Features Added
1. **Resume Editor Page**: Edit resume text inline and re-analyze instantly
2. **Paste Resume Text Option**: Users can now paste resume text instead of only uploading files
3. **Industry-Specific Recommendations**: Automatic detection of job industry with tailored keyword suggestions for 8 industries
4. **Enhanced Dashboard**: Shows industry-specific missing keywords alongside general recommendations

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Application Structure

**Frontend Framework**: Streamlit with multi-page navigation
- Main entry point: `app.py` orchestrates all components
- Page-based navigation: Home, Upload & Analyze, Resume Editor, ATS Dashboard, AI Chatbot, Comparison, Reports
- Session state management for persisting resume data, job descriptions, analysis results, and chat history
- Responsive layout with sidebar navigation and wide page configuration
- No database - all data stored in session state for simplicity

**Component Architecture**: Modular, single-responsibility classes
- Each major feature is isolated into its own Python module
- Components are initialized once using Streamlit's `@st.cache_resource` for performance
- Dependency injection pattern through the main app initialization

### Core Components

**Resume Parser** (`resume_parser.py`)
- Handles multi-format document parsing (PDF via PyPDF2, DOCX via python-docx)
- Supports direct text input via `parse_text()` method for pasted resumes
- Uses spaCy NLP model (`en_core_web_sm`) for entity recognition and text analysis
- Extracts structured data: contact information, education, experience, skills, certifications
- Categorizes skills into predefined groups: programming languages, data science, cloud platforms, business skills
- Returns standardized dictionary structure for downstream processing

**ATS Analyzer** (`ats_analyzer.py`)
- Core scoring engine that evaluates resume quality against job descriptions
- Multi-dimensional analysis:
  - Keyword matching and density scoring
  - Skill alignment percentage calculation
  - Experience relevance scoring
  - Education alignment evaluation
  - Formatting compliance checking
- Uses spaCy for advanced text similarity and entity extraction
- Implements rule-based scoring with weighted components
- Identifies ATS-friendly vs ATS-unfriendly formatting patterns
- Industry detection and role-based keyword recommendations for 8 industries:
  - Software Engineering, Data Science, Marketing, Product Management
  - Sales, Design, Finance, HR
- Provides missing industry-specific keywords tailored to the job role

**AI Chatbot** (`ai_chatbot.py`)
- Rule-based conversational interface (no external API dependencies)
- Knowledge base organized by topics: ATS, skills, formatting, keywords, experience, education
- Context-aware responses using current resume analysis results
- Provides targeted advice based on user questions and resume weaknesses
- Maintains conversation flow through Streamlit session state

**Report Generator** (`report_generator.py`)
- PDF report generation using ReportLab library
- Creates comprehensive analysis documents with:
  - ATS score visualization
  - Skill gap analysis tables
  - Detailed recommendations
  - Color-coded sections (primary, success, warning, danger themes)
- Custom styling with professional formatting
- Supports letter and A4 page sizes

**Text Utilities** (`utils.py`)
- Reusable text processing functions
- Stop word filtering for cleaner analysis
- Skill categorization and matching logic
- Technical keyword extraction and classification
- Supports multiple skill domains: programming, web, databases, cloud, data science, business

### Data Management

**Session State Management**:
- All data persisted in Streamlit session state (no database required)
- Resume data, job descriptions, and analysis results stored temporarily during session
- Chat history maintained for conversational context
- Edited resume text tracked for re-analysis

**Data Flow**:
1. User uploads resume file or pastes text, and provides job description
2. Parser extracts and structures information
3. Data stored in session state
4. Analyzer processes data and generates results
5. Results displayed and available for reports
6. Resume Editor allows inline editing and re-analysis

### Visualization & Analytics

**Plotly Integration**:
- Interactive dashboards with graph_objects and express modules
- Subplots for multi-metric visualization
- Real-time score updates and comparisons
- Exportable charts and data tables

**Analytics Features**:
- ATS score trending
- Skill match percentages
- Experience relevance metrics
- Comparative analysis across multiple resumes
- Historical performance tracking

### NLP Processing

**spaCy Integration**:
- Entity recognition for extracting names, organizations, dates
- Text similarity scoring for job description matching
- Token-based analysis for keyword extraction
- Named entity recognition for structured data extraction
- Graceful degradation with error handling if model not installed

## External Dependencies

### Python Libraries

**Core Framework**:
- `streamlit`: Web application framework and UI components
- `pandas`: Data manipulation and analysis
- `plotly`: Interactive visualizations (graph_objects, express, subplots)

**Document Processing**:
- `PyPDF2`: PDF text extraction
- `python-docx`: DOCX file parsing
- `reportlab`: PDF report generation

**NLP & Text Analysis**:
- `spacy`: Natural language processing (requires `en_core_web_sm` model)
- Standard library: `re` for regex pattern matching, `collections.Counter` for frequency analysis

**Data Handling**:
- Session state for temporary data storage
- `json`: Data serialization (Python standard library)

**Utilities**:
- `io`: In-memory file handling
- `base64`: File encoding for downloads
- `datetime`: Timestamp management

### Required Setup

**spaCy Model Installation**:
```bash
python -m spacy download en_core_web_sm
```

**No Database Setup Required**:
- All data stored in session state
- No persistence between sessions (by design for privacy)

### No External APIs

The application is designed to run completely offline with no external API dependencies. The AI chatbot uses a rule-based knowledge system rather than cloud-based LLMs, ensuring privacy and zero API costs.
