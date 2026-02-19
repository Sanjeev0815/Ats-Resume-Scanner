import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import io
import base64
from datetime import datetime

from resume_parser import ResumeParser
from ats_analyzer import ATSAnalyzer
from ai_chatbot import AIChatbot
from report_generator import ReportGenerator

# Initialize components
@st.cache_resource
def init_components():
    parser = ResumeParser()
    analyzer = ATSAnalyzer()
    chatbot = AIChatbot()
    report_gen = ReportGenerator()
    return parser, analyzer, chatbot, report_gen

def main():
    st.set_page_config(
        page_title="ResumeScan AI - Smart ATS Resume Scanner",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    parser, analyzer, chatbot, report_gen = init_components()
    
    # Initialize session state
    if 'resume_data' not in st.session_state:
        st.session_state.resume_data = None
    if 'job_description' not in st.session_state:
        st.session_state.job_description = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a section:",
        ["Home", "Upload & Analyze", "Resume Editor", "ATS Dashboard", "AI Chatbot", "Comparison", "Reports"]
    )
    
    if page == "Home":
        show_home_page()
    elif page == "Upload & Analyze":
        show_upload_page(parser, analyzer)
    elif page == "Resume Editor":
        show_resume_editor_page(parser, analyzer)
    elif page == "ATS Dashboard":
        show_dashboard_page()
    elif page == "AI Chatbot":
        show_chatbot_page(chatbot)
    elif page == "Comparison":
        show_comparison_page(parser, analyzer)
    elif page == "Reports":
        show_reports_page(report_gen)

def show_home_page():
    st.title("ResumeScan AI - Smart ATS Resume Scanner")
    st.markdown("### Optimize your resume for ATS systems with AI-powered insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### Upload & Parse")
        st.markdown("- Support for PDF, DOCX, TXT formats")
        st.markdown("- Extract key information automatically")
        st.markdown("- Clean data processing")
    
    with col2:
        st.markdown("#### ATS Analysis")
        st.markdown("- Compatibility scoring")
        st.markdown("- Keyword matching")
        st.markdown("- Formatting analysis")
    
    with col3:
        st.markdown("#### AI Recommendations")
        st.markdown("- Personalized feedback")
        st.markdown("- Improvement suggestions")
        st.markdown("- Industry-specific advice")
    
    st.markdown("---")
    st.markdown("### Getting Started")
    st.markdown("1. Navigate to **Upload & Analyze** to upload or paste your resume and job description")
    st.markdown("2. Review your **ATS Dashboard** for detailed scoring and insights with industry-specific keywords")
    st.markdown("3. Use the **Resume Editor** to edit your resume based on feedback and re-analyze")
    st.markdown("4. Chat with the **AI Advisor** for personalized improvement recommendations")
    st.markdown("5. **Compare** multiple resume versions to see which performs better")
    st.markdown("6. Download your **Reports** for future reference")

