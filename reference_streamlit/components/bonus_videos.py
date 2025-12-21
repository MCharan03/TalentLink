import streamlit as st
import random
import json
from file_utils import fetch_yt_video_title

with open('config.json', 'r') as f:
    config = json.load(f)

resume_videos = config['videos']['resume_videos']
interview_videos = config['videos']['interview_videos']


def display_bonus_videos():

    with st.container():

        st.header("**Bonus Videos**")

        st.subheader("Resume Writing Tips")

        resume_vid = random.choice(resume_videos)

        res_vid_title = fetch_yt_video_title(resume_vid)

        st.video(resume_vid)

        st.subheader("Interview Tips")

        interview_vid = random.choice(interview_videos)

        int_vid_title = fetch_yt_video_title(interview_vid)

        st.video(interview_vid)

        return resume_vid, interview_vid
