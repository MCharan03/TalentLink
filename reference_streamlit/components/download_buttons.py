import streamlit as st
import pandas as pd
from file_utils import create_user_pdf, create_doc


def display_download_buttons(resume_data, ts, no_of_pages, field, cand_level, user_skills, recommended_skills, recommended_courses, resume_vid_url, interview_vid_url):

    user_data = {

        'Name': resume_data.get('name', 'N/A'),

        'Email_ID': resume_data.get('email', 'N/A'),

        'ai_feedback': resume_data.get('ai_feedback', 'N/A'),

        'Timestamp': ts,

        'Page_no': no_of_pages,

        'Predicted_Field': field,

        'User_level': cand_level,

        'Actual_skills': str(user_skills),

        'Recommended_skills': str(recommended_skills),

        'Recommended_courses': str(recommended_courses),

        'Resume Writing Tip URL': resume_vid_url,

        'Interview Tip URL': interview_vid_url,

    }

    user_df = pd.DataFrame([user_data])

    pdf_data = create_user_pdf(user_df)

    st.download_button(

        label="📄 Download Report as PDF",

        data=pdf_data,

        file_name=f"{resume_data.get('name', 'user')}_Resume_Analysis.pdf",

        mime='application/pdf',

    )

    doc_data = create_doc(user_df)

    st.download_button(

        label="📄 Download Report as DOC",

        data=doc_data,

        file_name=f"{resume_data.get('name', 'user')}_Resume_Analysis.docx",

        mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document',

    )
