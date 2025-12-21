import streamlit as st


def display_formatting_analysis(analysis):
    with st.container():
        st.subheader("📄 **Formatting Analysis**")
        if analysis:
            st.markdown(analysis)
        else:
            st.info(
                "No specific formatting analysis at the moment. Your resume's formatting looks good!")
