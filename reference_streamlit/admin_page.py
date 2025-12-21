import streamlit as st
import pandas as pd
import io
import plotly.express as px
from file_utils import create_admin_pdf
from admin_panel import handle_admin_panel, handle_user_management
from database import delete_all_data, reset_database


def display_skill_demand_trends(connection, cursor):
    st.subheader("📈 Skill Demand Trends")
    cursor.execute(
        "SELECT required_skills FROM job_postings WHERE status = 'open'")
    skills_data = cursor.fetchall()

    all_skills = []
    for row in skills_data:
        if row[0]:  # Check if skills string is not empty
            skills_list = [skill.strip().lower()
                           for skill in row[0].split(',')]
            all_skills.extend(skills_list)

    if not all_skills:
        st.info("No skills found in open job postings.")
        return

    skill_counts = pd.Series(all_skills).value_counts().reset_index()
    skill_counts.columns = ['Skill', 'Count']

    fig = px.bar(
        skill_counts,
        x='Skill',
        y='Count',
        title='Most Demanded Skills',
        labels={'Count': 'Number of Job Postings', 'Skill': 'Skill'},
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)


def display_user_engagement_metrics(connection, cursor):
    st.subheader("📊 User Engagement Metrics")

    # Fetch data for resume analyses
    cursor.execute("SELECT Timestamp FROM user_data")
    resume_analyses_timestamps = [pd.to_datetime(
        row[0], format="%Y-%m-%d_%H:%M:%S") for row in cursor.fetchall()]

    # Fetch data for mock tests
    cursor.execute("SELECT timestamp FROM mock_tests")
    mock_tests_timestamps = [pd.to_datetime(
        row[0], format="%Y-%m-%d %H:%M:%S") for row in cursor.fetchall()]

    # Fetch data for mock interviews
    cursor.execute("SELECT timestamp FROM mock_interviews")
    mock_interviews_timestamps = [pd.to_datetime(
        row[0], format="%Y-%m-%d %H:%M:%S") for row in cursor.fetchall()]

    all_timestamps = []
    for ts in resume_analyses_timestamps:
        all_timestamps.append({'Timestamp': ts, 'Activity': 'Resume Analysis'})
    for ts in mock_tests_timestamps:
        all_timestamps.append({'Timestamp': ts, 'Activity': 'Mock Test'})
    for ts in mock_interviews_timestamps:
        all_timestamps.append({'Timestamp': ts, 'Activity': 'Mock Interview'})

    if not all_timestamps:
        st.info("No user engagement data available yet.")
        return

    df = pd.DataFrame(all_timestamps)
    df['Date'] = df['Timestamp'].dt.date  # Extract date for grouping

    # Group by date and activity
    engagement_counts = df.groupby(
        ['Date', 'Activity']).size().reset_index(name='Count')

    fig = px.line(
        engagement_counts,
        x='Date',
        y='Count',
        color='Activity',
        title='User Activity Over Time',
        labels={'Count': 'Number of Activities', 'Date': 'Date'},
        hover_data={'Date': True, 'Activity': True, 'Count': True}
    )
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)


