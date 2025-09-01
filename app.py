# import streamlit as st
# import pandas as pd
# import json
# import os
# from pathlib import Path
# import plotly.express as px
# import plotly.graph_objects as go
# from streamlit_option_menu import option_menu

# from resume_parser import ResumeParser
# from candidate_ranker import CandidateRanker

# # Page config
# st.set_page_config(
#     page_title="Resume Parser & Ranker",
#     page_icon="📄",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Custom CSS
# st.markdown("""
# <style>
#     .main-header {
#         font-size: 2.5rem;
#         font-weight: bold;
#         color: #1f77b4;
#         text-align: center;
#         margin-bottom: 2rem;
#     }
#     .metric-card {
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#         padding: 1rem;
#         border-radius: 10px;
#         color: white;
#         text-align: center;
#         margin: 0.5rem 0;
#     }
#     .candidate-card {
#         border: 1px solid #ddd;
#         border-radius: 10px;
#         padding: 1rem;
#         margin: 1rem 0;
#         background: #f8f9fa;
#     }
#     .top-candidate {
#         border: 2px solid #28a745;
#         background: #d4edda;
#     }
# </style>
# """, unsafe_allow_html=True)

# def initialize_session_state():
#     """Initialize session state variables"""
#     if 'parsed_resumes' not in st.session_state:
#         st.session_state.parsed_resumes = []
#     if 'job_description' not in st.session_state:
#         st.session_state.job_description = ""
#     if 'rankings' not in st.session_state:
#         st.session_state.rankings = []

# def main():
#     initialize_session_state()
    
#     # Header
#     st.markdown('<h1 class="main-header">🎯 AI Resume Parser & Candidate Ranker</h1>', unsafe_allow_html=True)
    
#     # Navigation
#     selected = option_menu(
#         menu_title=None,
#         options=["Upload & Parse", "View Results", "Candidate Ranking", "Analytics"],
#         icons=["cloud-upload", "table", "trophy", "bar-chart"],
#         menu_icon="cast",
#         default_index=0,
#         orientation="horizontal",
#         styles={
#             "container": {"padding": "0!important", "background-color": "#fafafa"},
#             "icon": {"color": "#1f77b4", "font-size": "18px"},
#             "nav-link": {"font-size": "16px", "text-align": "center", "margin": "0px", "--hover-color": "#eee"},
#             "nav-link-selected": {"background-color": "#1f77b4"},
#         }
#     )
    
#     if selected == "Upload & Parse":
#         upload_and_parse_page()
#     elif selected == "View Results":
#         view_results_page()
#     elif selected == "Candidate Ranking":
#         candidate_ranking_page()
#     elif selected == "Analytics":
#         analytics_page()

# def upload_and_parse_page():
#     st.header("📤 Upload and Parse Resumes")
    
#     col1, col2 = st.columns([2, 1])
    
#     with col1:
#         # File uploader
#         uploaded_files = st.file_uploader(
#             "Choose resume files",
#             type=['pdf', 'txt', 'docx'],
#             accept_multiple_files=True,
#             help="Upload PDF, TXT, or DOCX files"
#         )
        
#         if uploaded_files:
#             st.success(f"📁 {len(uploaded_files)} files uploaded successfully!")
            
#             # Model path configuration
#             model_path = st.text_input(
#                 "TinyLlama Model Path",
#                 value="D:/downloads/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
#                 help="Path to your TinyLlama .gguf model file"
#             )
            
#             if st.button("🚀 Parse Resumes", type="primary"):
#                 if not os.path.exists(model_path):
#                     st.error(f"❌ Model file not found at: {model_path}")
#                     return
                
#                 progress_bar = st.progress(0)
#                 status_text = st.empty()
                
#                 try:
#                     # Initialize parser
#                     parser = ResumeParser(model_path)
#                     parsed_resumes = []
                    
#                     for i, uploaded_file in enumerate(uploaded_files):
#                         status_text.text(f"Processing {uploaded_file.name}...")
#                         progress_bar.progress((i + 1) / len(uploaded_files))
                        
#                         # Save uploaded file temporarily
#                         temp_path = f"temp_{uploaded_file.name}"
#                         with open(temp_path, "wb") as f:
#                             f.write(uploaded_file.getbuffer())
                        
#                         # Parse resume
#                         result = parser.parse_resume(temp_path)
#                         result['filename'] = uploaded_file.name
#                         parsed_resumes.append(result)
                        
#                         # Clean up temp file
#                         os.remove(temp_path)
                    
#                     st.session_state.parsed_resumes = parsed_resumes
#                     status_text.text("✅ All resumes parsed successfully!")
#                     st.success(f"🎉 Successfully parsed {len(parsed_resumes)} resumes!")
                    
#                 except Exception as e:
#                     st.error(f"❌ Error during parsing: {str(e)}")
    
#     with col2:
#         st.info("""
#         ### 📋 Supported Formats
#         - **PDF**: Most common resume format
#         - **TXT**: Plain text resumes
#         - **DOCX**: Microsoft Word documents
        
#         ### 🔍 Extracted Fields
#         - Name & Contact Info
#         - Education Details
#         - Work Experience
#         - Skills & Technologies
#         - Certifications
#         - Summary/Objective
#         """)

# def view_results_page():
#     st.header("📊 Parsed Resume Results")
    
#     if not st.session_state.parsed_resumes:
#         st.warning("⚠️ No parsed resumes found. Please upload and parse resumes first.")
#         return
    
#     # Summary metrics
#     col1, col2, col3, col4 = st.columns(4)
    
#     with col1:
#         st.markdown(f"""
#         <div class="metric-card">
#             <h3>{len(st.session_state.parsed_resumes)}</h3>
#             <p>Total Resumes</p>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col2:
#         avg_experience = sum([len(resume.get('experience', [])) for resume in st.session_state.parsed_resumes]) / len(st.session_state.parsed_resumes)
#         st.markdown(f"""
#         <div class="metric-card">
#             <h3>{avg_experience:.1f}</h3>
#             <p>Avg Experience</p>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col3:
#         total_skills = sum([len(resume.get('skills', [])) for resume in st.session_state.parsed_resumes])
#         st.markdown(f"""
#         <div class="metric-card">
#             <h3>{total_skills}</h3>
#             <p>Total Skills</p>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with col4:
#         certified_count = sum([1 for resume in st.session_state.parsed_resumes if resume.get('certifications')])
#         st.markdown(f"""
#         <div class="metric-card">
#             <h3>{certified_count}</h3>
#             <p>With Certifications</p>
#         </div>
#         """, unsafe_allow_html=True)
    
#     # Detailed results
#     st.subheader("📋 Detailed Results")
    
#     for i, resume in enumerate(st.session_state.parsed_resumes):
#         with st.expander(f"📄 {resume.get('filename', f'Resume {i+1}')} - {resume.get('name', 'Unknown')}"):
#             col1, col2 = st.columns(2)
            
#             with col1:
#                 st.write("**📞 Contact Information:**")
#                 st.write(f"• Name: {resume.get('name', 'N/A')}")
#                 st.write(f"• Email: {resume.get('email', 'N/A')}")
#                 st.write(f"• Phone: {resume.get('phone', 'N/A')}")
#                 st.write(f"• LinkedIn: {resume.get('linkedin', 'N/A')}")
#                 st.write(f"• GitHub: {resume.get('github', 'N/A')}")
                
#                 st.write("**🎓 Education:**")
#                 for edu in resume.get('education', []):
#                     st.write(f"• {edu}")
                
#                 st.write("**📜 Certifications:**")
#                 for cert in resume.get('certifications', []):
#                     st.write(f"• {cert}")
            
#             with col2:
#                 st.write("**💼 Experience:**")
#                 for exp in resume.get('experience', []):
#                     st.write(f"• {exp}")
                
#                 st.write("**🛠️ Skills:**")
#                 skills_text = ", ".join(resume.get('skills', []))
#                 st.write(skills_text if skills_text else "N/A")
                
#                 st.write("**📝 Summary:**")
#                 st.write(resume.get('summary', 'N/A'))

# def candidate_ranking_page():
#     st.header("🏆 Candidate Ranking")
    
#     if not st.session_state.parsed_resumes:
#         st.warning("⚠️ No parsed resumes found. Please upload and parse resumes first.")
#         return
    
#     col1, col2 = st.columns([2, 1])
    
#     with col1:
#         # Job description input
#         job_description = st.text_area(
#             "📝 Job Description",
#             value=st.session_state.job_description,
#             height=200,
#             placeholder="Enter the job description to rank candidates against..."
#         )
#         st.session_state.job_description = job_description
        
