import streamlit as st
import requests
import re
from datetime import datetime
from isodate import parse_duration
import xml.etree.ElementTree as ET
import base64

# YouTube API 키 설정
API_KEY = "YOUR_API_KEY_HERE"  # 여기에 실제 API 키를 입력하세요

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

def download_caption(caption_id):
    try:
        caption_url = f"https://www.googleapis.com/youtube/v3/captions/{caption_id}?key={API_KEY}"
        headers = {"Accept": "application/ttml+xml"}
        response = requests.get(caption_url, headers=headers)
        
        if response.status_code == 200:
            return response.text
        else:
            st.error(f"자막 다운로드 중 오류 발생: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"자막 다운로드 중 오류 발생: {str(e)}")
        return None

def parse_ttml_to_srt(ttml_content):
    root = ET.fromstring(ttml_content)
    namespace = {'tt': 'http://www.w3.org/ns/ttml'}
    
    srt_content = ""
    for i, p in enumerate(root.findall('.//tt:p', namespace), 1):
        begin = p.get('begin')
        end = p.get('end')
        text = p.text or ""
        
        srt_content += f"{i}\n{begin.replace('.', ',')} --> {end.replace('.', ',')}\n{text}\n\n"
    
    return srt_content

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
            if video_info["captions"]:
                caption_options = {f"{caption['snippet']['language']} ({caption['snippet']['trackKind']})": caption['id'] for caption in video_info["captions"]}
                selected_caption = st.selectbox("다운로드할 자막을 선택하세요:", list(caption_options.keys()))
                
                if st.button("선택한 자막 다운로드"):
                    caption_id = caption_options[selected_caption]
                    caption_content = download_caption(caption_id)
                    if caption_content:
                        srt_content = parse_ttml_to_srt(caption_content)
                        b64 = base64.b64encode(srt_content.encode()).decode()
                        href = f'<a href="data:text/plain;base64,{b64}" download="{video_info["title"]}.srt">자막 파일 다운로드 (.srt)</a>'
                        st.markdown(href, unsafe_allow_html=True)
            else:
                st.write("이 동영상에는 사용 가능한 자막이 없습니다.")
            
            st.subheader("오디오 정보")
            st.write("YouTube는 동영상의 오디오 트랙에 대한 직접적인 정보를 제공하지 않습니다.")
            st.write("그러나 다음과 같은 방법으로 오디오를 합법적으로 즐길 수 있습니다:")
            youtube_music_url = f"https://music.youtube.com/watch?v={video_id}"
            st.markdown(f"[YouTube Music에서 열기]({youtube_music_url})")
            
            st.subheader("동영상 미리보기")
            st.video(url)
    else:
        st.error("유효한 YouTube URL을 입력해주세요.")
else:
    st.info("YouTube 동영상 링크를 입력하면 정보를 표시합니다.")

st.write("참고: 이 애플리케이션은 YouTube Data API를 사용합니다.")
st.write("주의: 저작권을 존중하며 합법적인 방법으로만 콘텐츠를 이용해 주세요.")