def show_upload_page(parser, analyzer):
    st.title("Upload & Analyze Resume")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Resume Input")
        
        # Option to choose between file upload or paste text
        resume_input_method = st.radio(
            "Choose how to input your resume:",
            ["Upload File", "Paste Text"],
            horizontal=True
        )
        
        if resume_input_method == "Upload File":
            resume_file = st.file_uploader(
                "Choose a resume file",
                type=['pdf', 'docx', 'txt'],
                help="Supported formats: PDF, DOCX, TXT"
            )
            
            if resume_file is not None:
                with st.spinner("Parsing resume..."):
                    resume_data = parser.parse_resume(resume_file)
                    st.session_state.resume_data = resume_data
                    
                if resume_data:
                    st.success("Resume parsed successfully!")
                    
                    # Display extracted information
                    with st.expander("Extracted Information", expanded=True):
                        if resume_data.get('name'):
                            st.write(f"**Name:** {resume_data['name']}")
                        if resume_data.get('email'):
                            st.write(f"**Email:** {resume_data['email']}")
                        if resume_data.get('phone'):
                            st.write(f"**Phone:** {resume_data['phone']}")
                        if resume_data.get('skills'):
                            st.write(f"**Skills:** {', '.join(resume_data['skills'])}")
                        if resume_data.get('experience_years'):
                            st.write(f"**Total Experience:** {resume_data['experience_years']} years")
        
        else:  # Paste Text
            resume_text = st.text_area(
                "Paste your resume text here:",
                height=300,
                help="Copy and paste your resume content here"
            )
            
            if resume_text:
                if st.button("Parse Resume Text", key="parse_resume_btn"):
                    with st.spinner("Parsing resume..."):
                        resume_data = parser.parse_text(resume_text)
                        st.session_state.resume_data = resume_data
                        
                    if resume_data:
                        st.success("Resume parsed successfully!")
                        
                        # Display extracted information
                        with st.expander("Extracted Information", expanded=True):
                            if resume_data.get('name'):
                                st.write(f"**Name:** {resume_data['name']}")
                            if resume_data.get('email'):
                                st.write(f"**Email:** {resume_data['email']}")
                            if resume_data.get('phone'):
                                st.write(f"**Phone:** {resume_data['phone']}")
                            if resume_data.get('skills'):
                                st.write(f"**Skills:** {', '.join(resume_data['skills'])}")
                            if resume_data.get('experience_years'):
                                st.write(f"**Total Experience:** {resume_data['experience_years']} years")
    
    with col2:
        st.subheader("Job Description")
        
        input_method = st.radio("Input method:", ["Paste Text", "Upload File"])
        
        if input_method == "Paste Text":
            job_desc_text = st.text_area(
                "Paste job description here:",
                height=300,
                help="Copy and paste the job description from the job posting"
            )
            if job_desc_text:
                st.session_state.job_description = parser.parse_job_description(job_desc_text)
        
        else:  # Upload File
            jd_file = st.file_uploader(
                "Upload job description file",
                type=['txt', 'pdf', 'docx'],
                help="Upload a file containing the job description"
            )
            if jd_file is not None:
                jd_text = parser.extract_text_from_file(jd_file)
                st.session_state.job_description = parser.parse_job_description(jd_text)
        
        if st.session_state.job_description:
            st.success("Job description processed!")
            with st.expander("Extracted Requirements", expanded=True):
                jd_data = st.session_state.job_description
                if jd_data.get('required_skills'):
                    st.write(f"**Required Skills:** {', '.join(jd_data['required_skills'])}")
                if jd_data.get('preferred_skills'):
                    st.write(f"**Preferred Skills:** {', '.join(jd_data['preferred_skills'])}")
                if jd_data.get('experience_required'):
                    st.write(f"**Experience Required:** {jd_data['experience_required']}")
    
    # Analysis section
    if st.session_state.resume_data and st.session_state.job_description:
        st.markdown("---")
        if st.button("Analyze Resume", type="primary"):
            with st.spinner("Analyzing resume against job description..."):
                analysis = analyzer.analyze_resume(
                    st.session_state.resume_data,
                    st.session_state.job_description
                )
                st.session_state.analysis_results = analysis
            
            if analysis:
                st.success("Analysis completed!")
                
                # Quick overview
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    score = analysis['ats_score']
                    color = get_score_color(score)
                    st.metric("ATS Score", f"{score}/100", delta=None)
                    st.markdown(f"<div style='color: {color}; font-weight: bold;'>{get_score_category(score)}</div>", unsafe_allow_html=True)
                
                with col2:
                    st.metric("Skill Match", f"{analysis['skill_match_percentage']:.1f}%")
                
                with col3:
                    st.metric("Missing Skills", len(analysis['missing_skills']))
                
                with col4:
                    st.metric("Format Score", f"{analysis['formatting_score']}/100")

