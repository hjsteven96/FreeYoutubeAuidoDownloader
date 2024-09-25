import streamlit as st
import requests
import re
from datetime import datetime
from isodate import parse_duration
from youtube_transcript_api import YouTubeTranscriptApi
import json

# YouTube API 키 설정
API_KEY = "AIzaSyCc_2gWC1gaHw2BUV8YX8jYPcbOzUqvRpE"  # 여기에 실제 API 키를 입력하세요

def get_video_id(url):
    video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return video_id_match.group(1) if video_id_match else None

def get_video_info(video_id):
    try:
        video_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails&id={video_id}&key={API_KEY}"
        video_response = requests.get(video_url)
        video_data = video_response.json()

        if not video_data.get("items"):
            return None

        item = video_data["items"][0]
        snippet = item["snippet"]
        content_details = item["contentDetails"]

        return {
            "title": snippet["title"],
            "description": snippet["description"],
            "channel_title": snippet["channelTitle"],
            "publish_date": snippet["publishedAt"],
            "duration": content_details["duration"],
        }
    except Exception as e:
        st.error(f"동영상 정보를 가져오는 중 오류 발생: {str(e)}")
        return None

def get_available_transcripts(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        return [{'language': t.language, 'language_code': t.language_code} for t in transcript_list]
    except Exception as e:
        st.error(f"자막 정보를 가져오는 중 오류 발생: {str(e)}")
        return []

def download_transcript(video_id, language_code):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language_code])
        return transcript
    except Exception as e:
        st.error(f"자막 다운로드 중 오류 발생: {str(e)}")
        return None

st.set_page_config(page_title="YouTube 정보 뷰어", page_icon="🎥")
st.title("YouTube 정보 뷰어")

# 세션 상태 초기화
if 'url' not in st.session_state:
    st.session_state.url = ""
if 'video_info' not in st.session_state:
    st.session_state.video_info = None
if 'transcripts' not in st.session_state:
    st.session_state.transcripts = None

# URL 입력 필드
url = st.text_input("YouTube 링크를 입력하세요:", value=st.session_state.url)

# URL이 변경되면 비디오 정보 초기화
if url != st.session_state.url:
    st.session_state.url = url
    st.session_state.video_info = None
    st.session_state.transcripts = None

# 정보 가져오기 버튼
if st.button("정보 가져오기") or (url and not st.session_state.video_info):
    video_id = get_video_id(url)
    if video_id:
        with st.spinner('동영상 정보를 가져오는 중...'):
            st.session_state.video_info = get_video_info(video_id)
            st.session_state.transcripts = get_available_transcripts(video_id)
    else:
        st.error("유효한 YouTube URL을 입력해주세요.")

# 비디오 정보 표시
if st.session_state.video_info:
    video_info = st.session_state.video_info
    st.subheader(video_info["title"])
    st.write(f"채널: {video_info['channel_title']}")
    
    publish_date = datetime.fromisoformat(video_info['publish_date'].replace('Z', '+00:00'))
    st.write(f"게시일: {publish_date.strftime('%Y년 %m월 %d일')}")
    
    duration = parse_duration(video_info['duration'])
    hours, remainder = divmod(duration.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    duration_str = f"{int(hours)}시간 " if hours > 0 else ""
    duration_str += f"{int(minutes)}분 {int(seconds)}초"
    st.write(f"재생 시간: {duration_str}")
    
    st.subheader("동영상 설명")
    st.write(video_info["description"])
    
    st.subheader("사용 가능한 자막")
    if st.session_state.transcripts:
        transcript_options = {f"{t['language']} ({t['language_code']})": t['language_code'] for t in st.session_state.transcripts}
        selected_transcript = st.selectbox("다운로드할 자막을 선택하세요:", list(transcript_options.keys()))
        
        if st.button("선택한 자막 다운로드"):
            language_code = transcript_options[selected_transcript]
            with st.spinner('자막을 다운로드하는 중...'):
                transcript = download_transcript(get_video_id(url), language_code)
            if transcript:
                st.download_button(
                    label="자막 파일 다운로드 (JSON)",
                    data=json.dumps(transcript, ensure_ascii=False, indent=2),
                    file_name=f"{video_info['title']}_transcript.json",
                    mime="application/json"
                )
                st.success("자막 다운로드가 완료되었습니다. 위 버튼을 클릭하여 다운로드하세요.")
    else:
        st.write("이 동영상에는 사용 가능한 자막이 없습니다.")
    
    st.subheader("동영상 미리보기")
    st.video(url)

st.write("참고: 이 애플리케이션은 YouTube Data API와 youtube-transcript-api를 사용합니다.")
st.write("주의: 저작권을 존중하며 합법적인 방법으로만 콘텐츠를 이용해 주세요.")
