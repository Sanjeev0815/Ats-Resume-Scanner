import streamlit as st
import PyPDF2
import docx
import re
import spacy
from io import BytesIO
import pandas as pd
from typing import Dict, List, Optional, Union

class ResumeParser:
    def __init__(self):
        # Load spaCy model for NLP processing
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            st.error("spaCy English model not found. Please install it with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Common skill patterns and keywords
        self.skill_patterns = {
            'programming': [
                'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'c',
                'html', 'css', 'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'react.js',
                'typescript', 'kotlin', 'swift', 'scala', 'perl', 'matlab', 'r programming'
            ],
            'data_science': [
                'machine learning', 'data science', 'artificial intelligence', 'deep learning', 'ai',
                'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn', 'sql', 'r', 'keras',
                'opencv', 'nlp', 'natural language processing', 'computer vision', 'neural networks',
                'cnn', 'rnn', 'lstm', 'data analysis', 'statistical analysis', 'data visualization',
                'tableau', 'power bi', 'matplotlib', 'seaborn', 'plotly', 'data mining',
                'predictive modeling', 'regression', 'classification', 'clustering', 'etl',
                'big data', 'hadoop', 'spark', 'data engineering', 'data warehousing'
            ],
            'cloud': [
                'aws', 'azure', 'google cloud', 'gcp', 'docker', 'kubernetes', 'terraform',
                'ansible', 'jenkins', 'git', 'ci/cd', 'devops', 'cloud computing'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'oracle', 'sql server', 'redis', 'cassandra',
                'dynamodb', 'firebase', 'sqlite', 'nosql', 'database'
            ],
            'web': [
                'html', 'css', 'javascript', 'react', 'angular', 'vue', 'node.js', 'express',
                'django', 'flask', 'spring', 'rest api', 'graphql', 'web development',
                'frontend', 'backend', 'full stack', 'responsive design', 'bootstrap', 'tailwind'
            ],
            'tools': [
                'git', 'github', 'gitlab', 'jira', 'confluence', 'excel', 'powerpoint', 'word',
                'jupyter', 'vs code', 'pycharm', 'intellij', 'eclipse', 'visual studio'
            ],
            'business': [
                'project management', 'agile', 'scrum', 'leadership', 'communication',
                'analysis', 'strategy', 'marketing', 'sales', 'problem solving', 'teamwork',
                'analytical thinking', 'data-driven', 'stakeholder management'
            ]
        }
    
    def parse_resume(self, file) -> Optional[Dict]:
        """Parse resume file and extract key information"""
        if file is None:
            return None
        
        try:
            # Extract text based on file type
            if file.type == "application/pdf":
                text = self._extract_pdf_text(file)
            elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                text = self._extract_docx_text(file)
            else:  # txt or other text files
                text = str(file.read(), "utf-8")
            
            if not text:
                st.error("Could not extract text from the uploaded file.")
                return None
            
            # Parse the extracted text
            return self._parse_text(text)
            
        except Exception as e:
            st.error(f"Error parsing resume: {str(e)}")
            return None
    
    def _extract_pdf_text(self, file) -> str:
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(file.read()))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            st.error(f"Error reading PDF: {str(e)}")
            return ""
    
    def _extract_docx_text(self, file) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(BytesIO(file.read()))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            st.error(f"Error reading DOCX: {str(e)}")
            return ""
    
    def parse_text(self, text: str) -> Dict:
        """Public method to parse text directly (useful for edited resumes)"""
        return self._parse_text(text)
    
    def _parse_text(self, text: str) -> Dict:
        """Parse extracted text and return structured data"""
        resume_data = {
            'raw_text': text,
            'name': self._extract_name(text),
            'email': self._extract_email(text),
            'phone': self._extract_phone(text),
            'skills': self._extract_skills(text),
            'experience': self._extract_experience(text),
            'education': self._extract_education(text),
            'experience_years': self._estimate_experience_years(text),
            'certifications': self._extract_certifications(text),
            'languages': self._extract_languages(text)
        }
        
        return resume_data
    
    def _extract_name(self, text: str) -> Optional[str]:
        """Extract candidate name from resume text"""
        lines = text.split('\n')
        # Usually name is in the first few lines
        for line in lines[:5]:
            line = line.strip()
            if len(line) > 0 and len(line.split()) <= 4:
                # Check if line contains typical name patterns
                if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+', line):
                    return line
        return None
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address from resume text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from resume text"""
        phone_patterns = [
            r'\b\d{3}-\d{3}-\d{4}\b',
            r'\b\(\d{3}\)\s*\d{3}-\d{4}\b',
            r'\b\d{3}\.\d{3}\.\d{4}\b',
            r'\b\+\d{1,3}\s*\d{3}\s*\d{3}\s*\d{4}\b',
            r'\b\d{10}\b'
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                return phones[0]
        return None
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text"""
        text_lower = text.lower()
        found_skills = []
        
        # Check for skills from predefined patterns
        for category, skills in self.skill_patterns.items():
            for skill in skills:
                if skill.lower() in text_lower:
                    found_skills.append(skill)
        
        # Look for skills section
        skills_section = self._find_section(text, ['skills', 'technical skills', 'core competencies'])
        if skills_section:
            # Extract skills from skills section
            section_skills = self._extract_skills_from_section(skills_section)
            found_skills.extend(section_skills)
        
        # Remove duplicates and return
        return list(set(found_skills))
    
    def _extract_skills_from_section(self, section_text: str) -> List[str]:
        """Extract skills from a specific skills section"""
        skills = []
        # Split by common delimiters including parentheses
        potential_skills = re.split(r'[,;|\n•·\-()&]', section_text)
        
        for skill in potential_skills:
            skill = skill.strip()
            # More flexible skill extraction - allow numbers, longer names
            if 2 <= len(skill) <= 50:
                # Remove extra whitespace
                skill = ' '.join(skill.split())
                # Skip if it's just a number or common words
                if skill and not skill.isdigit() and skill.lower() not in ['and', 'or', 'the', 'a', 'an']:
                    skills.append(skill)
        
        return skills
    
    def _extract_experience(self, text: str) -> List[Dict]:
        """Extract work experience from resume text"""
        experience_section = self._find_section(text, [
            'experience', 'work experience', 'professional experience', 'employment'
        ])
        
        if not experience_section:
            return []
        
        experiences = []
        # Look for date patterns and job titles
        date_pattern = r'\b(?:19|20)\d{2}\b'
        dates = re.findall(date_pattern, experience_section)
        
        # Simple experience extraction (can be enhanced)
        lines = experience_section.split('\n')
        current_exp = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for job titles (usually capitalized)
            if re.search(r'^[A-Z][a-z\s]+(?:Manager|Engineer|Analyst|Developer|Director|Specialist|Coordinator)', line):
                if current_exp:
                    experiences.append(current_exp)
                current_exp = {'title': line, 'description': ''}
            elif current_exp:
                current_exp['description'] += line + ' '
        
        if current_exp:
            experiences.append(current_exp)
        
        return experiences
    
    def _extract_education(self, text: str) -> List[Dict]:
        """Extract education information from resume text"""
        education_section = self._find_section(text, ['education', 'academic background', 'qualifications'])
        
        if not education_section:
            return []
        
        education = []
        degree_patterns = [
            r'(?:Bachelor|Master|PhD|MBA|BS|MS|BA|MA)\s+(?:of|in)?\s+[A-Za-z\s]+',
            r'(?:B\.S\.|M\.S\.|B\.A\.|M\.A\.|Ph\.D\.)\s+(?:in)?\s+[A-Za-z\s]+'
        ]
        
        for pattern in degree_patterns:
            degrees = re.findall(pattern, education_section, re.IGNORECASE)
            for degree in degrees:
                education.append({'degree': degree.strip()})
        
        return education
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications from resume text"""
        cert_section = self._find_section(text, ['certifications', 'certificates', 'licenses'])
        
        if not cert_section:
            return []
        
        # Common certification patterns
        cert_patterns = [
            r'(?:AWS|Azure|Google Cloud|GCP)\s+[A-Za-z\s]+',
            r'(?:PMP|CISSP|CISA|CompTIA)\s*[A-Za-z\s]*',
            r'[A-Z]{2,}\s+Certified\s+[A-Za-z\s]+'
        ]
        
        certifications = []
        for pattern in cert_patterns:
            certs = re.findall(pattern, cert_section, re.IGNORECASE)
            certifications.extend(certs)
        
        return certifications
    
    def _extract_languages(self, text: str) -> List[str]:
        """Extract languages from resume text"""
        lang_section = self._find_section(text, ['languages', 'language skills'])
        
        common_languages = [
            'English', 'Spanish', 'French', 'German', 'Italian', 'Portuguese',
            'Chinese', 'Japanese', 'Korean', 'Arabic', 'Russian', 'Hindi'
        ]
        
        found_languages = []
        search_text = lang_section if lang_section else text
        
        for lang in common_languages:
            if lang.lower() in search_text.lower():
                found_languages.append(lang)
        
        return found_languages
    
    def _estimate_experience_years(self, text: str) -> int:
        """Estimate total years of experience"""
        # Look for experience statements
        exp_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of)?\s*experience',
            r'(\d+)\+?\s*yrs?\s*(?:of)?\s*experience',
            r'over\s+(\d+)\s+years?',
            r'more than\s+(\d+)\s+years?'
        ]
        
        max_years = 0
        for pattern in exp_patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                try:
                    years = int(match)
                    max_years = max(max_years, years)
                except ValueError:
                    continue
        
        # If no explicit mention, try to estimate from dates
        if max_years == 0:
            date_pattern = r'\b(?:19|20)(\d{2})\b'
            dates = [int(match) for match in re.findall(date_pattern, text)]
            if len(dates) >= 2:
                max_years = max(dates) - min(dates)
        
        return max_years
    
    def _find_section(self, text: str, section_names: List[str]) -> Optional[str]:
        """Find a specific section in the resume text"""
        lines = text.split('\n')
        section_start = -1
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            if any(name.lower() in line_lower for name in section_names):
                section_start = i
                break
        
        if section_start == -1:
            return None
        
        # Find section end (next major section or end of text)
        section_end = len(lines)
        for i in range(section_start + 1, len(lines)):
            line = lines[i].strip()
            if line and line[0].isupper() and len(line.split()) <= 3:
                # Potential new section header
                if any(keyword in line.lower() for keyword in [
                    'education', 'experience', 'skills', 'projects', 'achievements', 'summary'
                ]):
                    section_end = i
                    break
        
        return '\n'.join(lines[section_start:section_end])
    
    def parse_job_description(self, jd_text: str) -> Dict:
        """Parse job description and extract requirements"""
        return {
            'raw_text': jd_text,
            'required_skills': self._extract_jd_skills(jd_text, required=True),
            'preferred_skills': self._extract_jd_skills(jd_text, required=False),
            'experience_required': self._extract_jd_experience(jd_text),
            'education_required': self._extract_jd_education(jd_text),
            'responsibilities': self._extract_responsibilities(jd_text),
            'qualifications': self._extract_qualifications(jd_text)
        }
    
    def _extract_jd_skills(self, text: str, required: bool = True) -> List[str]:
        """Extract required or preferred skills from job description"""
        text_lower = text.lower()
        skills = []
        
        # Look for skills in all categories
        for category, skill_list in self.skill_patterns.items():
            for skill in skill_list:
                if skill.lower() in text_lower:
                    skills.append(skill)
        
        # Look for skills sections
        if required:
            sections = self._find_jd_sections(text, [
                'required', 'must have', 'essential', 'mandatory'
            ])
        else:
            sections = self._find_jd_sections(text, [
                'preferred', 'nice to have', 'desired', 'plus'
            ])
        
        for section in sections:
            section_skills = self._extract_skills_from_section(section)
            skills.extend(section_skills)
        
        return list(set(skills))
    
    def _extract_jd_experience(self, text: str) -> str:
        """Extract experience requirements from job description"""
        exp_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of)?\s*experience',
            r'(\d+)\+?\s*yrs?\s*(?:of)?\s*experience',
            r'minimum\s+(\d+)\s+years?',
            r'at least\s+(\d+)\s+years?'
        ]
        
        for pattern in exp_patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                return f"{matches[0]} years"
        
        return "Not specified"
    
    def _extract_jd_education(self, text: str) -> str:
        """Extract education requirements from job description"""
        degree_patterns = [
            r'(?:Bachelor|Master|PhD|MBA|BS|MS|BA|MA)(?:\'s)?\s+(?:degree|in)?',
            r'(?:B\.S\.|M\.S\.|B\.A\.|M\.A\.|Ph\.D\.)',
            r'(?:undergraduate|graduate)\s+degree'
        ]
        
        for pattern in degree_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches[0]
        
        return "Not specified"
    
    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract job responsibilities from job description"""
        resp_section = self._find_section(text, [
            'responsibilities', 'duties', 'role', 'what you will do'
        ])
        
        if not resp_section:
            return []
        
        # Split by bullet points or new lines
        responsibilities = []
        lines = resp_section.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                responsibilities.append(line[1:].strip())
            elif line and len(line) > 20:
                responsibilities.append(line)
        
        return responsibilities[:10]  # Limit to top 10
    
    def _extract_qualifications(self, text: str) -> List[str]:
        """Extract qualifications from job description"""
        qual_section = self._find_section(text, [
            'qualifications', 'requirements', 'what we need', 'must have'
        ])
        
        if not qual_section:
            return []
        
        qualifications = []
        lines = qual_section.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                qualifications.append(line[1:].strip())
            elif line and len(line) > 20:
                qualifications.append(line)
        
        return qualifications[:10]  # Limit to top 10
    
    def _find_jd_sections(self, text: str, keywords: List[str]) -> List[str]:
        """Find sections in job description containing specific keywords"""
        sections = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in keywords):
                # Extract the section (next 5-10 lines or until next major section)
                section_lines = []
                for j in range(i, min(i + 10, len(lines))):
                    section_lines.append(lines[j])
                sections.append('\n'.join(section_lines))
        
        return sections
    
    def extract_text_from_file(self, file) -> str:
        """Extract text from uploaded file (for job descriptions)"""
        if file.type == "application/pdf":
            return self._extract_pdf_text(file)
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return self._extract_docx_text(file)
        else:  # txt file
            return str(file.read(), "utf-8")