#         if st.button("🎯 Rank Candidates", type="primary") and job_description:
#             with st.spinner("🤖 AI is analyzing candidates..."):
#                 try:
#                     ranker = CandidateRanker()
#                     rankings = ranker.rank_candidates(st.session_state.parsed_resumes, job_description)
#                     st.session_state.rankings = rankings
#                     st.success("✅ Ranking completed!")
#                 except Exception as e:
#                     st.error(f"❌ Error during ranking: {str(e)}")
    
#     with col2:
#         st.info("""
#         ### 🎯 Ranking Criteria
#         - **Skills Match**: Technical skills alignment
#         - **Experience**: Relevant work experience
#         - **Education**: Educational background fit
#         - **Keywords**: Job description keywords
#         - **Overall Fit**: Comprehensive assessment
#         """)
    
#     # Display rankings
#     if st.session_state.rankings:
#         st.subheader("📊 Candidate Rankings")
        
#         # Create ranking visualization
#         df_rankings = pd.DataFrame(st.session_state.rankings)
        
#         fig = px.bar(
#             df_rankings.head(10),
#             x='name',
#             y='',
#             title='Top 10 Candidates by Score',
#             color='score',
#             color_continuous_scale='viridis'
#         )
#         fig.update_layout(xaxis_tickangle=-45)
#         st.plotly_chart(fig, use_container_width=True)
        
#         # Display detailed rankings
#         for i, candidate in enumerate(st.session_state.rankings):
#             card_class = "candidate-card top-candidate" if i == 0 else "candidate-card"
            
#             st.markdown(f"""
#             <div class="{card_class}">
#                 <h4>#{i+1} {candidate['name']} {'🏆' if i == 0 else '🥈' if i == 1 else '🥉' if i == 2 else ''}</h4>
#                 <p><strong>Score:</strong> {candidate['score']:.2f}/100</p>
#                 <p><strong>Reasoning:</strong> {candidate['reasoning']}</p>
#             </div>
#             """, unsafe_allow_html=True)

# def analytics_page():
#     st.header("📈 Analytics Dashboard")
    
#     if not st.session_state.parsed_resumes:
#         st.warning("⚠️ No parsed resumes found. Please upload and parse resumes first.")
#         return
    
#     # Skills analysis
#     st.subheader("🛠️ Skills Analysis")
    
#     all_skills = []
#     for resume in st.session_state.parsed_resumes:
#         all_skills.extend(resume.get('skills', []))
    
#     if all_skills:
#         skills_df = pd.DataFrame({'skill': all_skills})
#         skill_counts = skills_df['skill'].value_counts().head(15)
        
#         fig_skills = px.bar(
#             x=skill_counts.values,
#             y=skill_counts.index,
#             orientation='h',
#             title='Most Common Skills',
#             labels={'x': 'Frequency', 'y': 'Skills'}
#         )
#         st.plotly_chart(fig_skills, use_container_width=True)
    
#     # Experience distribution
#     st.subheader("💼 Experience Distribution")
    
#     experience_counts = [len(resume.get('experience', [])) for resume in st.session_state.parsed_resumes]
    
#     fig_exp = px.histogram(
#         x=experience_counts,
#         nbins=10,
#         title='Distribution of Work Experience',
#         labels={'x': 'Number of Experiences', 'y': 'Number of Candidates'}
#     )
#     st.plotly_chart(fig_exp, use_container_width=True)
    
#     # Education analysis
#     st.subheader("🎓 Education Analysis")
    
#     education_data = []
#     for resume in st.session_state.parsed_resumes:
#         education_data.append({
#             'name': resume.get('name', 'Unknown'),
#             'education_count': len(resume.get('education', [])),
#             'has_certification': len(resume.get('certifications', [])) > 0
#         })
    
#     if education_data:
#         edu_df = pd.DataFrame(education_data)
        
#         col1, col2 = st.columns(2)
        
#         with col1:
#             fig_edu = px.pie(
#                 values=[edu_df['has_certification'].sum(), len(edu_df) - edu_df['has_certification'].sum()],
#                 names=['With Certifications', 'Without Certifications'],
#                 title='Certification Distribution'
#             )
#             st.plotly_chart(fig_edu, use_container_width=True)
        
#         with col2:
#             fig_edu_count = px.bar(
#                 edu_df,
#                 x='name',
#                 y='education_count',
#                 title='Education Count by Candidate'
#             )
#             fig_edu_count.update_layout(xaxis_tickangle=-45)
#             st.plotly_chart(fig_edu_count, use_container_width=True)

# if __name__ == "__main__":
#     main()















#working 


# app.py
# import os
# import json
# from pathlib import Path
# import tempfile
# import pandas as pd
# import streamlit as st
# import plotly.express as px
# from streamlit_option_menu import option_menu

# from resume_parser import ResumeParser
# from candidate_ranker import CandidateRanker

# st.set_page_config(page_title="Resume Parser & Ranker", page_icon="📄", layout="wide")

# # ---------------- UI helpers ---------------- #
# st.markdown("""
# <style>
# .metric-card{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:1rem;border-radius:10px;color:#fff;text-align:center}
# .candidate-card{border:1px solid #ddd;border-radius:10px;padding:1rem;margin:1rem 0;background:#f8f9fa}
# .top-candidate{border:2px solid #28a745;background:#d4edda}
# </style>
# """, unsafe_allow_html=True)

# def header():
#     st.markdown('<h1 style="text-align:center;margin:0 0 1rem 0">🎯 AI Resume Parser & Candidate Ranker</h1>', unsafe_allow_html=True)

# def metrics_box(title: str, value: str):
#     st.markdown(f'<div class="metric-card"><h3>{value}</h3><p>{title}</p></div>', unsafe_allow_html=True)

# # ---------------- Session ---------------- #
# if "parsed" not in st.session_state:
#     st.session_state.parsed = []
# if "rankings" not in st.session_state:
#     st.session_state.rankings = []
# if "jd_text" not in st.session_state:
#     st.session_state.jd_text = ""

# # ---------------- Nav ---------------- #
# header()
# selected = option_menu(
#     None,
#     ["Upload & Parse", "View Results", "Candidate Ranking"],
#     icons=["cloud-upload", "table", "trophy"],
#     orientation="horizontal",
#     default_index=0
# )

# # ---------------- Pages ---------------- #
# if selected == "Upload & Parse":
#     col1, col2 = st.columns([2,1])

#     with col1:
#         up = st.file_uploader(
#             "Upload resumes (PDF, DOCX, TXT, or ZIP folder)",
#             type=["pdf","docx","txt","zip"],
#             accept_multiple_files=True
#         )
#         model_path = st.text_input(
#             "Optional: Local LLaMA (.gguf) for extra parsing accuracy",
#             value=r"D:\downloads\tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
#             help="Leave as-is if you only want heuristic parsing. File must exist for LLM refinement."
#         )

#         if st.button("🚀 Parse Resumes", type="primary"):
#             if not up:
#                 st.warning("Upload at least one file.")
#             else:
#                 use_llm = os.path.exists(model_path)
#                 parser = ResumeParser(model_path=model_path if use_llm else None)
#                 results = []
#                 prog = st.progress(0.0)

#                 # collect all uploaded files
#                 all_files = []
#                 for uf in up:
#                     suffix = Path(uf.name).suffix.lower()

#                     if suffix == ".zip":
#                         # unzip into temp folder
#                         with tempfile.TemporaryDirectory() as tmpdir:
#                             zip_path = Path(tmpdir) / uf.name
#                             with open(zip_path, "wb") as f:
#                                 f.write(uf.getbuffer())

#                             import zipfile
#                             with zipfile.ZipFile(zip_path, "r") as zip_ref:
#                                 zip_ref.extractall(tmpdir)

#                             # collect resumes
#                             for f in Path(tmpdir).rglob("*"):
#                                 if f.suffix.lower() in [".pdf", ".docx", ".txt"]:
#                                     all_files.append(f)
#                     else:
#                         with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
#                             tmp.write(uf.getbuffer())
#                             all_files.append(Path(tmp.name))

#                 # helper to shorten JSON
#                 def shorten_resume_json(parsed: dict) -> dict:
#                     return {
#                         "name": parsed.get("name"),
#                         "email": parsed.get("email"),
#                         "phone": parsed.get("phone"),
#                         "linkedin": parsed.get("linkedin"),
#                         "github": parsed.get("github"),
#                         "education": parsed.get("education")[0] if parsed.get("education") else None,
#                         "summary": parsed.get("summary"),
#                         "skills": parsed.get("skills")[:5] if parsed.get("skills") else [],
#                         "total_experience": parsed.get("total_experience_years"),
#                         "filename": parsed.get("filename")
#                     }

#                 # parse all collected resumes
#                 for i, fpath in enumerate(all_files):
#                     parsed = parser.parse_resume(str(fpath))
#                     parsed["filename"] = fpath.name

