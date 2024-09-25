import streamlit as st
import io
import re
from pytubefix import YouTube

def is_valid_youtube_url(url):
    # YouTube URL 패턴
    pattern = r'^(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+'
    return re.match(pattern, url) is not None

def get_video_info(url):
    try:
        yt = YouTube(url)
        yt.check_availability()  # 동영상 사용 가능 여부 확인
        return {
            'title': yt.title,
            'thumbnail': yt.thumbnail_url,
            'channel': yt.author,
            'duration': f"{yt.length // 60}:{yt.length % 60:02d}",
            'streams': yt.streams.filter(only_audio=True)
        }
    except Exception as e:
        return {'error': f"동영상 정보를 가져오는 중 오류가 발생했습니다: {str(e)}"}

def format_filesize(bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024
    return f"{bytes:.2f} TB"

st.set_page_config(page_title="YouTube Downloader", page_icon="🎵")
st.title("YouTube 음원 다운로더")

col1, col2 = st.columns([4, 1])
with col1:
    url = st.text_input("YouTube 링크를 입력하세요:", key="url_input")
with col2:
    enter_button = st.button("Enter", key="enter_button")

if enter_button or st.session_state.url_input:
    if not is_valid_youtube_url(st.session_state.url_input):
        st.error("URL 형식을 확인해 주세요")
    else:
        video_info = get_video_info(st.session_state.url_input)
        
        if 'error' not in video_info:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.image(video_info['thumbnail'], use_column_width=True)
            
            with col2:
                st.markdown(f"**[{video_info['title']}]({st.session_state.url_input})**")
                st.write(f"채널명: {video_info['channel']}")
                st.write(f"재생 시간: {video_info['duration']}")
            
            st.subheader("음원 다운로드 옵션")
            for stream in video_info['streams']:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"{stream.abr} ({stream.mime_type.split('/')[1]})")
                with col2:
                    st.write(format_filesize(stream.filesize))
                with col3:
                    if st.button("다운로드", key=stream.itag):
                        try:
                            buffer = io.BytesIO()
                            stream.stream_to_buffer(buffer)
                            buffer.seek(0)
                            st.download_button(
                                label="파일 다운로드",
                                data=buffer,
                                file_name=f"{video_info['title']}.{stream.mime_type.split('/')[1]}",
                                mime=stream.mime_type
                            )
                        except Exception as e:
                            st.error(f"다운로드 중 오류 발생: {str(e)}")
        else:
            st.error(video_info['error'])
