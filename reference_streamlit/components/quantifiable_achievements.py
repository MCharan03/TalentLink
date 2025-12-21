import streamlit as st


def display_quantifiable_achievements(suggestions):
    with st.container():
        st.subheader("🎯 **Quantifiable Achievements Suggestions**")
        if suggestions:
            for suggestion in suggestions:
                st.markdown(f"* {suggestion}")
        else:
            st.info(
                "No specific suggestions for quantifiable achievements at the moment. Your resume looks good in this regard!")