def show_resume_editor_page(parser, analyzer):
    st.title("Resume Editor")
    st.markdown("Edit your resume based on analysis feedback and re-analyze it instantly.")
    
    if not st.session_state.resume_data:
        st.warning("Please upload and analyze a resume first before editing.")
        return
    
    # Initialize edited resume text in session state if not exists
    if 'edited_resume_text' not in st.session_state:
        st.session_state.edited_resume_text = st.session_state.resume_data.get('raw_text', '')
    
    # Show current analysis summary if available
    if st.session_state.analysis_results:
        st.subheader("Current Analysis Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            score = st.session_state.analysis_results['ats_score']
            color = get_score_color(score)
            st.metric("ATS Score", f"{score}/100")
        with col2:
            st.metric("Skill Match", f"{st.session_state.analysis_results['skill_match_percentage']:.1f}%")
        with col3:
            st.metric("Missing Skills", len(st.session_state.analysis_results.get('missing_skills', [])))
        
        # Show key recommendations
        st.markdown("**Key Areas to Improve:**")
        recommendations = st.session_state.analysis_results.get('recommendations', [])
        if recommendations:
            for rec in recommendations[:3]:
                st.markdown(f"- {rec}")
    
    st.markdown("---")
    
    # Two-column layout for editing
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("Edit Resume")
        
        # Editable text area with the resume content
        edited_text = st.text_area(
            "Resume Content:",
            value=st.session_state.edited_resume_text,
            height=400,
            help="Edit your resume text here. Make changes based on the recommendations."
        )
        
        st.session_state.edited_resume_text = edited_text
        
        # Action buttons
        btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 2])
        
        with btn_col1:
            if st.button("Reset to Original", help="Reset to the originally uploaded resume"):
                st.session_state.edited_resume_text = st.session_state.resume_data.get('raw_text', '')
                st.rerun()
        
        with btn_col2:
            if st.button("Re-Analyze", type="primary"):
                if st.session_state.job_description and edited_text:
                    with st.spinner("Re-analyzing updated resume..."):
                        # Parse the edited text as a new resume
                        updated_resume_data = parser.parse_text(edited_text)
                        
                        # Analyze against job description
                        new_analysis = analyzer.analyze_resume(
                            updated_resume_data,
                            st.session_state.job_description
                        )
                        
                        # Update session state
                        st.session_state.resume_data = updated_resume_data
                        st.session_state.analysis_results = new_analysis
                    
                    st.success("Resume re-analyzed successfully!")
                    st.rerun()
                else:
                    st.error("Please ensure you have a job description loaded before re-analyzing.")
    
    with col2:
        st.subheader("Editing Tips")
        
        if st.session_state.analysis_results:
            # Show missing skills
            missing_skills = st.session_state.analysis_results.get('missing_skills', [])
            if missing_skills:
                st.markdown("**Add these missing skills:**")
                for skill in missing_skills[:5]:
                    st.markdown(f"- {skill}")
            
            # Show formatting issues
            format_issues = st.session_state.analysis_results.get('formatting_issues', [])
            if format_issues:
                st.markdown("**Formatting suggestions:**")
                for issue in format_issues[:3]:
                    st.markdown(f"- {issue}")
            
            # General tips
            st.markdown("**General Tips:**")
            st.markdown("- Use action verbs (achieved, managed, led)")
            st.markdown("- Quantify achievements with numbers")
            st.markdown("- Use standard section headers")
            st.markdown("- Keep formatting simple and clean")
            st.markdown("- Include relevant keywords naturally")
        else:
            st.info("Analyze your resume first to get personalized editing tips.")
    
    # Show download option for edited resume
    if edited_text and edited_text != st.session_state.resume_data.get('raw_text', ''):
        st.markdown("---")
        st.subheader("Download Edited Resume")
        
        col1, col2 = st.columns(2)
        with col1:
            # Download as TXT
            st.download_button(
                label="Download as TXT",
                data=edited_text,
                file_name=f"edited_resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

def show_dashboard_page():
    st.title("ATS Analysis Dashboard")
    
    if not st.session_state.analysis_results:
        st.warning("No analysis results available. Please upload and analyze a resume first.")
        return
    
    results = st.session_state.analysis_results
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        score = results['ats_score']
        color = get_score_color(score)
        st.metric("Overall ATS Score", f"{score}/100")
        st.markdown(f"<div style='color: {color}; font-weight: bold; text-align: center;'>{get_score_category(score)}</div>", unsafe_allow_html=True)
    
    with col2:
        st.metric("Skill Match", f"{results['skill_match_percentage']:.1f}%")
    
    with col3:
        st.metric("Experience Relevance", f"{results['experience_relevance_score']}/100")
    
    with col4:
        st.metric("Education Alignment", f"{results['education_alignment_score']}/100")
    
    st.markdown("---")
    
    # Detailed analysis sections
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Skill Analysis")
        
        # Skill match chart
        if results.get('matched_skills') or results.get('missing_skills'):
            matched_count = len(results.get('matched_skills', []))
            missing_count = len(results.get('missing_skills', []))
            
            fig = go.Figure(data=[
                go.Bar(name='Matched Skills', x=['Skills'], y=[matched_count], marker_color='green'),
                go.Bar(name='Missing Skills', x=['Skills'], y=[missing_count], marker_color='red')
            ])
            fig.update_layout(title="Skill Match Overview", barmode='group', height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        # Missing skills
        if results.get('missing_skills'):
            st.subheader("Missing Skills")
            for skill in results['missing_skills']:
                st.markdown(f"- {skill}")
        
        # Extra skills
        if results.get('extra_skills'):
            st.subheader("Additional Skills (Advantage)")
            for skill in results['extra_skills']:
                st.markdown(f"+ {skill}")
    
    with col2:
        st.subheader("Keyword Analysis")
        
        # Keyword density chart
        if results.get('keyword_analysis'):
            keywords = results['keyword_analysis']
            
            fig = go.Figure(data=[
                go.Bar(
                    x=list(keywords.keys()),
                    y=list(keywords.values()),
                    marker_color='lightblue'
                )
            ])
            fig.update_layout(
                title="Keyword Frequency",
                xaxis_title="Keywords",
                yaxis_title="Frequency",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Formatting analysis
        st.subheader("Formatting Analysis")
        format_issues = results.get('formatting_issues', [])
        if format_issues:
            for issue in format_issues:
                st.markdown(f"⚠️ {issue}")
        else:
            st.markdown("✅ No major formatting issues detected")
    
    # Recommendations section
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Key Recommendations")
        recommendations = results.get('recommendations', [])
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f"{i}. {rec}")
        else:
            st.info("No specific recommendations available.")
    
    with col2:
        st.subheader("Industry-Specific Keywords")
        industry_keywords = results.get('industry_specific_keywords', {})
        detected_industry = results.get('detected_industry', 'general')
        
        if detected_industry != 'general':
            st.info(f"Detected Industry: **{industry_keywords.get('industry', 'General')}**")
            
            missing = industry_keywords.get('missing', [])
            present = industry_keywords.get('present', [])
            
            if missing:
                st.markdown("**Missing Industry Keywords:**")
                for keyword in missing[:5]:
                    st.markdown(f"- {keyword}")
            
            if present:
                st.markdown(f"**✅ You have {len(present)} industry-relevant keywords**")
        else:
            st.info("Add a job description to get industry-specific keyword suggestions.")

def show_chatbot_page(chatbot):
    st.title("AI Resume Advisor")
    st.markdown("Get personalized advice and ask questions about your resume analysis.")
    
    if not st.session_state.analysis_results:
        st.warning("Please analyze a resume first to get personalized advice.")
        return
    
    # Chat interface
    chat_container = st.container()
    
    # Display chat history
    with chat_container:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f"**You:** {message['content']}")
            else:
                st.markdown(f"**AI Advisor:** {message['content']}")
    
    # Chat input
    user_input = st.text_input(
        "Ask a question about your resume:",
        placeholder="e.g., How can I improve my ATS score?",
        key="chat_input"
    )
    
    if st.button("Send") and user_input:
        # Add user message to history
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_input
        })
        
        # Get AI response
        with st.spinner("AI is thinking..."):
            response = chatbot.get_response(
                user_input,
                st.session_state.analysis_results,
                st.session_state.resume_data,
                st.session_state.job_description
            )
        
        # Add AI response to history
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': response
        })
        
        # Clear input and rerun to show new messages
        st.rerun()
    
    # Quick action buttons
    st.markdown("---")
    st.markdown("**Quick Questions:**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("How to improve ATS score?"):
            quick_question = "How can I improve my ATS score based on my current analysis?"
            st.session_state.chat_history.append({'role': 'user', 'content': quick_question})
            with st.spinner("AI is thinking..."):
                response = chatbot.get_response(
                    quick_question,
                    st.session_state.analysis_results,
                    st.session_state.resume_data,
                    st.session_state.job_description
                )
            st.session_state.chat_history.append({'role': 'assistant', 'content': response})
            st.rerun()
    
    with col2:
        if st.button("Missing skills advice?"):
            quick_question = "What should I do about the missing skills identified in my resume?"
            st.session_state.chat_history.append({'role': 'user', 'content': quick_question})
            with st.spinner("AI is thinking..."):
                response = chatbot.get_response(
                    quick_question,
                    st.session_state.analysis_results,
                    st.session_state.resume_data,
                    st.session_state.job_description
                )
            st.session_state.chat_history.append({'role': 'assistant', 'content': response})
            st.rerun()
    
    with col3:
        if st.button("Format improvements?"):
            quick_question = "What formatting improvements should I make to my resume?"
            st.session_state.chat_history.append({'role': 'user', 'content': quick_question})
            with st.spinner("AI is thinking..."):
                response = chatbot.get_response(
                    quick_question,
                    st.session_state.analysis_results,
                    st.session_state.resume_data,
                    st.session_state.job_description
                )
            st.session_state.chat_history.append({'role': 'assistant', 'content': response})
            st.rerun()

def show_comparison_page(parser, analyzer):
    st.title("Resume Comparison")
    st.markdown("Compare multiple resumes or different versions of your resume.")
    
    # Upload multiple resumes
    st.subheader("Upload Resumes for Comparison")
    
    uploaded_files = st.file_uploader(
        "Choose resume files to compare",
        type=['pdf', 'docx', 'txt'],
        accept_multiple_files=True,
        help="Upload 2-5 resumes for comparison"
    )
    
    if len(uploaded_files) >= 2:
        # Job description for comparison
        jd_text = st.text_area(
            "Job Description (for comparison context):",
            height=150,
            help="Provide job description to compare resumes against"
        )
        
        if st.button("Compare Resumes") and jd_text:
            comparison_results = []
            
            with st.spinner("Analyzing all resumes..."):
                jd_data = parser.parse_job_description(jd_text)
                
                for i, file in enumerate(uploaded_files):
                    resume_data = parser.parse_resume(file)
                    if resume_data:
                        analysis = analyzer.analyze_resume(resume_data, jd_data)
                        comparison_results.append({
                            'filename': file.name,
                            'data': resume_data,
                            'analysis': analysis
                        })
            
            if comparison_results:
                st.success(f"Compared {len(comparison_results)} resumes successfully!")
                
                # Comparison table
                comparison_df = pd.DataFrame([
                    {
                        'Resume': result['filename'],
                        'ATS Score': result['analysis']['ats_score'],
                        'Skill Match %': f"{result['analysis']['skill_match_percentage']:.1f}%",
                        'Experience Score': result['analysis']['experience_relevance_score'],
                        'Format Score': result['analysis']['formatting_score'],
                        'Missing Skills': len(result['analysis']['missing_skills'])
                    }
                    for result in comparison_results
                ])
                
                st.subheader("Comparison Results")
                st.dataframe(comparison_df, use_container_width=True)
                
                # Visualization
                fig = go.Figure()
                
                for result in comparison_results:
                    fig.add_trace(go.Bar(
                        name=result['filename'][:20] + '...' if len(result['filename']) > 20 else result['filename'],
                        x=['ATS Score', 'Skill Match', 'Experience', 'Format'],
                        y=[
                            result['analysis']['ats_score'],
                            result['analysis']['skill_match_percentage'],
                            result['analysis']['experience_relevance_score'],
                            result['analysis']['formatting_score']
                        ]
                    ))
                
                fig.update_layout(
                    title="Resume Comparison Chart",
                    barmode='group',
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Best performing resume
                best_resume = max(comparison_results, key=lambda x: x['analysis']['ats_score'])
                st.subheader("Best Performing Resume")
                st.success(f"**{best_resume['filename']}** has the highest ATS score of {best_resume['analysis']['ats_score']}/100")

def show_reports_page(report_gen):
    st.title("Download Reports")
    
    if not st.session_state.analysis_results:
        st.warning("No analysis results available. Please analyze a resume first.")
        return
    
    st.markdown("Generate and download detailed reports of your resume analysis.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("ATS Compliance Report")
        st.markdown("Comprehensive PDF report including:")
        st.markdown("- ATS score and breakdown")
        st.markdown("- Skill gap analysis")
        st.markdown("- Keyword optimization suggestions")
        st.markdown("- Formatting recommendations")
        st.markdown("- Action items for improvement")
        
        if st.button("Generate PDF Report", type="primary"):
            with st.spinner("Generating PDF report..."):
                pdf_buffer = report_gen.generate_pdf_report(
                    st.session_state.resume_data,
                    st.session_state.job_description,
                    st.session_state.analysis_results
                )
            
            if pdf_buffer:
                st.download_button(
                    label="Download PDF Report",
                    data=pdf_buffer,
                    file_name=f"ATS_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
    
    with col2:
        st.subheader("Excel Analysis Data")
        st.markdown("Detailed data export including:")
        st.markdown("- Resume data extraction")
        st.markdown("- Job requirements analysis")
        st.markdown("- Skill matching details")
        st.markdown("- Keyword frequency data")
        st.markdown("- Recommendations list")
        
        if st.button("Generate Excel Report"):
            with st.spinner("Generating Excel report..."):
                excel_buffer = report_gen.generate_excel_report(
                    st.session_state.resume_data,
                    st.session_state.job_description,
                    st.session_state.analysis_results
                )
            
            if excel_buffer:
                st.download_button(
                    label="Download Excel Report",
                    data=excel_buffer,
                    file_name=f"ATS_Analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

def get_score_color(score):
    if score >= 80:
        return "green"
    elif score >= 60:
        return "orange"
    else:
        return "red"

def get_score_category(score):
    if score >= 80:
        return "High ATS Compatibility"
    elif score >= 60:
        return "Medium ATS Compatibility"
    else:
        return "Low ATS Compatibility"

if __name__ == "__main__":
    main()
