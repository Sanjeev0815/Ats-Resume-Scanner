import re
from typing import Dict, List, Optional
import streamlit as st

class AIChatbot:
    """Rule-based chatbot for resume advice - no API required"""
    
    def __init__(self):
        # Knowledge base for common questions
        self.knowledge_base = {
            'ats': [
                'ATS (Applicant Tracking System) compatibility is crucial for getting your resume past initial screening.',
                'Focus on using standard section headers, simple formatting, and relevant keywords.',
                'Avoid tables, images, and complex formatting that ATS systems may not read correctly.'
            ],
            'skills': [
                'List skills that directly match the job description requirements.',
                'Include both technical and soft skills relevant to the position.',
                'Use the exact skill names mentioned in the job posting when applicable.'
            ],
            'formatting': [
                'Use standard fonts like Arial, Calibri, or Times New Roman.',
                'Stick to clear section headers: Summary, Experience, Education, Skills.',
                'Use bullet points for easy readability and ATS parsing.',
                'Avoid headers, footers, tables, and text boxes.'
            ],
            'keywords': [
                'Naturally incorporate keywords from the job description throughout your resume.',
                'Place important keywords in your skills section and experience descriptions.',
                'Avoid keyword stuffing - use terms naturally in context.'
            ],
            'experience': [
                'Quantify your achievements with specific numbers and results.',
                'Use action verbs to start each bullet point (achieved, managed, led, etc.).',
                'Highlight experience most relevant to the target role.',
                'Focus on accomplishments rather than just responsibilities.'
            ],
            'education': [
                'List your highest degree first.',
                'Include relevant coursework or certifications if applicable.',
                'Mention academic honors or significant achievements.',
                'Ensure your education aligns with job requirements.'
            ]
        }
    
    def get_response(self, user_message: str, analysis_results: Dict, resume_data: Dict, job_description: Dict) -> str:
        """Get response based on user question and resume analysis"""
        user_message_lower = user_message.lower()
        
        # Detect question type and provide targeted response
        if any(word in user_message_lower for word in ['ats', 'score', 'improve score', 'compatibility']):
            return self._get_ats_improvement_advice(analysis_results)
        
        elif any(word in user_message_lower for word in ['skill', 'missing', 'add skill']):
            return self._get_skill_advice(analysis_results)
        
        elif any(word in user_message_lower for word in ['format', 'formatting', 'structure']):
            return self._get_formatting_advice(analysis_results)
        
        elif any(word in user_message_lower for word in ['keyword', 'optimize']):
            return self._get_keyword_advice(analysis_results)
        
        elif any(word in user_message_lower for word in ['experience', 'work history']):
            return self._get_experience_advice(analysis_results, resume_data, job_description)
        
        elif any(word in user_message_lower for word in ['education', 'degree', 'qualification']):
            return self._get_education_advice(analysis_results, resume_data, job_description)
        
        else:
            # General improvement advice
            return self._get_general_advice(analysis_results)
    
    def _get_ats_improvement_advice(self, analysis: Dict) -> str:
        """Provide ATS score improvement advice"""
        ats_score = analysis.get('ats_score', 0)
        skill_match = analysis.get('skill_match_percentage', 0)
        format_score = analysis.get('formatting_score', 0)
        
        advice = []
        
        if ats_score >= 80:
            advice.append("Great job! Your resume has strong ATS compatibility. Here are some ways to optimize even further:")
        elif ats_score >= 60:
            advice.append("Your resume has decent ATS compatibility, but there's room for improvement. Focus on these areas:")
        else:
            advice.append("Your resume needs significant ATS optimization. Here's what you should prioritize:")
        
        # Skill-based recommendations
        if skill_match < 70:
            missing_skills = analysis.get('missing_skills', [])
            if missing_skills:
                advice.append(f"\n**Skills Gap (Priority: High)**")
                advice.append(f"Add these missing skills if you have them: {', '.join(missing_skills[:5])}")
                advice.append("This could boost your ATS score by 15-20 points.")
        
        # Formatting recommendations
        if format_score < 80:
            advice.append(f"\n**Formatting Issues (Priority: Medium)**")
            formatting_issues = analysis.get('formatting_issues', [])
            if formatting_issues:
                advice.append(f"Fix these formatting problems:")
                for issue in formatting_issues[:3]:
                    advice.append(f"- {issue}")
            advice.append("Improving formatting could add 10-15 points to your ATS score.")
        
        # Keyword optimization
        keyword_analysis = analysis.get('keyword_analysis', {})
        missing_keywords = [k for k, v in keyword_analysis.items() if v == 0]
        if len(missing_keywords) > 3:
            advice.append(f"\n**Keyword Optimization (Priority: Medium)**")
            advice.append(f"Incorporate these job-relevant keywords: {', '.join(missing_keywords[:4])}")
            advice.append("Natural keyword inclusion can improve your score by 5-10 points.")
        
        return "\n".join(advice)
    
    def _get_skill_advice(self, analysis: Dict) -> str:
        """Provide skill-related advice"""
        missing_skills = analysis.get('missing_skills', [])
        matched_skills = analysis.get('matched_skills', [])
        extra_skills = analysis.get('extra_skills', [])
        
        advice = []
        advice.append("**Skill Optimization Strategy:**\n")
        
        if matched_skills:
            advice.append(f"✅ **Strengths** - You already have these key skills: {', '.join(matched_skills[:5])}")
            advice.append("Keep these prominently displayed in your skills section.\n")
        
        if missing_skills:
            advice.append(f"❌ **Missing Skills** - The job requires: {', '.join(missing_skills[:8])}")
            advice.append("\n**Action Steps:**")
            advice.append("1. Review each missing skill - if you have experience with it, add it to your resume")
            advice.append("2. Provide specific examples of using these skills in your work experience")
            advice.append("3. Consider taking courses or certifications in critical missing skills\n")
        
        if extra_skills:
            advice.append(f"➕ **Competitive Advantage** - These additional skills set you apart: {', '.join(extra_skills[:4])}")
            advice.append("These can be valuable differentiators if they're relevant to the role.")
        
        return "\n".join(advice)
    
    def _get_formatting_advice(self, analysis: Dict) -> str:
        """Provide formatting advice"""
        format_score = analysis.get('formatting_score', 0)
        formatting_issues = analysis.get('formatting_issues', [])
        
        advice = []
        advice.append(f"**Formatting Analysis (Score: {format_score}/100)**\n")
        
        if formatting_issues:
            advice.append("**Issues to Fix:**")
            for i, issue in enumerate(formatting_issues, 1):
                advice.append(f"{i}. {issue}")
            advice.append("")
        
        advice.append("**ATS-Friendly Formatting Best Practices:**")
        advice.append("• Use standard section headers: Summary, Experience, Education, Skills")
        advice.append("• Choose simple fonts: Arial, Calibri, or Times New Roman (10-12pt)")
        advice.append("• Use bullet points for responsibilities and achievements")
        advice.append("• Avoid tables, text boxes, headers/footers, and images")
        advice.append("• Keep formatting consistent throughout")
        advice.append("• Save as both .docx and .pdf formats")
        advice.append("• Ensure contact information is clearly visible at the top")
        
        return "\n".join(advice)
    
    def _get_keyword_advice(self, analysis: Dict) -> str:
        """Provide keyword optimization advice"""
        keyword_analysis = analysis.get('keyword_analysis', {})
        
        advice = []
        advice.append("**Keyword Optimization Strategy:**\n")
        
        if keyword_analysis:
            present_keywords = {k: v for k, v in keyword_analysis.items() if v > 0}
            missing_keywords = {k: v for k, v in keyword_analysis.items() if v == 0}
            
            if present_keywords:
                advice.append(f"✅ **Keywords Found:** {', '.join(list(present_keywords.keys())[:5])}")
                advice.append("These are being picked up by ATS systems.\n")
            
            if missing_keywords:
                advice.append(f"❌ **Missing Keywords:** {', '.join(list(missing_keywords.keys())[:6])}")
                advice.append("\n**How to Add Keywords Naturally:**")
                advice.append("1. Incorporate them in your professional summary")
                advice.append("2. Use them when describing your experience and achievements")
                advice.append("3. Include them in your skills section if applicable")
                advice.append("4. Add them to project descriptions or certifications")
                advice.append("\n**Important:** Don't just list keywords - use them in meaningful context!")
        else:
            advice.append("Focus on including terms and phrases directly from the job description.")
            advice.append("Pay special attention to required qualifications and key responsibilities.")
        
        return "\n".join(advice)
    
    def _get_experience_advice(self, analysis: Dict, resume_data: Dict, job_description: Dict) -> str:
        """Provide experience-related advice"""
        exp_score = analysis.get('experience_relevance_score', 0)
        resume_exp = resume_data.get('experience_years', 0)
        
        advice = []
        advice.append(f"**Experience Optimization (Score: {exp_score}/100)**\n")
        
        if exp_score >= 80:
            advice.append("Your experience aligns well with the job requirements. To make it even stronger:")
        elif exp_score >= 60:
            advice.append("Your experience is relevant but could be better highlighted:")
        else:
            advice.append("Let's improve how you present your experience:")
        
        advice.append("\n**Best Practices:**")
        advice.append("• Start each bullet with action verbs (achieved, managed, led, improved)")
        advice.append("• Quantify achievements with specific numbers and percentages")
        advice.append("• Focus on results and impact, not just responsibilities")
        advice.append("• Tailor descriptions to match job requirements")
        advice.append("• Use the STAR method (Situation, Task, Action, Result)")
        
        advice.append("\n**Examples of Strong Bullets:**")
        advice.append("❌ Weak: 'Responsible for managing team'")
        advice.append("✅ Strong: 'Led team of 8 developers, improving delivery speed by 30%'")
        advice.append("")
        advice.append("❌ Weak: 'Worked on sales projects'")
        advice.append("✅ Strong: 'Increased quarterly sales by 25% through strategic client engagement'")
        
        return "\n".join(advice)
    
    def _get_education_advice(self, analysis: Dict, resume_data: Dict, job_description: Dict) -> str:
        """Provide education-related advice"""
        edu_score = analysis.get('education_alignment_score', 0)
        education = resume_data.get('education', [])
        
        advice = []
        advice.append(f"**Education Section (Score: {edu_score}/100)**\n")
        
        if edu_score >= 80:
            advice.append("Your education meets the job requirements well.")
        elif edu_score >= 60:
            advice.append("Your education is acceptable, but consider these enhancements:")
        else:
            advice.append("Strengthen your education section with these improvements:")
        
        advice.append("\n**Optimization Tips:**")
        advice.append("• List your highest/most relevant degree first")
        advice.append("• Include graduation date (or expected date if current student)")
        advice.append("• Add relevant coursework if it matches job requirements")
        advice.append("• Highlight academic honors, awards, or high GPA (3.5+)")
        advice.append("• Include relevant certifications and training")
        
        if not education or len(education) == 0:
            advice.append("\n**Action:** Ensure your education section is clearly visible and complete")
        
        advice.append("\n**Additional Qualifications:**")
        advice.append("Consider adding certifications related to the role (online courses, bootcamps, professional certifications)")
        
        return "\n".join(advice)
    
    def _get_general_advice(self, analysis: Dict) -> str:
        """Provide general resume improvement advice"""
        ats_score = analysis.get('ats_score', 0)
        recommendations = analysis.get('recommendations', [])
        
        advice = []
        advice.append(f"**Overall Resume Assessment (ATS Score: {ats_score}/100)**\n")
        
        if recommendations:
            advice.append("**Top Priority Actions:**")
            for i, rec in enumerate(recommendations[:5], 1):
                advice.append(f"{i}. {rec}")
            advice.append("")
        
        advice.append("**General Resume Best Practices:**")
        advice.append("• Keep it concise (1-2 pages)")
        advice.append("• Use clear, professional language")
        advice.append("• Tailor your resume for each job application")
        advice.append("• Proofread carefully for errors")
        advice.append("• Update regularly with new skills and achievements")
        advice.append("• Use consistent formatting throughout")
        
        advice.append("\n**Quick Wins:**")
        advice.append("1. Add missing skills you actually possess")
        advice.append("2. Fix any formatting issues identified")
        advice.append("3. Quantify at least 3 achievements with numbers")
        advice.append("4. Ensure contact info is complete and correct")
        
        return "\n".join(advice)
    
    def get_specific_advice(self, topic: str, analysis_results: Dict, resume_data: Dict, job_description: Dict) -> str:
        """Get specific advice for common topics"""
        topic_map = {
            'ats_score': lambda: self._get_ats_improvement_advice(analysis_results),
            'skills': lambda: self._get_skill_advice(analysis_results),
            'formatting': lambda: self._get_formatting_advice(analysis_results),
            'keywords': lambda: self._get_keyword_advice(analysis_results),
            'experience': lambda: self._get_experience_advice(analysis_results, resume_data, job_description),
            'education': lambda: self._get_education_advice(analysis_results, resume_data, job_description)
        }
        
        advice_func = topic_map.get(topic)
        if advice_func:
            return advice_func()
        return self._get_general_advice(analysis_results)
    
    def generate_improvement_plan(self, analysis_results: Dict, resume_data: Dict, job_description: Dict) -> str:
        """Generate a comprehensive improvement plan"""
        ats_score = analysis_results.get('ats_score', 0)
        skill_match = analysis_results.get('skill_match_percentage', 0)
        format_score = analysis_results.get('formatting_score', 0)
        
        plan = []
        plan.append("**📋 Prioritized Resume Improvement Plan**\n")
        
        # Determine top 3 priorities based on scores
        priorities = []
        
        if skill_match < 70:
            priorities.append(('Skills Gap', skill_match, 'High Impact'))
        if format_score < 80:
            priorities.append(('Formatting', format_score, 'Medium Impact'))
        if analysis_results.get('experience_relevance_score', 0) < 70:
            priorities.append(('Experience Presentation', analysis_results.get('experience_relevance_score', 0), 'High Impact'))
        
        # Sort by score (lowest first = highest priority)
        priorities.sort(key=lambda x: x[1])
        
        plan.append("**🎯 Top 3 Priorities (Most Impact First):**\n")
        
        for i, (area, score, impact) in enumerate(priorities[:3], 1):
            plan.append(f"**Priority {i}: {area}** (Current Score: {score:.0f}/100, {impact})")
            
            if 'Skills' in area:
                missing_skills = analysis_results.get('missing_skills', [])
                plan.append("Action Steps:")
                plan.append(f"  • Add these missing skills: {', '.join(missing_skills[:5])}")
                plan.append("  • Provide examples of using these skills in your experience")
                plan.append(f"  • Estimated impact: +15-20 points to ATS score\n")
            
            elif 'Formatting' in area:
                plan.append("Action Steps:")
                plan.append("  • Fix section headers (use: Summary, Experience, Education, Skills)")
                plan.append("  • Remove tables, images, and complex formatting")
                plan.append("  • Use simple bullet points for readability")
                plan.append(f"  • Estimated impact: +10-15 points to ATS score\n")
            
            elif 'Experience' in area:
                plan.append("Action Steps:")
                plan.append("  • Quantify achievements with specific numbers")
                plan.append("  • Use action verbs to start each bullet point")
                plan.append("  • Align experience descriptions with job requirements")
                plan.append(f"  • Estimated impact: +10-15 points to ATS score\n")
        
        plan.append("\n**⚡ Quick Wins (Implement Today):**")
        plan.append("1. Update contact information to be clearly visible")
        plan.append("2. Add 2-3 missing skills you already possess")
        plan.append("3. Fix the most critical formatting issue identified")
        plan.append("4. Add at least one quantified achievement")
        
        plan.append("\n**📈 Expected Results:**")
        if ats_score < 60:
            plan.append("Following this plan could improve your ATS score to 70-80/100")
        elif ats_score < 80:
            plan.append("Following this plan could improve your ATS score to 85-90/100")
        else:
            plan.append("These refinements will optimize your already strong resume to 90+/100")
        
        plan.append("\n**💡 Remember:** Customize your resume for each job application by adjusting keywords and emphasis!")
        
        return "\n".join(plan)
    
    def explain_score_components(self, analysis_results: Dict) -> str:
        """Explain how the ATS score was calculated"""
        ats_score = analysis_results.get('ats_score', 0)
        skill_match = analysis_results.get('skill_match_percentage', 0)
        exp_score = analysis_results.get('experience_relevance_score', 0)
        edu_score = analysis_results.get('education_alignment_score', 0)
        format_score = analysis_results.get('formatting_score', 0)
        
        explanation = []
        explanation.append(f"**Understanding Your ATS Score: {ats_score}/100**\n")
        
        explanation.append("Your ATS score is calculated using a weighted formula:\n")
        
        explanation.append(f"**1. Skill Match (30% weight): {skill_match:.1f}%**")
        explanation.append("   Measures how well your skills align with job requirements")
        if skill_match >= 80:
            explanation.append("   ✅ Excellent - You have most required skills")
        elif skill_match >= 60:
            explanation.append("   ⚠️  Good - Some key skills are missing")
        else:
            explanation.append("   ❌ Needs work - Major skill gaps identified\n")
        
        explanation.append(f"\n**2. Experience Relevance (25% weight): {exp_score}/100**")
        explanation.append("   Evaluates your experience level and relevance")
        if exp_score >= 80:
            explanation.append("   ✅ Excellent - Strong relevant experience")
        elif exp_score >= 60:
            explanation.append("   ⚠️  Good - Experience is adequate")
        else:
            explanation.append("   ❌ Needs work - Limited relevant experience shown\n")
        
        explanation.append(f"\n**3. Formatting Quality (20% weight): {format_score}/100**")
        explanation.append("   Assesses ATS-friendly formatting and structure")
        if format_score >= 80:
            explanation.append("   ✅ Excellent - ATS can easily parse your resume")
        elif format_score >= 60:
            explanation.append("   ⚠️  Good - Minor formatting improvements needed")
        else:
            explanation.append("   ❌ Needs work - Formatting may confuse ATS systems\n")
        
        explanation.append(f"\n**4. Education Alignment (15% weight): {edu_score}/100**")
        explanation.append("   Checks if education meets job requirements")
        if edu_score >= 80:
            explanation.append("   ✅ Excellent - Education matches or exceeds requirements")
        elif edu_score >= 60:
            explanation.append("   ⚠️  Good - Education is acceptable")
        else:
            explanation.append("   ❌ Needs work - Educational requirements not clearly met\n")
        
        explanation.append("\n**5. Keyword Optimization (10% weight)**")
        explanation.append("   Measures presence of job-relevant keywords")
        explanation.append("   Important for ATS scanning and ranking\n")
        
        explanation.append("**What Makes a Good Score?**")
        explanation.append("• 80-100: Excellent - High chance of passing ATS")
        explanation.append("• 60-79: Good - Likely to pass with some improvements")
        explanation.append("• Below 60: Needs work - Significant optimization required")
        
        return "\n".join(explanation)
