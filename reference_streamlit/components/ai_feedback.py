import streamlit as st


def display_ai_feedback(ai_summary):
    with st.container():
        st.subheader("📝 **AI Summary**")
        st.markdown(ai_summary)