#                     short_json = shorten_resume_json(parsed)
#                     results.append(short_json)

#                     try:
#                         os.unlink(fpath)
#                     except Exception:
#                         pass

#                     prog.progress((i+1)/len(all_files))

#                 st.session_state.parsed = results
#                 st.success(f"Parsed {len(results)} resumes ✅")

#     with col2:
#         st.info("""
#         **What gets extracted**
#         - Name, Email, Phone, LinkedIn, GitHub  
#         - Education (only highest), Skills (top 5), Summary  
#         - Estimated Total Experience (years)  

#         **Tip:** You can upload resumes individually **or** upload a folder as `.zip` (auto-unzipped).
#         """)


# # ---------------- View Results ---------------- #
# if selected == "View Results":
#     st.header("📂 Parsed Resume Results")

#     if not st.session_state.parsed:
#         st.warning("No resumes parsed yet. Please upload and parse resumes first.")
#     else:
#         results = st.session_state.parsed

#         for res in results:
#             st.subheader(res.get("filename", "Unnamed Resume"))

#             st.write(f"**Name:** {res.get('name', 'N/A')}")
#             st.write(f"**Email:** {res.get('email', 'N/A')}")
#             st.write(f"**Phone:** {res.get('phone', 'N/A')}")
#             st.write(f"**Experience (Years):** {res.get('total_experience', 'N/A')}")
#             st.write(f"**Top Skills:** {', '.join(res.get('skills', [])) if res.get('skills') else 'N/A'}")

#             with st.expander("🔎 Full JSON"):
#                 st.json(res)

#             st.markdown("---")

#         # Bulk download
#         json_export = json.dumps(results, indent=2)
#         st.download_button(
#             "💾 Download All Results (JSON)",
#             json_export,
#             "parsed_resumes.json",
#             "application/json"
#         )

# elif selected == "Candidate Ranking":
#     st.header("🏆 Candidate Ranking")

#     # Option 1: Upload JD
#     jd_file = st.file_uploader("📂 Upload Job Description (txt/pdf)", type=["txt", "pdf"], key="jd_upload")

#     # Option 2: Manual JD input
#     jd_text_manual = st.text_area("✍️ Or paste the Job Description here", placeholder="Paste JD here...")

#     jd_text = None
#     if jd_file is not None:
#         if jd_file.name.endswith(".pdf"):
#             jd_text = parser.extract_text_from_pdf(jd_file)
#         else:
#             jd_text = jd_file.read().decode("utf-8")
#         st.success("✅ Job Description uploaded!")
#     elif jd_text_manual.strip():
#         jd_text = jd_text_manual
#         st.success("✅ Job Description entered manually!")

#     if jd_text:
#         if "parsed" in st.session_state:
#             resumes = st.session_state.parsed

#             # Rank candidates
#             ranker = CandidateRanker()
#             ranked = ranker.rank_candidates(resumes, jd_text)

#             # Show clean ranking table
#             st.subheader("📊 Candidate Rankings")
#             for i, r in enumerate(ranked, 1):
#                 score = r.get("score", 0)

#                 if score == 0:
#                     st.markdown(f"### {i}. {r['name']} — ❌ Not Matched")
#                 else:
#                     st.markdown(f"### {i}. {r['name']} — {score}%")

#                 st.markdown("---")
#         else:
#             st.warning("⚠️ Please upload resumes first.")
#     else:
#         st.info("📂 Upload a JD file or paste it above to rank candidates.")






# # app.py
# import os
# import json
# from pathlib import Path
# import tempfile
# import pandas as pd
# import streamlit as st
# import plotly.express as px
# from streamlit_option_menu import option_menu

# from resume_parser import ResumeParser
# from candidate_ranker import CandidateRanker

# st.set_page_config(page_title="Resume Parser & Ranker", page_icon="📄", layout="wide")

# # ---------------- UI helpers ---------------- #
# st.markdown("""
# <style>
# .metric-card{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:1rem;border-radius:10px;color:#fff;text-align:center}
# .candidate-card{border:1px solid #ddd;border-radius:10px;padding:1rem;margin:1rem 0;background:#f8f9fa}
# .top-candidate{border:2px solid #28a745;background:#d4edda}
# </style>
# """, unsafe_allow_html=True)

# def header():
#     st.markdown('<h1 style="text-align:center;margin:0 0 1rem 0">🎯 AI Resume Parser & Candidate Ranker</h1>', unsafe_allow_html=True)

# def metrics_box(title: str, value: str):
#     st.markdown(f'<div class="metric-card"><h3>{value}</h3><p>{title}</p></div>', unsafe_allow_html=True)

# # ---------------- Session ---------------- #
# if "parsed" not in st.session_state:
#     st.session_state.parsed = []
# if "rankings" not in st.session_state:
#     st.session_state.rankings = []
# if "jd_text" not in st.session_state:
#     st.session_state.jd_text = ""

# # ---------------- Nav ---------------- #
# header()
# selected = option_menu(
#     None,
#     ["Upload & Parse", "View Results", "Candidate Ranking"],
#     icons=["cloud-upload", "table", "trophy"],
#     orientation="horizontal",
#     default_index=0
# )

# # ---------------- Pages ---------------- #
# if selected == "Upload & Parse":
#     col1, col2 = st.columns([2,1])

#     with col1:
#         up = st.file_uploader(
#             "Upload resumes (PDF, DOCX, TXT, or ZIP folder)",
#             type=["pdf","docx","txt","zip"],
#             accept_multiple_files=True
#         )
#         model_path = st.text_input(
#             "Optional: Local LLaMA (.gguf) for extra parsing accuracy",
#             value=r"D:\downloads\tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
#             help="Leave as-is if you only want heuristic parsing. File must exist for LLM refinement."
#         )

#         if st.button("🚀 Parse Resumes", type="primary"):
#             if not up:
#                 st.warning("Upload at least one file.")
#             else:
#                 use_llm = os.path.exists(model_path)
#                 parser = ResumeParser(model_path=model_path if use_llm else None)
#                 results = []
#                 prog = st.progress(0.0)

#                 # collect all uploaded files
#                 all_files = []
#                 for uf in up:
#                     suffix = Path(uf.name).suffix.lower()

#                     if suffix == ".zip":
#                         # unzip into temp folder
#                         with tempfile.TemporaryDirectory() as tmpdir:
#                             zip_path = Path(tmpdir) / uf.name
#                             with open(zip_path, "wb") as f:
#                                 f.write(uf.getbuffer())

#                             import zipfile
#                             with zipfile.ZipFile(zip_path, "r") as zip_ref:
#                                 zip_ref.extractall(tmpdir)

#                             # collect resumes
#                             for f in Path(tmpdir).rglob("*"):
#                                 if f.suffix.lower() in [".pdf", ".docx", ".txt"]:
#                                     all_files.append(f)
#                     else:
#                         with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
#                             tmp.write(uf.getbuffer())
#                             all_files.append(Path(tmp.name))

#                 # helper to shorten JSON
#                 def shorten_resume_json(parsed: dict) -> dict:
#                     return {
#                         "name": parsed.get("name"),
#                         "email": parsed.get("email"),
#                         "phone": parsed.get("phone"),
#                         "linkedin": parsed.get("linkedin"),
#                         "github": parsed.get("github"),
#                         "education": parsed.get("education")[0] if parsed.get("education") else None,
#                         "summary": parsed.get("summary"),
#                         "skills": parsed.get("skills")[:5] if parsed.get("skills") else [],
#                         "total_experience": parsed.get("total_experience_years"),
#                         "filename": parsed.get("filename")
#                     }

#                 # parse all collected resumes
#                 for i, fpath in enumerate(all_files):
#                     parsed = parser.parse_resume(str(fpath))
#                     parsed["filename"] = fpath.name

#                     short_json = shorten_resume_json(parsed)
#                     results.append(short_json)

#                     try:
#                         os.unlink(fpath)
#                     except Exception:
#                         pass

#                     prog.progress((i+1)/len(all_files))

#                 st.session_state.parsed = results
#                 st.success(f"Parsed {len(results)} resumes ✅")

#     with col2:
#         st.info("""
#         **What gets extracted**
#         - Name, Email, Phone, LinkedIn, GitHub  
#         - Education (only highest), Skills (top 5), Summary  
#         - Estimated Total Experience (years)  

#         **Tip:** You can upload resumes individually **or** upload a folder as `.zip` (auto-unzipped).
#         """)

# # ---------------- View Results ---------------- #
# if selected == "View Results":
#     st.header("📂 Parsed Resume Results")

#     if not st.session_state.parsed:
#         st.warning("No resumes parsed yet. Please upload and parse resumes first.")
#     else:
#         results = st.session_state.parsed

