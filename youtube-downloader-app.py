import streamlit as st
import requests
import re
from datetime import datetime
from isodate import parse_duration

# YouTube API 키 설정
API_KEY = "AIzaSyCc_2gWC1gaHw2BUV8YX8jYPcbOzUqvRpE"  # 여기에 실제 API 키를 입력하세요

def get_video_id(url):
    # YouTube URL에서 비디오 ID 추출
    video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    if video_id_match:
        return video_id_match.group(1)
    return None

def get_video_info(video_id):
    try:
        # 비디오 정보 요청
        video_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails&id={video_id}&key={API_KEY}"
        video_response = requests.get(video_url)
        video_data = video_response.json()

        if not video_data.get("items"):
            return None

        item = video_data["items"][0]
        snippet = item["snippet"]
        content_details = item["contentDetails"]

        # 자막 정보 요청
        captions_url = f"https://www.googleapis.com/youtube/v3/captions?part=snippet&videoId={video_id}&key={API_KEY}"
        captions_response = requests.get(captions_url)
        captions_data = captions_response.json()

        return {
            "title": snippet["title"],
            "description": snippet["description"],
            "channel_title": snippet["channelTitle"],
            "publish_date": snippet["publishedAt"],
            "duration": content_details["duration"],
            "captions": captions_data.get("items", [])
        }
    except Exception as e:
        st.error(f"동영상 정보를 가져오는 중 오류 발생: {str(e)}")
        return None

st.set_page_config(page_title="YouTube 정보 뷰어", page_icon="🎥")
st.title("YouTube 정보 뷰어")

url = st.text_input("YouTube 링크를 입력하세요:")

if url:
    video_id = get_video_id(url)
    if video_id:
        with st.spinner('동영상 정보를 가져오는 중...'):
            video_info = get_video_info(video_id)
        
        if video_info:
            st.subheader(video_info["title"])
            st.write(f"채널: {video_info['channel_title']}")
            
            # ISO 8601 형식의 날짜를 읽기 쉬운 형식으로 변환
            publish_date = datetime.fromisoformat(video_info['publish_date'].replace('Z', '+00:00'))
            st.write(f"게시일: {publish_date.strftime('%Y년 %m월 %d일')}")
            
            # ISO 8601 형식의 기간을 읽기 쉬운 형식으로 변환
            duration = parse_duration(video_info['duration'])
            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            duration_str = f"{int(hours)}시간 " if hours > 0 else ""
            duration_str += f"{int(minutes)}분 {int(seconds)}초"
            st.write(f"재생 시간: {duration_str}")
            
            st.subheader("동영상 설명")
            st.write(video_info["description"])
            
            st.subheader("사용 가능한 자막")
            if video_info["captions"]:
                for caption in video_info["captions"]:
                    st.write(f"- {caption['snippet']['language']} ({caption['snippet']['trackKind']})")
            else:
                st.write("이 동영상에는 사용 가능한 자막이 없습니다.")
            
            st.subheader("동영상 미리보기")
            st.video(url)
    else:
        st.error("유효한 YouTube URL을 입력해주세요.")
else:
    st.info("YouTube 동영상 링크를 입력하면 정보를 표시합니다.")

st.write("참고: 이 애플리케이션은 YouTube Data API를 사용합니다.")
