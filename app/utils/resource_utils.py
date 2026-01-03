import json
import os
import random
from pytubefix import YouTube, Search

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')

def load_config():
    """Loads the config.json file."""
    if not os.path.exists(CONFIG_PATH):
        return {}
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def get_curated_courses(predicted_field):
    """Returns curated course recommendations based on the predicted field."""
    config = load_config()
    courses = config.get('courses', {})
    
    field_lower = predicted_field.lower() if predicted_field else ""
    
    if 'data' in field_lower or 'science' in field_lower or 'analyst' in field_lower:
        return courses.get('ds_course', [])
    elif 'web' in field_lower or 'full stack' in field_lower or 'developer' in field_lower and 'android' not in field_lower and 'ios' not in field_lower:
        return courses.get('web_course', [])
    elif 'android' in field_lower:
        return courses.get('android_course', [])
    elif 'ios' in field_lower or 'swift' in field_lower:
        return courses.get('ios_course', [])
    elif 'ui' in field_lower or 'ux' in field_lower or 'design' in field_lower:
        return courses.get('uiux_course', [])
    else:
        return []

def fetch_yt_video_title(link):
    """Fetches YouTube video title using pytubefix, with robust error handling."""
    try:
        yt = YouTube(link)
        return yt.title
    except Exception:
        return "Video Title Not Available"

def get_random_bonus_videos():
    """Returns random resume and interview tips from config."""
    config = load_config()
    videos = config.get('videos', {})
    
    resume_videos = videos.get('resume_videos', [])
    interview_videos = videos.get('interview_videos', [])
    
    res = {}
    if resume_videos:
        link = random.choice(resume_videos)
        res['resume_tip'] = {'link': link, 'title': fetch_yt_video_title(link)}
    
    if interview_videos:
        link = random.choice(interview_videos)
        res['interview_tip'] = {'link': link, 'title': fetch_yt_video_title(link)}
        
    return res

def get_dynamic_bonus_videos(analysis_result):
    """
    Fetches dynamic bonus videos based on the AI analysis search queries.
    Falls back to random videos if search fails or no queries.
    """
    queries = analysis_result.get('youtube_search_queries', [])
    
    if not queries:
        return get_random_bonus_videos()
    
    videos = {}
    
    try:
        # 1. Resume/Topic Tip (From 1st Query)
        s1 = Search(queries[0])
        # pytubefix Search results are lazy, access .videos to trigger fetch
        results1 = s1.videos
        if results1:
            # Pick top result
            vid = results1[0]
            videos['resume_tip'] = {'link': vid.watch_url, 'title': vid.title}
        
        # 2. Interview/Improvement Tip (From 2nd Query or similar)
        if len(queries) > 1:
            s2 = Search(queries[1])
            results2 = s2.videos
            if results2:
                vid = results2[0]
                videos['interview_tip'] = {'link': vid.watch_url, 'title': vid.title}
        
        # If we didn't find enough, fill with random
        if not videos.get('resume_tip') or not videos.get('interview_tip'):
            random_vids = get_random_bonus_videos()
            if not videos.get('resume_tip'):
                videos['resume_tip'] = random_vids.get('resume_tip')
            if not videos.get('interview_tip'):
                videos['interview_tip'] = random_vids.get('interview_tip')
                
    except Exception as e:
        print(f"Error fetching dynamic videos: {e}")
        return get_random_bonus_videos()
        
    return videos