#         for res in results:
#             st.subheader(res.get("filename", "Unnamed Resume"))

#             st.write(f"**Name:** {res.get('name', 'N/A')}")
#             st.write(f"**Email:** {res.get('email', 'N/A')}")
#             st.write(f"**Phone:** {res.get('phone', 'N/A')}")
#             st.write(f"**Experience (Years):** {res.get('total_experience', 'N/A')}")

#             # Handle skills being dicts
#             skills = res.get('skills', [])
#             if skills and isinstance(skills[0], dict):
#                 skills = [s.get('name','') for s in skills]
#             st.write(f"**Top Skills:** {', '.join(skills) if skills else 'N/A'}")

#             with st.expander("🔎 Full JSON"):
#                 st.json(res)

#             st.markdown("---")

#         # Bulk download
#         json_export = json.dumps(results, indent=2)
#         st.download_button(
#             "💾 Download All Results (JSON)",
#             json_export,
#             "parsed_resumes.json",
#             "application/json"
#         )

# # ---------------- Candidate Ranking ---------------- #
# elif selected == "Candidate Ranking":
#     st.header("🏆 Candidate Ranking")

#     # Option 1: Upload JD
#     jd_file = st.file_uploader("📂 Upload Job Description (txt/pdf)", type=["txt", "pdf"], key="jd_upload")

#     # Option 2: Manual JD input
#     jd_text_manual = st.text_area("✍️ Or paste the Job Description here", placeholder="Paste JD here...")

#     jd_text = None
#     if jd_file is not None:
#         if jd_file.name.endswith(".pdf"):
#             parser = ResumeParser()  # ensure parser exists
#             jd_text = parser.extract_text_from_pdf(jd_file)
#         else:
#             jd_text = jd_file.read().decode("utf-8")
#         st.success("✅ Job Description uploaded!")
#     elif jd_text_manual.strip():
#         jd_text = jd_text_manual
#         st.success("✅ Job Description entered manually!")

#     if jd_text:
#         if "parsed" in st.session_state and st.session_state.parsed:
#             resumes = st.session_state.parsed

#             # ---------------- Ranking Logic ---------------- #
#             def calculate_weighted_score(resume: dict, jd_text: str):
#                 jd_lower = jd_text.lower()

#                 # Education match: weight 40%
#                 education_score = 0
#                 if resume.get("education"):
#                     edu_keywords = resume["education"].lower().split()
#                     matched_edu = sum(1 for kw in edu_keywords if kw in jd_lower)
#                     education_score = min(matched_edu / len(edu_keywords), 1) * 40

#                 # Skills match: weight 60%
#                 skills_score = 0
#                 skills_list = resume.get('skills', [])
#                 if skills_list:
#                     # handle dict skills
#                     if isinstance(skills_list[0], dict):
#                         skills_list = [s.get('name','') for s in skills_list]
#                     skill_keywords = [s.lower() for s in skills_list]
#                     matched_skills = sum(1 for skill in skill_keywords if skill in jd_lower)
#                     skills_score = min(matched_skills / len(skill_keywords), 1) * 60

#                 total_score = round(education_score + skills_score, 2)
#                 return total_score

#             # Rank candidates
#             ranked = []
#             for res in resumes:
#                 score = calculate_weighted_score(res, jd_text)
#                 res_copy = res.copy()
#                 res_copy["score"] = score
#                 ranked.append(res_copy)

#             ranked.sort(key=lambda x: x["score"], reverse=True)

#             # Display rankings
#             st.subheader("📊 Candidate Rankings")
#             for i, r in enumerate(ranked, 1):
#                 score = r.get("score", 0)

#                 # Handle skills dicts
#                 skills = r.get('skills', [])
#                 if skills and isinstance(skills[0], dict):
#                     skills = [s.get('name','') for s in skills]

#                 card_class = "top-candidate" if score > 0 else ""
#                 with st.container():
#                     st.markdown(f'<div class="candidate-card {card_class}">', unsafe_allow_html=True)
#                     st.markdown(f"### {i}. {r.get('name','N/A')} — **Score:** {score}%")
#                     st.write(f"**Email:** {r.get('email','N/A')}")
#                     st.write(f"**Phone:** {r.get('phone','N/A')}")
#                     st.write(f"**Education:** {r.get('education','N/A')}")
#                     st.write(f"**Top Skills:** {', '.join(skills) if skills else 'N/A'}")
#                     st.markdown("</div>", unsafe_allow_html=True)
#                     st.markdown("---")
#         else:
#             st.warning("⚠️ Please upload resumes first.")
#     else:
#         st.info("📂 Upload a JD file or paste it above to rank candidates.")



# #  ......app.py.......


# import os
# import json
# from pathlib import Path
# import tempfile
# import pandas as pd
# import streamlit as st
# from streamlit_option_menu import option_menu

# from resume_parser import ResumeParser
# from candidate_ranker import CandidateRanker

# st.set_page_config(page_title="Resume Parser & Ranker", page_icon="📄", layout="wide")

# # ---------------- UI helpers ---------------- #
# st.markdown("""
# <style>
# .metric-card{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:1rem;border-radius:10px;color:#fff;text-align:center}
# .candidate-card{border:1px solid #ddd;border-radius:10px;padding:1rem;margin:1rem 0;background:#f8f9fa}
# .top-candidate{border:2px solid #28a745;background:#d4edda}
# </style>
# """, unsafe_allow_html=True)

# def header():
#     st.markdown('<h1 style="text-align:center;margin:0 0 1rem 0">🎯 AI Resume Parser & Candidate Ranker</h1>', unsafe_allow_html=True)

# def metrics_box(title: str, value: str):
#     st.markdown(f'<div class="metric-card"><h3>{value}</h3><p>{title}</p></div>', unsafe_allow_html=True)

# # ---------------- Session ---------------- #
# if "parsed" not in st.session_state:
#     st.session_state.parsed = []
# if "rankings" not in st.session_state:
#     st.session_state.rankings = []
# if "jd_text" not in st.session_state:
#     st.session_state.jd_text = ""

# # ---------------- Nav ---------------- #
# header()
# selected = option_menu(
#     None,
#     ["Upload & Parse", "View Results", "Candidate Ranking"],
#     icons=["cloud-upload", "table", "trophy"],
#     orientation="horizontal",
#     default_index=0
# )

# # ---------------- Pages ---------------- #
# if selected == "Upload & Parse":
#     col1, col2 = st.columns([2,1])

#     with col1:
#         up = st.file_uploader(
#             "Upload resumes (PDF, DOCX, TXT, or ZIP folder)",
#             type=["pdf","docx","txt","zip"],
#             accept_multiple_files=True
#         )
#         model_path = st.text_input(
#             "Optional: Local LLaMA (.gguf) for extra parsing accuracy",
#             value=r"D:\downloads\tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
#             help="Leave as-is if you only want heuristic parsing. File must exist for LLM refinement."
#         )

#         if st.button("🚀 Parse Resumes", type="primary"):
#             if not up:
#                 st.warning("Upload at least one file.")
#             else:
#                 use_llm = os.path.exists(model_path)
#                 parser = ResumeParser(model_path=model_path if use_llm else None)
#                 results = []
#                 prog = st.progress(0.0)

#                 # collect all uploaded files
#                 all_files = []
#                 for uf in up:
#                     suffix = Path(uf.name).suffix.lower()

#                     if suffix == ".zip":
#                         # unzip into temp folder
#                         with tempfile.TemporaryDirectory() as tmpdir:
#                             zip_path = Path(tmpdir) / uf.name
#                             with open(zip_path, "wb") as f:
#                                 f.write(uf.getbuffer())

#                             import zipfile
#                             with zipfile.ZipFile(zip_path, "r") as zip_ref:
#                                 zip_ref.extractall(tmpdir)

#                             # collect resumes
#                             for f in Path(tmpdir).rglob("*"):
#                                 if f.suffix.lower() in [".pdf", ".docx", ".txt"]:
#                                     all_files.append(f)
#                     else:
#                         with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
#                             tmp.write(uf.getbuffer())
#                             all_files.append(Path(tmp.name))

#                 # helper to shorten JSON
#                 def shorten_resume_json(parsed: dict) -> dict:
#                     return {
#                         "name": parsed.get("name"),
#                         "email": parsed.get("email"),
#                         "phone": parsed.get("phone"),
#                         "linkedin": parsed.get("linkedin"),
#                         "github": parsed.get("github"),
#                         "education": parsed.get("education")[0] if parsed.get("education") else None,
#                         "summary": parsed.get("summary"),
#                         "skills": parsed.get("skills")[:5] if parsed.get("skills") else [],
#                         "projects": parsed.get("projects")[:5] if parsed.get("projects") else [],
#                         "total_experience": parsed.get("total_experience_years"),
#                         "filename": parsed.get("filename")
#                     }

