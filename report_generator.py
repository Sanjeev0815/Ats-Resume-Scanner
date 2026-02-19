import io
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import streamlit as st
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

class ReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.colors = {
            'primary': HexColor('#1f77b4'),
            'success': HexColor('#2ca02c'),
            'warning': HexColor('#ff7f0e'), 
            'danger': HexColor('#d62728'),
            'dark': HexColor('#262730')
        }
        
        # Custom styles
        self.custom_styles = {
            'CustomTitle': ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Title'],
                fontSize=24,
                spaceAfter=30,
                textColor=self.colors['primary']
            ),
            'CustomHeading': ParagraphStyle(
                'CustomHeading',
                parent=self.styles['Heading2'],
                fontSize=16,
                spaceAfter=12,
                textColor=self.colors['dark']
            ),
            'CustomSubheading': ParagraphStyle(
                'CustomSubheading',
                parent=self.styles['Heading3'],
                fontSize=14,
                spaceAfter=8,
                textColor=self.colors['dark']
            )
        }
    
    def generate_pdf_report(self, resume_data: Dict, job_description: Dict, analysis_results: Dict) -> Optional[io.BytesIO]:
        """Generate comprehensive PDF report"""
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
            
            # Build report content
            content = []
            
            # Title and header
            content.append(Paragraph("ResumeScan AI - ATS Analysis Report", self.custom_styles['CustomTitle']))
            content.append(Spacer(1, 12))
            
            # Report metadata
            report_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
            candidate_name = resume_data.get('name', 'Candidate')
            
            content.append(Paragraph(f"<b>Candidate:</b> {candidate_name}", self.styles['Normal']))
            content.append(Paragraph(f"<b>Report Generated:</b> {report_date}", self.styles['Normal']))
            content.append(Spacer(1, 20))
            
            # Executive Summary
            content.extend(self._add_executive_summary(analysis_results))
            content.append(Spacer(1, 20))
            
            # Detailed Analysis Sections
            content.extend(self._add_score_breakdown(analysis_results))
            content.append(Spacer(1, 15))
            
            content.extend(self._add_skill_analysis(analysis_results))
            content.append(Spacer(1, 15))
            
            content.extend(self._add_formatting_analysis(analysis_results))
            content.append(Spacer(1, 15))
            
            content.extend(self._add_recommendations(analysis_results))
            content.append(Spacer(1, 15))
            
            content.extend(self._add_action_plan(analysis_results))
            
            # Build PDF
            doc.build(content)
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            st.error(f"Error generating PDF report: {str(e)}")
            return None
    
    def _add_executive_summary(self, analysis: Dict) -> List:
        """Add executive summary section to report"""
        content = []
        
        content.append(Paragraph("Executive Summary", self.custom_styles['CustomHeading']))
        
        ats_score = analysis.get('ats_score', 0)
        skill_match = analysis.get('skill_match_percentage', 0)
        
        # Overall assessment
        if ats_score >= 80:
            status = "Excellent"
            color = "green"
        elif ats_score >= 60:
            status = "Good" 
            color = "orange"
        else:
            status = "Needs Improvement"
            color = "red"
        
        summary_text = f"""
        Your resume has been analyzed against the provided job description with an overall ATS compatibility score of <b>{ats_score}/100</b> - <font color="{color}"><b>{status}</b></font>.
        
        <b>Key Findings:</b><br/>
        • Skill Match: {skill_match:.1f}% of required skills identified<br/>
        • Experience Relevance: {analysis.get('experience_relevance_score', 0)}/100<br/>
        • Education Alignment: {analysis.get('education_alignment_score', 0)}/100<br/>
        • Formatting Quality: {analysis.get('formatting_score', 0)}/100<br/>
        """
        
        content.append(Paragraph(summary_text, self.styles['Normal']))
        content.append(Spacer(1, 12))
        
        # Quick stats table
        stats_data = [
            ['Metric', 'Score', 'Status'],
            ['ATS Compatibility', f"{ats_score}/100", self._get_score_status(ats_score)],
            ['Skill Match', f"{skill_match:.1f}%", self._get_score_status(skill_match)],
            ['Experience', f"{analysis.get('experience_relevance_score', 0)}/100", self._get_score_status(analysis.get('experience_relevance_score', 0))],
            ['Education', f"{analysis.get('education_alignment_score', 0)}/100", self._get_score_status(analysis.get('education_alignment_score', 0))],
            ['Formatting', f"{analysis.get('formatting_score', 0)}/100", self._get_score_status(analysis.get('formatting_score', 0))]
        ]
        
        stats_table = Table(stats_data, colWidths=[2*inch, 1*inch, 1.5*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        content.append(stats_table)
        
        return content
    
    def _add_score_breakdown(self, analysis: Dict) -> List:
        """Add detailed score breakdown section"""
        content = []
        
        content.append(Paragraph("Score Breakdown & Analysis", self.custom_styles['CustomHeading']))
        
        # ATS Score explanation
        content.append(Paragraph("ATS Compatibility Score Components:", self.custom_styles['CustomSubheading']))
        
        breakdown_text = f"""
        Your overall ATS score of {analysis.get('ats_score', 0)}/100 is calculated using the following weighted components:
        
        <b>• Skill Matching (30% weight):</b> {analysis.get('skill_match_percentage', 0):.1f}%<br/>
        Measures how well your resume skills align with job requirements.
        
        <b>• Experience Relevance (25% weight):</b> {analysis.get('experience_relevance_score', 0)}/100<br/>
        Evaluates your experience level and relevance to the position.
        
        <b>• Formatting Quality (20% weight):</b> {analysis.get('formatting_score', 0)}/100<br/>
        Assesses ATS-friendly formatting and structure.
        
        <b>• Education Alignment (15% weight):</b> {analysis.get('education_alignment_score', 0)}/100<br/>
        Checks educational background against job requirements.
        
        <b>• Keyword Optimization (10% weight):</b> Based on job description keyword presence<br/>
        Measures inclusion of important keywords from the job posting.
        """
        
        content.append(Paragraph(breakdown_text, self.styles['Normal']))
        
        return content
    
    def _add_skill_analysis(self, analysis: Dict) -> List:
        """Add skill analysis section"""
        content = []
        
        content.append(Paragraph("Skill Analysis", self.custom_styles['CustomHeading']))
        
        matched_skills = analysis.get('matched_skills', [])
        missing_skills = analysis.get('missing_skills', [])
        extra_skills = analysis.get('extra_skills', [])
        
        # Matched skills
        if matched_skills:
            content.append(Paragraph("✅ <b>Skills Successfully Matched:</b>", self.custom_styles['CustomSubheading']))
            matched_text = "• " + "<br/>• ".join(matched_skills)
            content.append(Paragraph(matched_text, self.styles['Normal']))
            content.append(Spacer(1, 10))
        
        # Missing skills
        if missing_skills:
            content.append(Paragraph("❌ <b>Missing Key Skills:</b>", self.custom_styles['CustomSubheading']))
            missing_text = "• " + "<br/>• ".join(missing_skills[:10])  # Limit to top 10
            content.append(Paragraph(missing_text, self.styles['Normal']))
            content.append(Paragraph("<i>Consider adding these skills if you have experience with them.</i>", self.styles['Italic']))
            content.append(Spacer(1, 10))
        
        # Extra skills
        if extra_skills:
            content.append(Paragraph("➕ <b>Additional Skills (Competitive Advantage):</b>", self.custom_styles['CustomSubheading']))
            extra_text = "• " + "<br/>• ".join(extra_skills[:8])  # Limit to top 8
            content.append(Paragraph(extra_text, self.styles['Normal']))
            content.append(Paragraph("<i>These additional skills may give you a competitive edge.</i>", self.styles['Italic']))
        
        return content
    
    def _add_formatting_analysis(self, analysis: Dict) -> List:
        """Add formatting analysis section"""
        content = []
        
        content.append(Paragraph("Formatting & ATS Readability", self.custom_styles['CustomHeading']))
        
        formatting_score = analysis.get('formatting_score', 0)
        formatting_issues = analysis.get('formatting_issues', [])
        
        content.append(Paragraph(f"<b>Formatting Score:</b> {formatting_score}/100", self.styles['Normal']))
        content.append(Spacer(1, 8))
        
        if formatting_issues:
            content.append(Paragraph("<b>Issues Identified:</b>", self.custom_styles['CustomSubheading']))
            for i, issue in enumerate(formatting_issues, 1):
                content.append(Paragraph(f"{i}. {issue}", self.styles['Normal']))
            content.append(Spacer(1, 10))
        
        # Best practices
        content.append(Paragraph("<b>ATS Formatting Best Practices:</b>", self.custom_styles['CustomSubheading']))
        best_practices = [
            "Use standard section headers (Summary, Experience, Education, Skills)",
            "Include clear contact information at the top", 
            "Use bullet points for easy scanning",
            "Avoid tables, text boxes, and complex formatting",
            "Use standard fonts (Arial, Calibri, Times New Roman)",
            "Save as both .docx and .pdf versions",
            "Keep formatting simple and clean"
        ]
        
        for practice in best_practices:
            content.append(Paragraph(f"• {practice}", self.styles['Normal']))
        
        return content
    
    def _add_recommendations(self, analysis: Dict) -> List:
        """Add recommendations section"""
        content = []
        
        content.append(Paragraph("Key Recommendations", self.custom_styles['CustomHeading']))
        
        recommendations = analysis.get('recommendations', [])
        
        if recommendations:
            content.append(Paragraph("Based on your analysis, here are the top priority improvements:", self.styles['Normal']))
            content.append(Spacer(1, 8))
            
            for i, rec in enumerate(recommendations, 1):
                content.append(Paragraph(f"<b>{i}.</b> {rec}", self.styles['Normal']))
                content.append(Spacer(1, 4))
        else:
            content.append(Paragraph("Your resume is well-optimized! Continue to tailor it for each specific job application.", self.styles['Normal']))
        
        return content
    
    def _add_action_plan(self, analysis: Dict) -> List:
        """Add action plan section"""
        content = []
        
        content.append(Paragraph("Action Plan", self.custom_styles['CustomHeading']))
        
        ats_score = analysis.get('ats_score', 0)
        
        if ats_score < 60:
            priority = "High Priority - Immediate Action Needed"
            timeline = "Complete within 1-2 days"
            color = "red"
        elif ats_score < 80:
            priority = "Medium Priority - Good Progress Needed"
            timeline = "Complete within 3-5 days"
            color = "orange"
        else:
            priority = "Low Priority - Fine-tuning"
            timeline = "Review and refine over 1 week"
            color = "green"
        
        content.append(Paragraph(f"<b>Priority Level:</b> <font color='{color}'>{priority}</font>", self.styles['Normal']))
        content.append(Paragraph(f"<b>Recommended Timeline:</b> {timeline}", self.styles['Normal']))
        content.append(Spacer(1, 12))
        
        # Step-by-step plan
        content.append(Paragraph("<b>Step-by-Step Improvement Plan:</b>", self.custom_styles['CustomSubheading']))
        
        steps = [
            "Review and address missing skills - add relevant ones you possess",
            "Fix formatting issues identified in the analysis",
            "Incorporate important keywords naturally throughout your resume",
            "Quantify achievements with specific numbers and results",
            "Optimize your professional summary with key qualifications",
            "Review and strengthen experience descriptions",
            "Proofread for grammar, spelling, and consistency",
            "Test with different ATS tools if possible",
            "Save in multiple formats (.pdf, .docx)",
            "Re-run analysis to track improvements"
        ]
        
        for i, step in enumerate(steps, 1):
            content.append(Paragraph(f"{i}. {step}", self.styles['Normal']))
        
        content.append(Spacer(1, 15))
        content.append(Paragraph("<b>Remember:</b> Customize your resume for each job application by adjusting keywords and emphasis based on the specific job description.", self.styles['Normal']))
        
        return content
    
    def _get_score_status(self, score: float) -> str:
        """Get status label for score"""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        else:
            return "Poor"
    
    def generate_excel_report(self, resume_data: Dict, job_description: Dict, analysis_results: Dict) -> Optional[io.BytesIO]:
        """Generate Excel report with detailed data"""
        try:
            buffer = io.BytesIO()
            
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                # Summary sheet
                summary_data = {
                    'Metric': ['ATS Score', 'Skill Match %', 'Experience Score', 'Education Score', 'Formatting Score'],
                    'Value': [
                        analysis_results.get('ats_score', 0),
                        analysis_results.get('skill_match_percentage', 0),
                        analysis_results.get('experience_relevance_score', 0),
                        analysis_results.get('education_alignment_score', 0),
                        analysis_results.get('formatting_score', 0)
                    ]
                }
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
                
                # Skills analysis
                skills_data = []
                
                for skill in analysis_results.get('matched_skills', []):
                    skills_data.append({'Skill': skill, 'Status': 'Matched', 'Action': 'Keep and emphasize'})
                
                for skill in analysis_results.get('missing_skills', []):
                    skills_data.append({'Skill': skill, 'Status': 'Missing', 'Action': 'Add if applicable'})
                
                for skill in analysis_results.get('extra_skills', []):
                    skills_data.append({'Skill': skill, 'Status': 'Extra', 'Action': 'Competitive advantage'})
                
                if skills_data:
                    pd.DataFrame(skills_data).to_excel(writer, sheet_name='Skills Analysis', index=False)
                
                # Keywords analysis
                keyword_analysis = analysis_results.get('keyword_analysis', {})
                if keyword_analysis:
                    keyword_data = {
                        'Keyword': list(keyword_analysis.keys()),
                        'Frequency in Resume': list(keyword_analysis.values()),
                        'Status': ['Present' if freq > 0 else 'Missing' for freq in keyword_analysis.values()]
                    }
                    pd.DataFrame(keyword_data).to_excel(writer, sheet_name='Keywords', index=False)
                
                # Recommendations
                recommendations = analysis_results.get('recommendations', [])
                if recommendations:
                    rec_data = {
                        'Priority': list(range(1, len(recommendations) + 1)),
                        'Recommendation': recommendations,
                        'Status': ['Pending'] * len(recommendations)
                    }
                    pd.DataFrame(rec_data).to_excel(writer, sheet_name='Recommendations', index=False)
                
                # Resume data
                resume_summary = {
                    'Field': ['Name', 'Email', 'Phone', 'Total Skills', 'Experience Years'],
                    'Value': [
                        resume_data.get('name', ''),
                        resume_data.get('email', ''),
                        resume_data.get('phone', ''),
                        len(resume_data.get('skills', [])),
                        resume_data.get('experience_years', 0)
                    ]
                }
                pd.DataFrame(resume_summary).to_excel(writer, sheet_name='Resume Data', index=False)
            
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            st.error(f"Error generating Excel report: {str(e)}")
            return None
