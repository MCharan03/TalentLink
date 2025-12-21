import streamlit as st


def display_basic_info(name, email, contact_number, experience_level, no_of_pages):
    with st.container():
        st.header("✨ **Resume Analysis**")
        st.success(f"Hello, {name}!")

        with st.container():
            st.subheader("📋 **Basic Information**")
            st.markdown(f"**Name:** {name}")
            st.markdown(f"**Email:** {email}")
            st.markdown(f"**Contact:** {contact_number}")
            st.markdown(f"**Resume Pages:** {no_of_pages}")

            if experience_level == "Fresher":
                st.markdown(
                    "<p style='text-align: left; color: #fabc10;'>You seem to be a **Fresher**! 🐣</p>", unsafe_allow_html=True)
            elif experience_level == "Intermediate":
                st.markdown(
                    "<p style='text-align: left; color: #1ed760;'>You are at an **Intermediate** level! 🚀</p>", unsafe_allow_html=True)
            else:
                st.markdown(
                    "<p style='text-align: left; color: #2196F3;'>You are an **Experienced** professional!👑</p>", unsafe_allow_html=True)
            return experience_level, no_of_pages