#                 # parse all collected resumes
#                 for i, fpath in enumerate(all_files):
#                     parsed = parser.parse_resume(str(fpath))
#                     parsed["filename"] = fpath.name

#                     short_json = shorten_resume_json(parsed)
#                     results.append(short_json)

#                     try:
#                         os.unlink(fpath)
#                     except Exception:
#                         pass

#                     prog.progress((i+1)/len(all_files))

#                 st.session_state.parsed = results
#                 st.success(f"Parsed {len(results)} resumes ✅")

#     with col2:
#         st.info("""
#         **What gets extracted**
#         - Name, Email, Phone, LinkedIn, GitHub  
#         - Education (only highest), Skills (top 5), Projects (top 5), Summary  
#         - Estimated Total Experience (years)  

#         **Tip:** You can upload resumes individually **or** upload a folder as `.zip` (auto-unzipped).
#         """)

# # ---------------- View Results ---------------- #
# if selected == "View Results":
#     st.header("📂 Parsed Resume Results")

#     if not st.session_state.parsed:
#         st.warning("No resumes parsed yet. Please upload and parse resumes first.")
#     else:
#         results = st.session_state.parsed

#         for res in results:
#             st.subheader(res.get("filename", "Unnamed Resume"))

#             st.write(f"**Name:** {res.get('name', 'N/A')}")
#             st.write(f"**Email:** {res.get('email', 'N/A')}")
#             st.write(f"**Phone:** {res.get('phone', 'N/A')}")
#             st.write(f"**Experience (Years):** {res.get('total_experience', 'N/A')}")

#             # Handle skills and projects being dicts
#             skills = res.get('skills', [])
#             if skills and isinstance(skills[0], dict):
#                 skills = [s.get('name','') for s in skills]
#             projects = res.get('projects', [])
#             if projects and isinstance(projects[0], dict):
#                 projects = [p.get('name','') for p in projects]

#             st.write(f"**Top Skills:** {', '.join(skills) if skills else 'N/A'}")
#             st.write(f"**Projects:** {', '.join(projects) if projects else 'N/A'}")

#             with st.expander("🔎 Full JSON"):
#                 st.json(res)

#             st.markdown("---")

#         # Bulk download
#         json_export = json.dumps(results, indent=2)
#         st.download_button(
#             "💾 Download All Results (JSON)",
#             json_export,
#             "parsed_resumes.json",
#             "application/json"
#         )

# # ---------------- Candidate Ranking ---------------- #
# elif selected == "Candidate Ranking":
#     st.header("🏆 Candidate Ranking")

#     jd_file = st.file_uploader("📂 Upload Job Description (txt/pdf)", type=["txt", "pdf"], key="jd_upload")
#     jd_text_manual = st.text_area("✍️ Or paste the Job Description here", placeholder="Paste JD here...")

#     jd_text = None
#     if jd_file:
#         if jd_file.name.endswith(".pdf"):
#             parser = ResumeParser()
#             jd_text = parser.extract_text_from_pdf(jd_file)
#         else:
#             jd_text = jd_file.read().decode("utf-8")
#         st.success("✅ Job Description uploaded!")
#     elif jd_text_manual.strip():
#         jd_text = jd_text_manual
#         st.success("✅ Job Description entered manually!")

#     if jd_text:
#         if "parsed" in st.session_state and st.session_state.parsed:
#             resumes = st.session_state.parsed

#             # ---------- Sliders for weights ----------
#             st.subheader("⚖️ Adjust Weights for Scoring (0–10)")
#             col1, col2, col3 = st.columns(3)
#             with col1:
#                 weight_skills = st.slider("Skills Weight", 0, 10, 6)
#             with col2:
#                 weight_education = st.slider("Education Weight", 0, 10, 3)
#             with col3:
#                 weight_projects = st.slider("Projects Weight", 0, 10, 1)

#             # normalize weights to 100
#             total_slider = weight_skills + weight_education + weight_projects
#             if total_slider == 0:
#                 st.warning("⚠️ At least one weight must be > 0.")
#                 total_slider = 1
#             w_skills = (weight_skills / total_slider) * 100
#             w_education = (weight_education / total_slider) * 100
#             w_projects = (weight_projects / total_slider) * 100

#             # ---------- Compute weighted score ----------
#             def calculate_weighted_score(resume: dict, jd_text: str):
#                 jd_lower = jd_text.lower()

#                 # Skills
#                 skills_score = 0
#                 skills_list = resume.get('skills', [])
#                 if skills_list:
#                     if isinstance(skills_list[0], dict):
#                         skills_list = [s.get('name','') for s in skills_list]
#                     skill_keywords = [s.lower() for s in skills_list]
#                     matched_skills = sum(1 for skill in skill_keywords if skill in jd_lower)
#                     skills_score = min(matched_skills / len(skill_keywords), 1) * w_skills

#                 # Education
#                 education_score = 0
#                 if resume.get('education'):
#                     edu_keywords = resume['education'].lower().split()
#                     matched_edu = sum(1 for kw in edu_keywords if kw in jd_lower)
#                     education_score = min(matched_edu / len(edu_keywords), 1) * w_education

#                 # Projects
#                 projects_score = 0
#                 projects_list = resume.get('projects', [])
#                 if projects_list:
#                     if isinstance(projects_list[0], dict):
#                         projects_list = [p.get('name','') for p in projects_list]
#                     project_keywords = [p.lower() for p in projects_list]
#                     matched_projects = sum(1 for p in project_keywords if p in jd_lower)
#                     projects_score = min(matched_projects / len(project_keywords), 1) * w_projects

#                 total_score = round(skills_score + education_score + projects_score, 2)
#                 return total_score

#             # Rank candidates
#             ranked = []
#             for res in resumes:
#                 score = calculate_weighted_score(res, jd_text)
#                 res_copy = res.copy()
#                 res_copy["score"] = score
#                 ranked.append(res_copy)

#             ranked.sort(key=lambda x: x["score"], reverse=True)

#             # ---------- Tabular display ----------
#             st.subheader("📊 Candidate Ranking Table")
#             table_data = []
#             for i, r in enumerate(ranked, 1):
#                 skills = r.get('skills', [])
#                 if skills and isinstance(skills[0], dict):
#                     skills = [s.get('name','') for s in skills]
#                 projects = r.get('projects', [])
#                 if projects and isinstance(projects[0], dict):
#                     projects = [p.get('name','') for p in projects]

#                 table_data.append({
#                     "Rank": i,
#                     "Name": r.get("name", "N/A"),
#                     "Email": r.get("email", "N/A"),
#                     "Phone": r.get("phone", "N/A"),
#                     "Education": r.get("education", "N/A"),
#                     "Top Skills": ", ".join(skills) if skills else "N/A",
#                     "Projects": ", ".join(projects) if projects else "N/A",
#                     "Weighted Score": r.get("score", 0)
#                 })

#             df = pd.DataFrame(table_data)
#             st.dataframe(df)
#         else:
#             st.warning("⚠️ Please upload resumes first.")
#     else:
#         st.info("📂 Upload a JD file or paste it above to rank candidates.")




# testing
import os
import json
import re
from pathlib import Path
import tempfile
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu

from resume_parser import ResumeParser

st.set_page_config(page_title="Resume Parser & Ranker", page_icon="📄", layout="wide")

# ---------------- UI helpers ---------------- #
st.markdown("""
<style>
.metric-card{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:1rem;border-radius:10px;color:#fff;text-align:center}
.candidate-card{border:1px solid #ddd;border-radius:10px;padding:1rem;margin:1rem 0;background:#f8f9fa}
.top-candidate{border:2px solid #28a745;background:#d4edda}
.low-match{border:2px solid #ff4b4b;background:#ffe6e6}
</style>
""", unsafe_allow_html=True)

def header():
    st.markdown('<h1 style="text-align:center;margin:0 0 1rem 0">🎯 AI Resume Parser & Candidate Ranker</h1>', unsafe_allow_html=True)

def metrics_box(title: str, value: str):
    st.markdown(f'<div class="metric-card"><h3>{value}</h3><p>{title}</p></div>', unsafe_allow_html=True)

# ---------------- Session ---------------- #
if "parsed" not in st.session_state:
    st.session_state.parsed = []
if "rankings" not in st.session_state:
    st.session_state.rankings = []
if "jd_text" not in st.session_state:
    st.session_state.jd_text = ""

# ---------------- Nav ---------------- #
header()
selected = option_menu(
    None,
    ["Upload & Parse", "View Results", "Candidate Ranking"],
    icons=["cloud-upload", "table", "trophy"],
    orientation="horizontal",
    default_index=0
)

