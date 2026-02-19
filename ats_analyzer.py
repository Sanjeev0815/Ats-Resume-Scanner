import re
import math
from typing import Dict, List, Tuple
import streamlit as st
from collections import Counter
import spacy

class ATSAnalyzer:
    def __init__(self):
        # Load spaCy model for advanced text analysis
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            st.error("spaCy English model not found. Please install it with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # ATS-friendly formatting rules
        self.formatting_rules = {
            'section_headers': ['summary', 'experience', 'education', 'skills', 'projects'],
            'bad_formatting': ['tables', 'columns', 'graphics', 'text boxes'],
            'good_practices': ['bullet points', 'consistent spacing', 'standard fonts']
        }
        
        # Common ATS keywords by category
        self.ats_keywords = {
            'action_verbs': [
                'achieved', 'managed', 'led', 'developed', 'created', 'implemented',
                'improved', 'increased', 'decreased', 'optimized', 'streamlined',
                'coordinated', 'collaborated', 'delivered', 'executed', 'analyzed'
            ],
            'technical_skills': [
                'python', 'java', 'sql', 'excel', 'powerpoint', 'word', 'outlook',
                'salesforce', 'crm', 'erp', 'project management', 'data analysis'
            ],
            'soft_skills': [
                'leadership', 'communication', 'teamwork', 'problem solving',
                'analytical', 'creative', 'detail oriented', 'organized'
            ]
        }
        
        # Industry-specific keyword recommendations
        self.industry_keywords = {
            'software_engineering': {
                'keywords': ['agile', 'scrum', 'ci/cd', 'microservices', 'api', 'rest', 'version control', 
                            'git', 'testing', 'debugging', 'code review', 'architecture', 'scalability'],
                'roles': ['software engineer', 'developer', 'programmer', 'backend', 'frontend', 'full stack']
            },
            'data_science': {
                'keywords': ['machine learning', 'statistical analysis', 'data visualization', 'predictive modeling',
                            'python', 'r', 'tensorflow', 'pytorch', 'sql', 'big data', 'etl', 'data pipeline'],
                'roles': ['data scientist', 'data analyst', 'ml engineer', 'ai engineer', 'analytics']
            },
            'marketing': {
                'keywords': ['seo', 'sem', 'google analytics', 'social media', 'content marketing', 'email campaigns',
                            'roi', 'conversion rate', 'brand awareness', 'digital marketing', 'marketing automation'],
                'roles': ['marketing', 'digital marketing', 'content', 'social media', 'brand', 'growth']
            },
            'product_management': {
                'keywords': ['product roadmap', 'user stories', 'stakeholder management', 'kpis', 'product strategy',
                            'user research', 'a/b testing', 'product launch', 'cross-functional', 'prioritization'],
                'roles': ['product manager', 'product owner', 'product lead', 'pm']
            },
            'sales': {
                'keywords': ['crm', 'sales pipeline', 'quota attainment', 'lead generation', 'client relationship',
                            'negotiation', 'closing', 'account management', 'revenue growth', 'prospecting'],
                'roles': ['sales', 'account executive', 'business development', 'sales rep', 'account manager']
            },
            'design': {
                'keywords': ['ui/ux', 'figma', 'sketch', 'adobe creative suite', 'wireframing', 'prototyping',
                            'user research', 'design system', 'responsive design', 'accessibility', 'visual design'],
                'roles': ['designer', 'ui designer', 'ux designer', 'product designer', 'graphic designer']
            },
            'finance': {
                'keywords': ['financial modeling', 'financial analysis', 'budgeting', 'forecasting', 'excel',
                            'variance analysis', 'financial reporting', 'gaap', 'accounting', 'p&l'],
                'roles': ['finance', 'financial analyst', 'accountant', 'controller', 'cfo']
            },
            'hr': {
                'keywords': ['recruitment', 'talent acquisition', 'onboarding', 'employee relations', 'hris',
                            'performance management', 'compensation', 'benefits', 'talent development', 'hr policies'],
                'roles': ['hr', 'human resources', 'recruiter', 'talent', 'people']
            }
        }
    
    def analyze_resume(self, resume_data: Dict, job_description: Dict) -> Dict:
        """Main method to analyze resume against job description"""
        if not resume_data or not job_description:
            return {}
        
        analysis_results = {
            'ats_score': 0,
            'skill_match_percentage': 0,
            'experience_relevance_score': 0,
            'education_alignment_score': 0,
            'formatting_score': 0,
            'keyword_analysis': {},
            'matched_skills': [],
            'missing_skills': [],
            'extra_skills': [],
            'formatting_issues': [],
            'recommendations': []
        }
        
        try:
            # Perform all analyses
            analysis_results.update(self._analyze_skills(resume_data, job_description))
            analysis_results.update(self._analyze_experience(resume_data, job_description))
            analysis_results.update(self._analyze_education(resume_data, job_description))
            analysis_results.update(self._analyze_formatting(resume_data))
            analysis_results.update(self._analyze_keywords(resume_data, job_description))
            
            # Calculate overall ATS score
            analysis_results['ats_score'] = self._calculate_ats_score(analysis_results)
            
            # Detect industry and add industry-specific recommendations
            detected_industry = self._detect_industry(job_description)
            industry_recommendations = self._get_industry_recommendations(
                resume_data, job_description, detected_industry
            )
            
            # Generate recommendations
            analysis_results['recommendations'] = self._generate_recommendations(analysis_results)
            analysis_results['industry_specific_keywords'] = industry_recommendations
            analysis_results['detected_industry'] = detected_industry
            
        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")
        
        return analysis_results
    
    def _analyze_skills(self, resume_data: Dict, job_description: Dict) -> Dict:
        """Analyze skill matching between resume and job description"""
        resume_skills = set([skill.lower().strip() for skill in resume_data.get('skills', [])])
        required_skills = set([skill.lower().strip() for skill in job_description.get('required_skills', [])])
        preferred_skills = set([skill.lower().strip() for skill in job_description.get('preferred_skills', [])])
        
        all_jd_skills = required_skills.union(preferred_skills)
        
        # Find exact matches
        matched_skills = resume_skills.intersection(all_jd_skills)
        
        # Find partial matches (for compound skills)
        partial_matches = set()
        remaining_jd_skills = all_jd_skills - matched_skills
        remaining_resume_skills = resume_skills - matched_skills
        
        for jd_skill in remaining_jd_skills:
            for resume_skill in remaining_resume_skills:
                # Check if either skill contains the other (partial match)
                if jd_skill in resume_skill or resume_skill in jd_skill:
                    matched_skills.add(jd_skill)
                    partial_matches.add(jd_skill)
                    break
                # Check for common abbreviations/variations
                jd_words = set(jd_skill.split())
                resume_words = set(resume_skill.split())
                if jd_words & resume_words and len(jd_words & resume_words) >= 2:
                    matched_skills.add(jd_skill)
                    partial_matches.add(jd_skill)
                    break
        
        missing_skills = all_jd_skills - matched_skills
        extra_skills = resume_skills - matched_skills - partial_matches
        
        # Calculate skill match percentage
        if all_jd_skills:
            skill_match_percentage = (len(matched_skills) / len(all_jd_skills)) * 100
        else:
            # If no specific skills in JD, check if resume has any skills at all
            skill_match_percentage = 100 if resume_skills else 0
        
        return {
            'skill_match_percentage': skill_match_percentage,
            'matched_skills': list(matched_skills),
            'missing_skills': list(missing_skills),
            'extra_skills': list(extra_skills)
        }
    
    def _analyze_experience(self, resume_data: Dict, job_description: Dict) -> Dict:
        """Analyze experience relevance and duration"""
        resume_exp_years = resume_data.get('experience_years', 0)
        required_exp = job_description.get('experience_required', '0 years')
        
        # Extract required experience years
        required_years_match = re.search(r'(\d+)', required_exp)
        required_years = int(required_years_match.group(1)) if required_years_match else 0
        
        # Calculate experience relevance score
        if required_years == 0:
            experience_score = 100  # No specific requirement
        elif resume_exp_years >= required_years:
            # Bonus for exceeding requirements, but cap at 100
            experience_score = min(100, 100 + (resume_exp_years - required_years) * 5)
        else:
            # Penalty for not meeting requirements
            experience_score = max(0, (resume_exp_years / required_years) * 80)
        
        return {
            'experience_relevance_score': int(experience_score)
        }
    
    def _analyze_education(self, resume_data: Dict, job_description: Dict) -> Dict:
        """Analyze education alignment with job requirements"""
        resume_education = resume_data.get('education', [])
        required_education = job_description.get('education_required', '').lower()
        
        if not resume_education or 'not specified' in required_education:
            return {'education_alignment_score': 75}  # Neutral score
        
        # Check for degree level alignment
        education_score = 0
        resume_degrees = [edu.get('degree', '').lower() for edu in resume_education]
        
        degree_hierarchy = {
            'phd': 100, 'doctorate': 100, 'ph.d': 100,
            'master': 90, 'mba': 90, 'ms': 90, 'ma': 90, 'm.s': 90, 'm.a': 90,
            'bachelor': 80, 'bs': 80, 'ba': 80, 'b.s': 80, 'b.a': 80,
            'associate': 60, 'diploma': 50, 'certificate': 40
        }
        
        # Find highest degree in resume
        max_resume_score = 0
        for degree in resume_degrees:
            for level, score in degree_hierarchy.items():
                if level in degree:
                    max_resume_score = max(max_resume_score, score)
        
        # Find required degree level
        required_score = 70  # Default
        for level, score in degree_hierarchy.items():
            if level in required_education:
                required_score = score
                break
        
        # Calculate alignment score
        if max_resume_score >= required_score:
            education_score = 100
        elif max_resume_score > 0:
            education_score = (max_resume_score / required_score) * 80
        else:
            education_score = 30  # Some penalty for no clear degree
        
        return {
            'education_alignment_score': int(education_score)
        }
    
    def _analyze_formatting(self, resume_data: Dict) -> Dict:
        """Analyze resume formatting for ATS compatibility"""
        raw_text = resume_data.get('raw_text', '')
        formatting_score = 100
        formatting_issues = []
        
        # Check for common formatting issues
        
        # 1. Check for section headers
        headers_found = 0
        for header in self.formatting_rules['section_headers']:
            if header.lower() in raw_text.lower():
                headers_found += 1
        
        if headers_found < 3:
            formatting_score -= 15
            formatting_issues.append("Missing standard section headers (Summary, Experience, Education, Skills)")
        
        # 2. Check for bullet points or structured format
        bullet_patterns = [r'•', r'-\s', r'\*\s', r'\d+\.']
        has_bullets = any(re.search(pattern, raw_text) for pattern in bullet_patterns)
        
        if not has_bullets:
            formatting_score -= 10
            formatting_issues.append("No bullet points found - use bullets for better readability")
        
        # 3. Check text length and density
        if len(raw_text) < 500:
            formatting_score -= 10
            formatting_issues.append("Resume appears too short - consider adding more detail")
        elif len(raw_text) > 3000:
            formatting_score -= 5
            formatting_issues.append("Resume might be too long - consider condensing content")
        
        # 4. Check for contact information
        has_email = resume_data.get('email') is not None
        has_phone = resume_data.get('phone') is not None
        
        if not has_email:
            formatting_score -= 10
            formatting_issues.append("Email address not found - ensure contact information is clear")
        
        if not has_phone:
            formatting_score -= 5
            formatting_issues.append("Phone number not found - add contact information")
        
        # 5. Check for excessive formatting that might confuse ATS
        problematic_chars = ['|', '─', '═', '┌', '┐', '└', '┘']
        if any(char in raw_text for char in problematic_chars):
            formatting_score -= 15
            formatting_issues.append("Special characters detected that may confuse ATS systems")
        
        # 6. Check for proper spacing and structure
        lines = raw_text.split('\n')
        empty_line_ratio = sum(1 for line in lines if line.strip() == '') / len(lines)
        
        if empty_line_ratio > 0.5:
            formatting_score -= 8
            formatting_issues.append("Too many empty lines - optimize spacing for ATS readability")
        
        return {
            'formatting_score': max(0, formatting_score),
            'formatting_issues': formatting_issues
        }
    
    def _analyze_keywords(self, resume_data: Dict, job_description: Dict) -> Dict:
        """Analyze keyword density and optimization"""
        resume_text = resume_data.get('raw_text', '').lower()
        jd_text = job_description.get('raw_text', '').lower()
        
        # Extract important keywords from job description
        jd_words = re.findall(r'\b[a-zA-Z]{3,}\b', jd_text)
        jd_word_freq = Counter(jd_words)
        
        # Get most common JD keywords (excluding common words)
        stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'had', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'}
        
        important_jd_keywords = []
        for word, freq in jd_word_freq.most_common(20):
            if word not in stop_words and len(word) > 3:
                important_jd_keywords.append(word)
        
        # Check keyword presence in resume
        keyword_analysis = {}
        for keyword in important_jd_keywords[:15]:  # Top 15 keywords
            count = resume_text.count(keyword)
            keyword_analysis[keyword] = count
        
        return {
            'keyword_analysis': keyword_analysis
        }
    
    def _calculate_ats_score(self, analysis: Dict) -> int:
        """Calculate overall ATS compatibility score"""
        # Weighted scoring system
        weights = {
            'skill_match': 0.30,      # 30% - Most important
            'experience': 0.25,       # 25% - Very important
            'formatting': 0.20,       # 20% - Important for ATS parsing
            'education': 0.15,        # 15% - Moderately important
            'keyword_density': 0.10   # 10% - Nice to have
        }
        
        # Get individual scores
        skill_score = analysis.get('skill_match_percentage', 0)
        experience_score = analysis.get('experience_relevance_score', 0)
        education_score = analysis.get('education_alignment_score', 0)
        formatting_score = analysis.get('formatting_score', 0)
        
        # Calculate keyword density score
        keyword_analysis = analysis.get('keyword_analysis', {})
        if keyword_analysis:
            # Score based on how many important keywords are present
            keywords_present = sum(1 for count in keyword_analysis.values() if count > 0)
            total_keywords = len(keyword_analysis)
            keyword_score = (keywords_present / total_keywords) * 100 if total_keywords > 0 else 0
        else:
            keyword_score = 0
        
        # Calculate weighted average
        overall_score = (
            skill_score * weights['skill_match'] +
            experience_score * weights['experience'] +
            education_score * weights['education'] +
            formatting_score * weights['formatting'] +
            keyword_score * weights['keyword_density']
        )
        
        return int(overall_score)
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # Skill-based recommendations
        if analysis.get('skill_match_percentage', 0) < 70:
            missing_skills = analysis.get('missing_skills', [])
            if missing_skills:
                recommendations.append(
                    f"Add these missing key skills to your resume: {', '.join(missing_skills[:5])}"
                )
        
        # Experience recommendations
        if analysis.get('experience_relevance_score', 0) < 70:
            recommendations.append(
                "Highlight more relevant work experience or quantify your achievements with specific metrics"
            )
        
        # Formatting recommendations
        formatting_score = analysis.get('formatting_score', 0)
        if formatting_score < 80:
            formatting_issues = analysis.get('formatting_issues', [])
            if formatting_issues:
                recommendations.append(f"Fix formatting issues: {formatting_issues[0]}")
        
        # Keyword optimization
        keyword_analysis = analysis.get('keyword_analysis', {})
        if keyword_analysis:
            missing_keywords = [k for k, v in keyword_analysis.items() if v == 0]
            if len(missing_keywords) > 5:
                recommendations.append(
                    f"Consider incorporating these job-relevant keywords: {', '.join(missing_keywords[:3])}"
                )
        
        # Education recommendations
        if analysis.get('education_alignment_score', 0) < 70:
            recommendations.append(
                "Clearly highlight your educational background and any relevant certifications"
            )
        
        # Overall ATS score recommendations
        ats_score = analysis.get('ats_score', 0)
        if ats_score < 60:
            recommendations.append(
                "Your ATS score is low. Focus on adding relevant keywords and improving format structure"
            )
        elif ats_score < 80:
            recommendations.append(
                "Good progress! Fine-tune your resume by addressing the specific gaps identified above"
            )
        
        # General recommendations if score is very low
        if ats_score < 40:
            recommendations.extend([
                "Use a simple, clean format with clear section headers",
                "Include a professional summary highlighting your key qualifications",
                "Quantify your achievements with specific numbers and results"
            ])
        
        return recommendations[:8]  # Limit to top 8 recommendations
    
    def _detect_industry(self, job_description: Dict) -> str:
        """Detect the industry/role from job description"""
        jd_text = job_description.get('raw_text', '').lower()
        job_title = job_description.get('title', '').lower()
        
        # Combine title and text for matching
        combined_text = job_title + ' ' + jd_text
        
        # Check each industry's role keywords
        industry_scores = {}
        for industry, data in self.industry_keywords.items():
            score = 0
            for role in data['roles']:
                if role in combined_text:
                    score += 10
            for keyword in data['keywords'][:5]:
                if keyword in combined_text:
                    score += 1
            industry_scores[industry] = score
        
        # Return industry with highest score
        if industry_scores:
            max_score = max(industry_scores.values())
            if max_score > 0:
                detected = max(industry_scores.items(), key=lambda x: x[1])[0]
                return detected
        return 'general'
    
    def _get_industry_recommendations(self, resume_data: Dict, job_description: Dict, 
                                     industry: str) -> Dict:
        """Get industry-specific keyword recommendations"""
        if industry == 'general' or industry not in self.industry_keywords:
            return {'missing': [], 'present': [], 'industry': 'general'}
        
        industry_data = self.industry_keywords[industry]
        resume_text = resume_data.get('raw_text', '').lower()
        
        missing_keywords = []
        present_keywords = []
        
        for keyword in industry_data['keywords']:
            if keyword.lower() in resume_text:
                present_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        return {
            'missing': missing_keywords[:8],
            'present': present_keywords,
            'industry': industry.replace('_', ' ').title()
        }
    
    def get_improvement_priority(self, analysis: Dict) -> List[Tuple[str, int, str]]:
        """Get prioritized list of improvement areas"""
        priorities = []
        
        # Check each component and add to priority list
        skill_match = analysis.get('skill_match_percentage', 0)
        if skill_match < 70:
            impact = 100 - skill_match
            priorities.append(('Skills', impact, 'Add missing key skills from job description'))
        
        experience_score = analysis.get('experience_relevance_score', 0)
        if experience_score < 70:
            impact = 100 - experience_score
            priorities.append(('Experience', impact, 'Better highlight relevant work experience'))
        
        formatting_score = analysis.get('formatting_score', 0)
        if formatting_score < 80:
            impact = 100 - formatting_score
            priorities.append(('Formatting', impact, 'Improve ATS-friendly formatting'))
        
        education_score = analysis.get('education_alignment_score', 0)
        if education_score < 70:
            impact = 100 - education_score
            priorities.append(('Education', impact, 'Clarify educational background'))
        
        # Sort by impact (higher impact = higher priority)
        priorities.sort(key=lambda x: x[1], reverse=True)
        
        return priorities
