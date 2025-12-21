import streamlit as st
from file_utils import show_pdf


def display_resume_preview(save_path):
    with st.container():
        st.header("✨ **Resume Preview**")
        show_pdf(save_path)