# ---------------- Pages ---------------- #
if selected == "Upload & Parse":
    col1, col2 = st.columns([2,1])

    with col1:
        up = st.file_uploader(
            "Upload resumes (PDF, DOCX, TXT, or ZIP folder)",
            type=["pdf","docx","txt","zip"],
            accept_multiple_files=True
        )
        model_path = st.text_input(
            "Optional: Local LLaMA (.gguf) for extra parsing accuracy",
            value=r"D:\downloads\tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
            help="Leave as-is if you only want heuristic parsing. File must exist for LLM refinement."
        )

        if st.button("🚀 Parse Resumes", type="primary"):
            if not up:
                st.warning("Upload at least one file.")
            else:
                use_llm = os.path.exists(model_path)
                parser = ResumeParser(model_path=model_path if use_llm else None)
                results = []
                prog = st.progress(0.0)

                # collect all uploaded files with their original names
                all_files = []  # This will store tuples: (temp_path, original_filename)
                for uf in up:
                    suffix = Path(uf.name).suffix.lower()
                    original_filename = uf.name

                    if suffix == ".zip":
                        # unzip into temp folder
                        with tempfile.TemporaryDirectory() as tmpdir:
                            zip_path = Path(tmpdir) / uf.name
                            with open(zip_path, "wb") as f:
                                f.write(uf.getbuffer())

                            import zipfile
                            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                                zip_ref.extractall(tmpdir)

                            # collect resumes with their original names
                            for f in Path(tmpdir).rglob("*"):
                                if f.suffix.lower() in [".pdf", ".docx", ".txt"]:
                                    all_files.append((f, f.name))  # Store both path and original name
                    else:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                            tmp.write(uf.getbuffer())
                            tmp_path = Path(tmp.name)
                            all_files.append((tmp_path, original_filename))  # Store original filename

                # helper to shorten JSON
                def shorten_resume_json(parsed: dict) -> dict:
                    return {
                        "name": parsed.get("name"),
                        "email": parsed.get("email"),
                        "phone": parsed.get("phone"),
                        "linkedin": parsed.get("linkedin"),
                        "github": parsed.get("github"),
                        "education": parsed.get("education")[0] if parsed.get("education") and parsed.get("education") != ["Not Available"] else None,
                        "summary": parsed.get("summary"),
                        "skills": parsed.get("skills")[:5] if parsed.get("skills") and parsed.get("skills") != ["Not Available"] else [],
                        "projects": parsed.get("projects")[:5] if parsed.get("projects") and parsed.get("projects") != ["Not Available"] else [],
                        "total_experience": parsed.get("total_experience_years"),
                        "filename": parsed.get("filename")
                    }

                # parse all collected resumes
                for i, (fpath, original_filename) in enumerate(all_files):
                    parsed = parser.parse_resume(str(fpath))
                    parsed["filename"] = original_filename  # Use the original filename instead of temp name

                    short_json = shorten_resume_json(parsed)
                    results.append(short_json)

                    try:
                        os.unlink(fpath)
                    except Exception:
                        pass

                    prog.progress((i+1)/len(all_files))

                st.session_state.parsed = results
                st.success(f"Parsed {len(results)} resumes ✅")

    with col2:
        st.info("""
        **What gets extracted**
        - Name, Email, Phone, LinkedIn, GitHub  
        - Education (only highest), Skills (top 5), Projects (top 5), Summary  
        - Estimated Total Experience (years)  

        **Tip:** You can upload resumes individually **or** upload a folder as `.zip` (auto-unzipped).
        """)

# ---------------- View Results ---------------- #
if selected == "View Results":
    st.header("📂 Parsed Resume Results")

    if not st.session_state.parsed:
        st.warning("No resumes parsed yet. Please upload and parse resumes first.")
    else:
        results = st.session_state.parsed

        for res in results:
            st.subheader(res.get("filename", "Unnamed Resume"))

            st.write(f"**Name:** {res.get('name', 'N/A')}")
            st.write(f"**Email:** {res.get('email', 'N/A')}")
            st.write(f"**Phone:** {res.get('phone', 'N/A')}")
            st.write(f"**Experience (Years):** {res.get('total_experience', 'N/A')}")

            # Handle skills and projects being dicts
            skills = res.get('skills', [])
            if skills and isinstance(skills[0], dict):
                skills = [s.get('name','') for s in skills]
            projects = res.get('projects', [])
            if projects and isinstance(projects[0], dict):
                projects = [p.get('name','') for p in projects]

            st.write(f"**Top Skills:** {', '.join(skills) if skills and skills != ['Not Available'] else 'N/A'}")
            st.write(f"**Projects:** {', '.join(projects) if projects and projects != ['Not Available'] else 'N/A'}")

            with st.expander("🔎 Full JSON"):
                st.json(res)

            st.markdown("---")

        # Bulk download
        json_export = json.dumps(results, indent=2)
        st.download_button(
            "💾 Download All Results (JSON)",
            json_export,
            "parsed_resumes.json",
            "application/json"
        )

