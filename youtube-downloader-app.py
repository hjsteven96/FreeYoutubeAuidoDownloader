import streamlit as st
import requests
from pytubefix import YouTube
from pytubefix.exceptions import RegexMatchError, VideoUnavailable
import re

def get_video_info(url):
    try:
        yt = YouTube(url)
        return {
            'title': yt.title,
            'thumbnail': yt.thumbnail_url,
            'channel': yt.author,
            'duration': f"{yt.length // 60}:{yt.length % 60:02d}",
            'streams': yt.streams.filter(only_audio=True)
        }
    except (RegexMatchError, VideoUnavailable):
        return None

def format_filesize(bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024
    return f"{bytes:.2f} TB"

st.set_page_config(page_title="YouTube Downloader", page_icon="🎵")
st.title("YouTube 음원 다운로더")

url = st.text_input("YouTube 링크를 입력하세요:")

if url:
    video_info = get_video_info(url)
    
    if video_info:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(video_info['thumbnail'], use_column_width=True)
        
        with col2:
            st.markdown(f"**[{video_info['title']}]({url})**")
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
                        download_path = stream.download()
                        st.success(f"다운로드 완료: {download_path}")
                    except Exception as e:
                        st.error(f"다운로드 중 오류 발생: {str(e)}")
    else:
        st.error("유효하지 않은 YouTube 링크입니다. 다시 확인해주세요.")
