import streamlit as st


def display_course_recommendations(recommended_courses, resume_score):
    with st.container():
        st.subheader("🎓 **Resume Score & Recommended Courses**")
        st.metric("Your Resume Score", f"{resume_score}/100")
        st.markdown("---")
        st.markdown("**Recommended Courses to Boost Your Score:**")
        for course in recommended_courses:
            st.markdown(f"* {course}")
