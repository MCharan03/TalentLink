import streamlit as st
from streamlit_tags import st_tags


def display_skills_and_recommendations(predicted_field, actual_skills, recommended_skills):
    with st.container():
        st.subheader("💡 **Skills & Recommendations**")
        st.success(
            f"📊 **Our analysis suggests you are a great fit for {predicted_field} roles!**")
        st_tags(label='### Your Skills',
                text='Skills extracted from your resume', value=actual_skills, key='1')
        st_tags(label='### Recommended Skills for You',
                text='Skills to boost your resume', value=recommended_skills, key='2')
        st.markdown("<p style='color: var(--info-color); font-weight: bold;'>Adding these skills to your resume can significantly boost your job prospects! 🚀</p>", unsafe_allow_html=True)