# ---------------- Candidate Ranking ---------------- #
elif selected == "Candidate Ranking":
    st.header("🏆 Candidate Ranking")

    jd_file = st.file_uploader("📂 Upload Job Description (txt/pdf)", type=["txt", "pdf"], key="jd_upload")
    jd_text_manual = st.text_area("✍️ Or paste the Job Description here", placeholder="Paste JD here...")

    jd_text = None
    if jd_file:
        if jd_file.name.endswith(".pdf"):
            parser = ResumeParser()
            jd_text = parser._extract_text_from_pdf(jd_file)
        else:
            jd_text = jd_file.read().decode("utf-8")
        st.success("✅ Job Description uploaded!")
    elif jd_text_manual.strip():
        jd_text = jd_text_manual
        st.success("✅ Job Description entered manually!")

    if jd_text:
        st.session_state.jd_text = jd_text
        if "parsed" in st.session_state and st.session_state.parsed:
            resumes = st.session_state.parsed

            # Extract JD domain to check for mismatches
            jd_lower = jd_text.lower()
            jd_domain = "other"
            domain_keywords = {
                "software": ["software", "developer", "programming", "coding", "java", "python", "javascript", "react", "node"],
                "data": ["data science", "analyst", "machine learning", "ai", "sql", "database", "big data"],
                "design": ["design", "ui", "ux", "graphic", "fashion", "creative", "photoshop", "illustrator"],
                "business": ["business", "marketing", "sales", "manager", "finance", "account", "mba"],
                "engineering": ["engineer", "mechanical", "electrical", "civil", "manufacturing"]
            }
            
            for domain, keywords in domain_keywords.items():
                if any(keyword in jd_lower for keyword in keywords):
                    jd_domain = domain
                    break

            # ---------- Compute weighted score ----------
            def calculate_weighted_score(resume: dict, jd_text: str, jd_domain: str):
                jd_lower = jd_text.lower()
                total_score = 0
                match_reasons = []

                # Skills matching (most important)
                skills_score = 0
                skills_list = resume.get('skills', [])
                if skills_list and skills_list != ["Not Available"] and skills_list:
                    if isinstance(skills_list[0], dict):
                        skills_list = [s.get('name','') for s in skills_list if s.get('name') != "Not Available"]
                    
                    # Count how many skills from resume are mentioned in JD
                    matched_skills = [skill for skill in skills_list if skill and skill.lower() in jd_lower]
                    if matched_skills:
                        skills_score = (len(matched_skills) / len(skills_list)) * 40
                        match_reasons.append(f"Skills: {', '.join(matched_skills[:3])}")

                # Check for domain mismatch
                resume_skills_text = ' '.join(skills_list).lower() if skills_list and skills_list != ["Not Available"] else ""
                domain_mismatch = False
                
                if jd_domain == "software" and not any(keyword in resume_skills_text for keyword in domain_keywords["software"]):
                    domain_mismatch = True
                elif jd_domain == "design" and not any(keyword in resume_skills_text for keyword in domain_keywords["design"]):
                    domain_mismatch = True
                elif jd_domain == "data" and not any(keyword in resume_skills_text for keyword in domain_keywords["data"]):
                    domain_mismatch = True
                elif jd_domain == "business" and not any(keyword in resume_skills_text for keyword in domain_keywords["business"]):
                    domain_mismatch = True
                elif jd_domain == "engineering" and not any(keyword in resume_skills_text for keyword in domain_keywords["engineering"]):
                    domain_mismatch = True

                # If domain mismatch, significantly reduce score
                if domain_mismatch:
                    total_score = max(skills_score * 0.1, 5)  # Max 10% of skills score or minimum 5
                    return total_score, ["Domain mismatch - resume doesn't match JD requirements"]

                # Education matching
                education_score = 0
                education = resume.get('education', '')
                if education and education != "Not Available" and education != ["Not Available"]:
                    if isinstance(education, list):
                        education_str = ' '.join(education).lower()
                    else:
                        education_str = str(education).lower()
                    
                    # Check if education matches JD requirements
                    education_terms = ['bachelor', 'master', 'phd', 'mba', 'degree', 'diploma']
                    jd_education_terms = [term for term in education_terms if term in jd_lower]
                    
                    if jd_education_terms and any(term in education_str for term in jd_education_terms):
                        education_score = 20
                        match_reasons.append("Education matches requirements")

                # Experience matching
                experience_score = 0
                experience = resume.get('total_experience', '')
                if experience and experience != "Not Available":
                    resume_exp_match = re.search(r'\d+', str(experience))
                    if resume_exp_match:
                        resume_exp = int(resume_exp_match.group(0))
                        # Look for experience requirements in JD
                        exp_patterns = [r'(\d+)[\s\-]*years?', r'(\d+)[\s\-]*yrs?', r'experience.*(\d+)']
                        for pattern in exp_patterns:
                            match = re.search(pattern, jd_lower)
                            if match:
                                jd_exp = int(match.group(1))
                                if resume_exp >= jd_exp:
                                    experience_score = 20
                                    match_reasons.append(f"Experience: {resume_exp}+ years")
                                    break

                # Projects matching
                projects_score = 0
                projects_list = resume.get('projects', [])
                if projects_list and projects_list != ["Not Available"] and projects_list:
                    if isinstance(projects_list[0], dict):
                        projects_list = [p.get('name','') for p in projects_list if p.get('name') != "Not Available"]
                    
                    # Check if project keywords match JD
                    project_keywords = ' '.join(projects_list).lower()
                    jd_project_terms = ['project', 'development', 'design', 'implementation', 'management']
                    matched_projects = [term for term in jd_project_terms if term in jd_lower and term in project_keywords]
                    
                    if matched_projects:
                        projects_score = 20
                        match_reasons.append("Relevant project experience")

                total_score = round(skills_score + education_score + experience_score + projects_score, 2)
                return total_score, match_reasons

            # Rank candidates
            ranked = []
            for res in resumes:
                score, match_reasons = calculate_weighted_score(res, jd_text, jd_domain)
                res_copy = res.copy()
                res_copy["score"] = score
                res_copy["match_reasons"] = match_reasons
                ranked.append(res_copy)

            ranked.sort(key=lambda x: x["score"], reverse=True)

            # Display JD for reference
            with st.expander("📋 View Job Description"):
                st.text(jd_text)
                st.write(f"**Detected Domain:** {jd_domain.upper()}")

            # ---------- Tabular display ----------
            st.subheader("📊 Candidate Ranking Table")
            st.write(f"**Total Candidates:** {len(ranked)}")
            st.write(f"**JD Domain:** {jd_domain.upper()}")

            table_data = []
            for i, r in enumerate(ranked, 1):
                skills = r.get('skills', [])
                if skills and isinstance(skills[0], dict):
                    skills = [s.get('name','') for s in skills if s.get('name') != "Not Available"]
                projects = r.get('projects', [])
                if projects and isinstance(projects[0], dict):
                    projects = [p.get('name','') for p in projects if p.get('name') != "Not Available"]

                score = r.get("score", 0)
                status = "✅ Good match" if score >= 50 else "⚠️ Partial match" if score >= 20 else "❌ Poor match"
                
                table_data.append({
                    "Rank": i,
                    "Name": r.get("name", "N/A"),
                    "Experience": r.get("total_experience", "N/A"),
                    "Education": r.get("education", "N/A"),
                    "Top Skills": ", ".join(skills[:3]) if skills and skills != ["Not Available"] else "N/A",
                    "Match Score": f"{score:.1f}/100",
                    "Status": status
                })

            df = pd.DataFrame(table_data)
            st.dataframe(df, width=True)

            # Show top candidates with match reasons
            st.subheader("🏅 Top Candidates with Match Analysis")
            for i, candidate in enumerate(ranked[:5], 1):
                score = candidate.get("score", 0)
                match_reasons = candidate.get("match_reasons", [])
                
                if score < 10:
                    st.markdown(f'<div class="low-match">', unsafe_allow_html=True)
                    st.markdown(f"### #{i} - {candidate.get('name', 'N/A')} - Score: {score:.1f}/100")
                    st.warning("❌ POOR MATCH - Resume doesn't align with JD requirements")
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f"### #{i} - {candidate.get('name', 'N/A')} - Score: {score:.1f}/100")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Email:** {candidate.get('email', 'N/A')}")
                    st.write(f"**Experience:** {candidate.get('total_experience', 'N/A')} years")
                    st.write(f"**Education:** {candidate.get('education', 'N/A')}")
                with col2:
                    skills = candidate.get('skills', [])
                    if skills and isinstance(skills[0], dict):
                        skills = [s.get('name','') for s in skills if s.get('name') != "Not Available"]
                    st.write(f"**Skills:** {', '.join(skills[:5]) if skills and skills != ['Not Available'] else 'N/A'}")
                
                if match_reasons:
                    st.write("**Match Reasons:**")
                    for reason in match_reasons:
                        st.write(f"✅ {reason}")
                else:
                    st.write("**No significant matches found with JD**")
                
                st.markdown("---")

            # Show statistics
            good_matches = sum(1 for r in ranked if r.get("score", 0) >= 50)
            partial_matches = sum(1 for r in ranked if 20 <= r.get("score", 0) < 50)
            poor_matches = sum(1 for r in ranked if r.get("score", 0) < 20)
            
            st.subheader("📈 Match Statistics")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Good Matches", good_matches)
            with col2:
                st.metric("Partial Matches", partial_matches)
            with col3:
                st.metric("Poor Matches", poor_matches)

        else:
            st.warning("⚠️ Please upload resumes first.")
    else:
        st.info("📂 Upload a JD file or paste it above to rank candidates.")


# # perfect
# import os
# import json
# from pathlib import Path
# import tempfile
# import pandas as pd
# import streamlit as st
# from streamlit_option_menu import option_menu

# from resume_parser import ResumeParser
# from candidate_ranker import CandidateRanker

# st.set_page_config(page_title="Resume Parser & Ranker", page_icon="📄", layout="wide")

# # ---------------- UI helpers ---------------- #
# st.markdown("""
# <style>
# .metric-card{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:1rem;border-radius:10px;color:#fff;text-align:center}
# .candidate-card{border:1px solid #ddd;border-radius:10px;padding:1rem;margin:1rem 0;background:#f8f9fa}
# .top-candidate{border:2px solid #28a745;background:#d4edda}
# </style>
# """, unsafe_allow_html=True)

# def header():
#     st.markdown('<h1 style="text-align:center;margin:0 0 1rem 0">🎯 AI Resume Parser & Candidate Ranker</h1>', unsafe_allow_html=True)

# def metrics_box(title: str, value: str):
#     st.markdown(f'<div class="metric-card"><h3>{value}</h3><p>{title}</p></div>', unsafe_allow_html=True)

# # ---------------- Session ---------------- #
# if "parsed" not in st.session_state:
#     st.session_state.parsed = []
# if "rankings" not in st.session_state:
#     st.session_state.rankings = []
# if "jd_text" not in st.session_state:
#     st.session_state.jd_text = ""

# # ---------------- Nav ---------------- #
# header()
# selected = option_menu(
#     None,
#     ["Upload & Parse", "View Results", "Candidate Ranking"],
#     icons=["cloud-upload", "table", "trophy"],
#     orientation="horizontal",
#     default_index=0
# )

# # ---------------- Pages ---------------- #
# if selected == "Upload & Parse":
#     col1, col2 = st.columns([2,1])

#     with col1:
#         up = st.file_uploader(
#             "Upload resumes (PDF, DOCX, TXT, or ZIP folder)",
#             type=["pdf","docx","txt","zip"],
#             accept_multiple_files=True
#         )
#         model_path = st.text_input(
#             "Optional: Local LLaMA (.gguf) for extra parsing accuracy",
#             value=r"D:\downloads\tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
#             help="Leave as-is if you only want heuristic parsing. File must exist for LLM refinement."
#         )

#         if st.button("🚀 Parse Resumes", type="primary"):
#             if not up:
#                 st.warning("Upload at least one file.")
#             else:
#                 use_llm = os.path.exists(model_path)
#                 parser = ResumeParser(model_path=model_path if use_llm else None)
#                 results = []
#                 prog = st.progress(0.0)

#                 # collect all uploaded files with their original names
#                 all_files = []  # This will store tuples: (temp_path, original_filename)
#                 for uf in up:
#                     suffix = Path(uf.name).suffix.lower()
#                     original_filename = uf.name