def handle_admin_user(connection, cursor):
    """Handles the admin login and data display logic."""
    if 'admin_logged_in' not in st.session_state:
        st.session_state.admin_logged_in = False

    if not st.session_state.admin_logged_in:
        st.title("Admin Login")
        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')
        if st.button('Login'):
            if ad_user == st.secrets["admin"]["username"] and ad_password == st.secrets["admin"]["password"]:
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("Invalid admin credentials")
    else:
        st.title("Admin Panel")
        dashboard_tab, interview_funnel_tab, user_management_tab = st.tabs(
            ["Dashboard", "Interview Funnel", "User Management"])

        with dashboard_tab:
            if st.button("Logout"):
                st.session_state.admin_logged_in = False
                st.rerun()
            st.success('Welcome to the Admin Panel')

            with st.expander("Database Actions"):
                if st.button("Reset Database (Erase All)"):
                    st.session_state.reset_db_confirmation = True

            if 'reset_db_confirmation' in st.session_state and st.session_state.reset_db_confirmation:
                confirm_reset_tab, cancel_reset_tab = st.tabs(
                    ["Confirm Database Reset", "Cancel"])
                with confirm_reset_tab:
                    st.error("DANGER ZONE: Are you absolutely, positively sure you want to RESET THE ENTIRE DATABASE? This will drop ALL tables and recreate them, permanently erasing ALL data and users. This action cannot be undone.")
                    if st.button("CONFIRM ERASE ALL AND RESET DATABASE"):
                        if reset_database(connection, cursor):
                            st.session_state.reset_db_confirmation = False
                            st.success(
                                "Database has been completely reset. All data and users are erased.")
                            st.rerun()
                        else:
                            st.error("Failed to reset database.")
                with cancel_reset_tab:
                    if st.button("Cancel Database Reset"):
                        st.session_state.reset_db_confirmation = False
                        st.rerun()

            # Fetch data from the database
            cursor.execute(
                'SELECT u.username, ud.* FROM user_data ud JOIN users u ON ud.user_id = u.id')
            data = cursor.fetchall()

            if not data:
                st.info("No user data has been collected yet.")
            else:
                # Create DataFrame
                df = pd.DataFrame(data, columns=['Username', 'ID', 'Name', 'Email_ID', 'ai_feedback', 'Timestamp', 'Page_no', 'Predicted_Field', 'User_level', 'Actual_skills',
                                  'Recommended_skills', 'Recommended_courses', 'user_id', 'status', 'resume_score', 'quantifiable_achievements_suggestions', 'formatting_analysis'])

                # --- Display User Data Table ---
                with st.container():
                    st.header("📊 **User's Data**")

                    # Create a copy for filtering
                    filtered_df = df.copy()

                    with st.expander("Search and Filter Data"):
                        search_term = st.text_input("Search all data")

                        if not df.empty:
                            field_options = df['Predicted_Field'].unique()
                            filter_fields = st.multiselect(
                                "Filter by Predicted Field", options=field_options)
                        else:
                            filter_fields = []

                        if not df.empty:
                            level_options = df['User_level'].unique()
                            filter_levels = st.multiselect(
                                "Filter by User Level", options=level_options)
                        else:
                            filter_levels = []

                    if search_term:
                        mask = filtered_df.apply(lambda row: row.astype(
                            str).str.contains(search_term, case=False).any(), axis=1)
                        filtered_df = filtered_df[mask]

                    if filter_fields:
                        filtered_df = filtered_df[filtered_df['Predicted_Field'].isin(
                            filter_fields)]

                    if filter_levels:
                        filtered_df = filtered_df[filtered_df['User_level'].isin(
                            filter_levels)]

                    st.dataframe(filtered_df)

                    with st.expander("Actions"):
                        pdf_data = create_admin_pdf(filtered_df)
                        st.download_button(
                            label="Download Report as PDF",
                            data=pdf_data,
                            file_name='User_Data.pdf',
                            mime='application/pdf',
                        )

                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            filtered_df.to_excel(
                                writer, index=False, sheet_name='Sheet1')
                        excel_data = output.getvalue()
                        st.download_button(
                            label="Download Report as Excel",
                            data=excel_data,
                            file_name='User_Data.xlsx',
                            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        )

                        if st.button("Delete All Data"):
                            st.session_state.delete_all_confirmation = True

                    if 'delete_all_confirmation' in st.session_state and st.session_state.delete_all_confirmation:
                        confirm_tab, cancel_tab = st.tabs(
                            ["Confirm Deletion", "Cancel"])
                        with confirm_tab:
                            st.warning("Are you absolutely sure you want to delete ALL data from the entire database, including all users, analyses, mock tests, interviews, job postings, applications, and notifications? This action cannot be undone.")
                            if st.button("Confirm Delete All"):
                                if delete_all_data(connection, cursor):
                                    st.session_state.delete_all_confirmation = False
                                    st.success(
                                        "All data has been deleted from the database.")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete all data.")
                        with cancel_tab:
                            if st.button("Cancel Deletion"):
                                st.session_state.delete_all_confirmation = False
                                st.rerun()

                # --- Display Data Visualizations ---
                with st.container():
                    st.header("📈 **Data Visualizations**")

                    # Prepare data for charts by counting occurrences
                    field_counts = df['Predicted_Field'].value_counts(
                    ).reset_index()
                    field_counts.columns = ['Predicted_Field', 'Count']

                    level_counts = df['User_level'].value_counts(
                    ).reset_index()
                    level_counts.columns = ['User_level', 'Count']

                    font_color = "#000000" if st.session_state.theme == "Light" else "#FFFFFF"

                    fig1 = px.pie(
                        field_counts,
                        names='Predicted_Field',
                        values='Count',
                        title="Predicted Field Recommendations",
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    fig1.update_traces(
                        textposition='inside',
                        textinfo='percent',
                        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>',
                        marker=dict(line=dict(color='#FFFFFF', width=2))
                    )
                    fig1.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(
                            color=font_color,
                            size=14
                        ),
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=-0.2,
                            xanchor="center",
                            x=0.5
                        )
                    )
                    st.plotly_chart(fig1, use_container_width=True)

                    st.markdown("---")

                    fig2 = px.pie(
                        level_counts,
                        names='User_level',
                        values='Count',
                        title="Candidate Experience Levels",
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    fig2.update_traces(
                        textposition='inside',
                        textinfo='percent',
                        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>',
                        marker=dict(line=dict(color='#FFFFFF', width=2))
                    )
                    fig2.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(
                            color=font_color,
                            size=14
                        ),
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=-0.2,
                            xanchor="center",
                            x=0.5
                        )
                    )
                    st.plotly_chart(fig2, use_container_width=True)

            display_skill_demand_trends(connection, cursor)
            display_user_engagement_metrics(connection, cursor)

        with interview_funnel_tab:
            handle_admin_panel(connection, cursor)
        with user_management_tab:
            handle_user_management(connection, cursor)
