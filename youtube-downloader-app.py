import streamlit as st
import googleapiclient.discovery
import re

# YouTube API 키 설정
API_KEY = "AIzaSyCc_2gWC1gaHw2BUV8YX8jYPcbOzUqvRpE"  # 여기에 실제 API 키를 입력하세요

# YouTube API 클라이언트 생성
youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=API_KEY)

def get_video_id(url):
    # YouTube URL에서 비디오 ID 추출
    video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    if video_id_match:
        return video_id_match.group(1)
    return None

def get_video_info(video_id):
    try:
        # 비디오 정보 요청
        video_response = youtube.videos().list(
            part="snippet,contentDetails",
            id=video_id
        ).execute()

        if not video_response["items"]:
            return None

        video_data = video_response["items"][0]
        snippet = video_data["snippet"]
        content_details = video_data["contentDetails"]

        # 자막 정보 요청
        captions_response = youtube.captions().list(
            part="snippet",
            videoId=video_id
        ).execute()

        return {
            "title": snippet["title"],
            "description": snippet["description"],
            "channel_title": snippet["channelTitle"],
            "publish_date": snippet["publishedAt"],
            "duration": content_details["duration"],
            "captions": captions_response.get("items", [])
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
            st.write(f"게시일: {video_info['publish_date']}")
            st.write(f"재생 시간: {video_info['duration']}")
            
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