#                     if suffix == ".zip":
#                         # unzip into temp folder
#                         with tempfile.TemporaryDirectory() as tmpdir:
#                             zip_path = Path(tmpdir) / uf.name
#                             with open(zip_path, "wb") as f:
#                                 f.write(uf.getbuffer())

#                             import zipfile
#                             with zipfile.ZipFile(zip_path, "r") as zip_ref:
#                                 zip_ref.extractall(tmpdir)

#                             # collect resumes with their original names
#                             for f in Path(tmpdir).rglob("*"):
#                                 if f.suffix.lower() in [".pdf", ".docx", ".txt"]:
#                                     all_files.append((f, f.name))  # Store both path and original name
#                     else:
#                         with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
#                             tmp.write(uf.getbuffer())
#                             tmp_path = Path(tmp.name)
#                             all_files.append((tmp_path, original_filename))  # Store original filename

#                 # helper to shorten JSON
#                 def shorten_resume_json(parsed: dict) -> dict:
#                     return {
#                         "name": parsed.get("name"),
#                         "email": parsed.get("email"),
#                         "phone": parsed.get("phone"),
#                         "linkedin": parsed.get("linkedin"),
#                         "github": parsed.get("github"),
#                         "education": parsed.get("education")[0] if parsed.get("education") else None,
#                         "summary": parsed.get("summary"),
#                         "skills": parsed.get("skills")[:5] if parsed.get("skills") else [],
#                         "projects": parsed.get("projects")[:5] if parsed.get("projects") else [],
#                         "total_experience": parsed.get("total_experience_years"),
#                         "filename": parsed.get("filename")
#                     }

#                 # parse all collected resumes
#                 for i, (fpath, original_filename) in enumerate(all_files):
#                     parsed = parser.parse_resume(str(fpath))
#                     parsed["filename"] = original_filename  # Use the original filename instead of temp name

#                     short_json = shorten_resume_json(parsed)
#                     results.append(short_json)

#                     try:
#                         os.unlink(fpath)
#                     except Exception:
#                         pass

#                     prog.progress((i+1)/len(all_files))

#                 st.session_state.parsed = results
#                 st.success(f"Parsed {len(results)} resumes ✅")

#     with col2:
#         st.info("""
#         **What gets extracted**
#         - Name, Email, Phone, LinkedIn, GitHub  
#         - Education (only highest), Skills (top 5), Projects (top 5), Summary  
#         - Estimated Total Experience (years)  

#         **Tip:** You can upload resumes individually **or** upload a folder as `.zip` (auto-unzipped).
#         """)

# # ---------------- View Results ---------------- #
# if selected == "View Results":
#     st.header("📂 Parsed Resume Results")

#     if not st.session_state.parsed:
#         st.warning("No resumes parsed yet. Please upload and parse resumes first.")
#     else:
#         results = st.session_state.parsed

#         for res in results:
#             st.subheader(res.get("filename", "Unnamed Resume"))

#             st.write(f"**Name:** {res.get('name', 'N/A')}")
#             st.write(f"**Email:** {res.get('email', 'N/A')}")
#             st.write(f"**Phone:** {res.get('phone', 'N/A')}")
#             st.write(f"**Experience (Years):** {res.get('total_experience', 'N/A')}")

#             # Handle skills and projects being dicts
#             skills = res.get('skills', [])
#             if skills and isinstance(skills[0], dict):
#                 skills = [s.get('name','') for s in skills]
#             projects = res.get('projects', [])
#             if projects and isinstance(projects[0], dict):
#                 projects = [p.get('name','') for p in projects]

#             st.write(f"**Top Skills:** {', '.join(skills) if skills else 'N/A'}")
#             st.write(f"**Projects:** {', '.join(projects) if projects else 'N/A'}")

#             with st.expander("🔎 Full JSON"):
#                 st.json(res)

#             st.markdown("---")

#         # Bulk download
#         json_export = json.dumps(results, indent=2)
#         st.download_button(
#             "💾 Download All Results (JSON)",
#             json_export,
#             "parsed_resumes.json",
#             "application/json"
#         )

# # ---------------- Candidate Ranking ---------------- #
# elif selected == "Candidate Ranking":
#     st.header("🏆 Candidate Ranking")

#     jd_file = st.file_uploader("📂 Upload Job Description (txt/pdf)", type=["txt", "pdf"], key="jd_upload")
#     jd_text_manual = st.text_area("✍️ Or paste the Job Description here", placeholder="Paste JD here...")

#     jd_text = None
#     if jd_file:
#         if jd_file.name.endswith(".pdf"):
#             parser = ResumeParser()
#             jd_text = parser.extract_text_from_pdf(jd_file)
#         else:
#             jd_text = jd_file.read().decode("utf-8")
#         st.success("✅ Job Description uploaded!")
#     elif jd_text_manual.strip():
#         jd_text = jd_text_manual
#         st.success("✅ Job Description entered manually!")

#     if jd_text:
#         if "parsed" in st.session_state and st.session_state.parsed:
#             resumes = st.session_state.parsed

#             # ---------- Sliders for weights ----------
#             st.subheader("⚖️ Adjust Weights for Scoring (0–10)")
#             col1, col2, col3 = st.columns(3)
#             with col1:
#                 weight_skills = st.slider("Skills Weight", 0, 10, 6)
#             with col2:
#                 weight_education = st.slider("Education Weight", 0, 10, 3)
#             with col3:
#                 weight_projects = st.slider("Projects Weight", 0, 10, 1)

#             # normalize weights to 100
#             total_slider = weight_skills + weight_education + weight_projects
#             if total_slider == 0:
#                 st.warning("⚠️ At least one weight must be > 0.")
#                 total_slider = 1
#             w_skills = (weight_skills / total_slider) * 100
#             w_education = (weight_education / total_slider) * 100
#             w_projects = (weight_projects / total_slider) * 100

#             # ---------- Compute weighted score ----------
#             def calculate_weighted_score(resume: dict, jd_text: str):
#                 jd_lower = jd_text.lower()

#                 # Skills
#                 skills_score = 0
#                 skills_list = resume.get('skills', [])
#                 if skills_list:
#                     if isinstance(skills_list[0], dict):
#                         skills_list = [s.get('name','') for s in skills_list]
#                     skill_keywords = [s.lower() for s in skills_list]
#                     matched_skills = sum(1 for skill in skill_keywords if skill in jd_lower)
#                     skills_score = min(matched_skills / len(skill_keywords), 1) * w_skills

#                 # Education
#                 education_score = 0
#                 if resume.get('education'):
#                     edu_keywords = resume['education'].lower().split()
#                     matched_edu = sum(1 for kw in edu_keywords if kw in jd_lower)
#                     education_score = min(matched_edu / len(edu_keywords), 1) * w_education

#                 # Projects
#                 projects_score = 0
#                 projects_list = resume.get('projects', [])
#                 if projects_list:
#                     if isinstance(projects_list[0], dict):
#                         projects_list = [p.get('name','') for p in projects_list]
#                     project_keywords = [p.lower() for p in projects_list]
#                     matched_projects = sum(1 for p in project_keywords if p in jd_lower)
#                     projects_score = min(matched_projects / len(project_keywords), 1) * w_projects

#                 total_score = round(skills_score + education_score + projects_score, 2)
#                 return total_score

#             # Rank candidates
#             ranked = []
#             for res in resumes:
#                 score = calculate_weighted_score(res, jd_text)
#                 res_copy = res.copy()
#                 res_copy["score"] = score
#                 ranked.append(res_copy)

#             ranked.sort(key=lambda x: x["score"], reverse=True)

#             # ---------- Tabular display ----------
#             st.subheader("📊 Candidate Ranking Table")
#             table_data = []
#             for i, r in enumerate(ranked, 1):
#                 skills = r.get('skills', [])
#                 if skills and isinstance(skills[0], dict):
#                     skills = [s.get('name','') for s in skills]
#                 projects = r.get('projects', [])
#                 if projects and isinstance(projects[0], dict):
#                     projects = [p.get('name','') for p in projects]

#                 table_data.append({
#                     "Rank": i,
#                     "Name": r.get("name", "N/A"),
#                     "Email": r.get("email", "N/A"),
#                     "Phone": r.get("phone", "N/A"),
#                     "Education": r.get("education", "N/A"),
#                     "Top Skills": ", ".join(skills) if skills else "N/A",
#                     "Projects": ", ".join(projects) if projects else "N/A",
#                     "Weighted Score": r.get("score", 0)
#                 })

#             df = pd.DataFrame(table_data)
#             st.dataframe(df)
#         else:
#             st.warning("⚠️ Please upload resumes first.")
#     else:
#         st.info("📂 Upload a JD file or paste it above to rank candidates.")