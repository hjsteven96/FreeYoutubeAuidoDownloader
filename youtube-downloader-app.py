import streamlit as st
import io
import re
from pytubefix import YouTube

def is_valid_youtube_url(url):
    pattern = r'^(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+'
    return re.match(pattern, url) is not None

def get_video_info(url):
    try:
        yt = YouTube(url)
        return {
            'title': yt.title,
            'thumbnail': yt.thumbnail_url,
            'channel': yt.author,
            'duration': f"{yt.length // 60}:{yt.length % 60:02d}",
            'stream': yt.streams.get_audio_only()
        }
    except Exception as e:
        return {'error': f"동영상 정보를 가져오는 중 오류가 발생했습니다: {str(e)}"}

st.set_page_config(page_title="YouTube Downloader", page_icon="🎵")
st.title("YouTube 음원 다운로더")

st.markdown("""
<style>
div.row-widget.stButton > button {
    background-color: black;
    color: white;
    border: none;
    height: 3em;
}
div.row-widget.stTextInput > div > div > input {
    background-color: white;
}
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([5,1])
with col1:
    url = st.text_input("YouTube 링크를 입력하세요:", key="url_input")
with col2:
    enter_button = st.button("Enter")

if enter_button or st.session_state.url_input:
    if not is_valid_youtube_url(st.session_state.url_input):
        st.error("올바른 YouTube URL 형식이 아닙니다. 다시 확인해주세요.")
    else:
        with st.spinner('동영상 정보를 가져오는 중...'):
            video_info = get_video_info(st.session_state.url_input)
        
        if 'error' not in video_info:
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(video_info['thumbnail'], use_column_width=True)
            with col2:
                st.markdown(f"**[{video_info['title']}]({st.session_state.url_input})**")
                st.write(f"채널명: {video_info['channel']}")
                st.write(f"재생 시간: {video_info['duration']}")
            
            if st.button("음원 다운로드"):
                try:
                    buffer = io.BytesIO()
                    video_info['stream'].download(output_buffer=buffer, mp3=True)
                    buffer.seek(0)
                    
                    st.download_button(
                        label="MP3 파일 다운로드",
                        data=buffer,
                        file_name=f"{video_info['title']}.mp3",
                        mime="audio/mp3"
                    )
                except Exception as e:
                    st.error(f"다운로드 중 오류 발생: {str(e)}")
        else:
            st.error(video_info['error'])
            st.write("문제 해결 방법:")
            st.write("1. 잠시 후 다시 시도해보세요. YouTube의 일시적인 제한일 수 있습니다.")
            st.write("2. 다른 YouTube 동영상 링크를 시도해보세요.")
            st.write("3. 이 동영상이 귀하의 지역에서 제한되어 있거나, 비공개 또는 삭제되었을 수 있습니다.")
            st.write("4. YouTube의 서비스 약관을 확인하세요. 일부 콘텐츠는 다운로드가 제한될 수 있습니다.")
