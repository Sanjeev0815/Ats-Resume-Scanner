import re
import string
from typing import List, Dict, Set, Tuple
import streamlit as st
from collections import Counter
import spacy

class TextUtils:
    """Utility functions for text processing and analysis"""
    
    def __init__(self):
        # Common stop words for filtering
        self.stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 
            'after', 'above', 'below', 'between', 'among', 'within', 'without',
            'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'must', 'can', 'shall', 'this', 'that', 'these', 'those'
        }
        
        # Technical skill categories for better matching
        self.skill_categories = {
            'programming_languages': [
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 
                'ruby', 'go', 'rust', 'swift', 'kotlin', 'scala', 'r', 'matlab'
            ],
            'web_technologies': [
                'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express',
                'django', 'flask', 'spring', 'laravel', 'asp.net', 'jquery'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'sqlite', 'oracle', 'sql server',
                'redis', 'elasticsearch', 'cassandra', 'dynamodb'
            ],
            'cloud_platforms': [
                'aws', 'azure', 'google cloud', 'gcp', 'heroku', 'docker', 
                'kubernetes', 'terraform', 'ansible', 'jenkins'
            ],
            'data_science': [
                'machine learning', 'deep learning', 'tensorflow', 'pytorch',
                'pandas', 'numpy', 'scikit-learn', 'data analysis', 'statistics',
                'tableau', 'power bi', 'spark', 'hadoop'
            ],
            'business_skills': [
                'project management', 'agile', 'scrum', 'leadership', 'communication',
                'analysis', 'strategy', 'marketing', 'sales', 'negotiation'
            ]
        }
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text for analysis"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep alphanumeric and basic punctuation
        text = re.sub(r'[^\w\s\.\,\-\(\)]', ' ', text)
        
        return text.strip()
    
    def extract_keywords(self, text: str, min_length: int = 3, max_length: int = 20) -> List[str]:
        """Extract meaningful keywords from text"""
        if not text:
            return []
        
        # Clean text
        cleaned_text = self.clean_text(text)
        
        # Split into words and phrases
        words = cleaned_text.split()
        
        # Filter words
        keywords = []
        for word in words:
            word = word.strip('.,()[]{}')
            if (min_length <= len(word) <= max_length and 
                word not in self.stop_words and 
                not word.isdigit()):
                keywords.append(word)
        
        # Also extract 2-word phrases that might be important
        phrases = []
        for i in range(len(words) - 1):
            phrase = f"{words[i]} {words[i + 1]}"
            phrase = phrase.strip('.,()[]{}')
            if (len(phrase.split()) == 2 and 
                not any(word in self.stop_words for word in phrase.split()) and
                len(phrase) <= max_length):
                phrases.append(phrase)
        
        # Combine and return unique keywords
        all_keywords = list(set(keywords + phrases))
        return all_keywords
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using word overlap"""
        if not text1 or not text2:
            return 0.0
        
        keywords1 = set(self.extract_keywords(text1))
        keywords2 = set(self.extract_keywords(text2))
        
        if not keywords1 or not keywords2:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(keywords1.intersection(keywords2))
        union = len(keywords1.union(keywords2))
        
        return intersection / union if union > 0 else 0.0
    
    def extract_years_of_experience(self, text: str) -> int:
        """Extract years of experience from text"""
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of)?\s*experience',
            r'(\d+)\+?\s*yrs?\s*(?:of)?\s*experience',
            r'over\s+(\d+)\s+years?',
            r'more than\s+(\d+)\s+years?',
            r'(\d+)\+?\s*years?\s*in',
            r'(\d+)\+?\s*years?\s*working',
        ]
        
        max_years = 0
        text_lower = text.lower()
        
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                try:
                    years = int(match)
                    max_years = max(max_years, years)
                except ValueError:
                    continue
        
        return max_years
    
    def extract_education_level(self, text: str) -> str:
        """Extract highest education level from text"""
        text_lower = text.lower()
        
        education_levels = [
            ('phd', ['phd', 'ph.d', 'doctorate', 'doctoral']),
            ('masters', ['master', 'masters', 'mba', 'ms', 'm.s', 'ma', 'm.a']),
            ('bachelors', ['bachelor', 'bachelors', 'bs', 'b.s', 'ba', 'b.a']),
            ('associates', ['associate', 'associates', 'aa', 'as']),
            ('diploma', ['diploma', 'high school', 'secondary']),
            ('certificate', ['certificate', 'certification'])
        ]
        
        for level, keywords in education_levels:
            if any(keyword in text_lower for keyword in keywords):
                return level
        
        return 'unknown'
    
    def categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """Categorize skills into different categories"""
        categorized = {category: [] for category in self.skill_categories.keys()}
        uncategorized = []
        
        for skill in skills:
            skill_lower = skill.lower()
            categorized_flag = False
            
            for category, category_skills in self.skill_categories.items():
                if any(cat_skill in skill_lower for cat_skill in category_skills):
                    categorized[category].append(skill)
                    categorized_flag = True
                    break
            
            if not categorized_flag:
                uncategorized.append(skill)
        
        if uncategorized:
            categorized['other'] = uncategorized
        
        # Remove empty categories
        return {k: v for k, v in categorized.items() if v}
    
    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information from text"""
        contact_info = {}
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]
        
        # Phone patterns
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
                contact_info['phone'] = phones[0]
                break
        
        # LinkedIn profile
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin = re.findall(linkedin_pattern, text.lower())
        if linkedin:
            contact_info['linkedin'] = linkedin[0]
        
        # GitHub profile
        github_pattern = r'github\.com/[\w-]+'
        github = re.findall(github_pattern, text.lower())
        if github:
            contact_info['github'] = github[0]
        
        return contact_info
    
    def calculate_keyword_density(self, text: str, keywords: List[str]) -> Dict[str, float]:
        """Calculate keyword density in text"""
        if not text or not keywords:
            return {}
        
        text_lower = text.lower()
        word_count = len(text_lower.split())
        
        density = {}
        for keyword in keywords:
            keyword_lower = keyword.lower()
            count = text_lower.count(keyword_lower)
            density[keyword] = (count / word_count) * 100 if word_count > 0 else 0
        
        return density
    
    def suggest_keywords(self, resume_text: str, job_description: str, top_n: int = 10) -> List[str]:
        """Suggest keywords to add to resume based on job description"""
        # Extract keywords from job description
        jd_keywords = self.extract_keywords(job_description)
        resume_keywords = set(self.extract_keywords(resume_text))
        
        # Find missing keywords
        missing_keywords = []
        for keyword in jd_keywords:
            if keyword not in resume_keywords:
                missing_keywords.append(keyword)
        
        # Count frequency in job description to prioritize
        jd_word_freq = Counter(jd_keywords)
        
        # Sort missing keywords by frequency in job description
        missing_keywords.sort(key=lambda x: jd_word_freq.get(x, 0), reverse=True)
        
        return missing_keywords[:top_n]
    
    def validate_resume_format(self, text: str) -> Dict[str, bool]:
        """Validate resume format for ATS compatibility"""
        validation_results = {}
        
        # Check for standard sections
        sections = ['summary', 'experience', 'education', 'skills']
        for section in sections:
            validation_results[f'has_{section}_section'] = section in text.lower()
        
        # Check for contact information
        contact_info = self.extract_contact_info(text)
        validation_results['has_email'] = 'email' in contact_info
        validation_results['has_phone'] = 'phone' in contact_info
        
        # Check for bullet points
        bullet_patterns = [r'•', r'-\s', r'\*\s', r'\d+\.']
        validation_results['has_bullet_points'] = any(re.search(pattern, text) for pattern in bullet_patterns)
        
        # Check text length
        word_count = len(text.split())
        validation_results['appropriate_length'] = 300 <= word_count <= 1000
        
        # Check for problematic formatting
        problematic_chars = ['|', '─', '═', '┌', '┐', '└', '┘', '▪', '►']
        validation_results['clean_formatting'] = not any(char in text for char in problematic_chars)
        
        return validation_results
    
    def extract_achievements(self, text: str) -> List[str]:
        """Extract quantified achievements from text"""
        achievements = []
        
        # Patterns for achievements with numbers
        achievement_patterns = [
            r'(?:increased|improved|reduced|decreased|grew|generated|saved|managed)\s+[^.]*?\d+[^.]*?(?:\.|$)',
            r'(?:led|managed|supervised)\s+[^.]*?\d+[^.]*?(?:\.|$)',
            r'\d+%\s+[^.]*?(?:increase|improvement|growth|reduction)',
            r'(?:over|more than|up to)\s+\$?\d+[^.]*?(?:\.|$)',
        ]
        
        for pattern in achievement_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                achievement = match.strip()
                if len(achievement) > 20:  # Filter out very short matches
                    achievements.append(achievement)
        
        return achievements[:10]  # Return top 10 achievements

class ValidationUtils:
    """Utilities for validating and scoring resume components"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        if not phone:
            return False
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        # Check if it's a valid US phone number (10-11 digits)
        return len(digits) in [10, 11]
    
    @staticmethod
    def score_section_completeness(sections: Dict[str, bool]) -> int:
        """Score resume section completeness"""
        required_sections = ['has_summary_section', 'has_experience_section', 'has_education_section', 'has_skills_section']
        completed_sections = sum(1 for section in required_sections if sections.get(section, False))
        return int((completed_sections / len(required_sections)) * 100)
    
    @staticmethod
    def calculate_readability_score(text: str) -> int:
        """Calculate basic readability score"""
        if not text:
            return 0
        
        # Basic metrics
        sentences = text.count('.') + text.count('!') + text.count('?')
        words = len(text.split())
        
        if sentences == 0 or words == 0:
            return 50
        
        # Average words per sentence (ideal: 15-20)
        avg_words_per_sentence = words / sentences
        
        # Calculate score based on readability
        if 10 <= avg_words_per_sentence <= 25:
            readability_score = 100
        elif avg_words_per_sentence < 10:
            readability_score = 70
        else:
            readability_score = max(50, 100 - (avg_words_per_sentence - 25) * 2)
        
        return int(readability_score)

class ScoreCalculator:
    """Centralized scoring calculations"""
    
    @staticmethod
    def calculate_skill_match_score(resume_skills: List[str], required_skills: List[str], preferred_skills: List[str] = None) -> Dict:
        """Calculate comprehensive skill matching score"""
        if not resume_skills or not required_skills:
            return {'score': 0, 'matched': [], 'missing': [], 'extra': []}
        
        resume_skills_lower = set(skill.lower() for skill in resume_skills)
        required_skills_lower = set(skill.lower() for skill in required_skills)
        preferred_skills_lower = set(skill.lower() for skill in (preferred_skills or []))
        
        all_jd_skills = required_skills_lower.union(preferred_skills_lower)
        
        matched_skills = resume_skills_lower.intersection(all_jd_skills)
        missing_skills = all_jd_skills - resume_skills_lower
        extra_skills = resume_skills_lower - all_jd_skills
        
        # Calculate score with weighting for required vs preferred
        required_matches = len(resume_skills_lower.intersection(required_skills_lower))
        preferred_matches = len(resume_skills_lower.intersection(preferred_skills_lower))
        
        required_weight = 0.8
        preferred_weight = 0.2
        
        if required_skills_lower:
            required_score = (required_matches / len(required_skills_lower)) * 100
        else:
            required_score = 100
        
        if preferred_skills_lower:
            preferred_score = (preferred_matches / len(preferred_skills_lower)) * 100
        else:
            preferred_score = 100
        
        overall_score = (required_score * required_weight) + (preferred_score * preferred_weight)
        
        return {
            'score': int(overall_score),
            'matched': list(matched_skills),
            'missing': list(missing_skills),
            'extra': list(extra_skills),
            'required_matches': required_matches,
            'preferred_matches': preferred_matches
        }
    
    @staticmethod
    def calculate_experience_match_score(resume_years: int, required_years_text: str) -> int:
        """Calculate experience matching score"""
        # Extract required years from text
        required_years_match = re.search(r'(\d+)', required_years_text)
        required_years = int(required_years_match.group(1)) if required_years_match else 0
        
        if required_years == 0:
            return 100  # No specific requirement
        
        if resume_years >= required_years:
            # Bonus for exceeding requirements, but cap at 100
            return min(100, 100 + (resume_years - required_years) * 2)
        else:
            # Linear penalty for not meeting requirements
            return max(0, int((resume_years / required_years) * 80))
