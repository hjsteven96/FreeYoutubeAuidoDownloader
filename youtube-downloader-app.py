import streamlit as st
import requests

try:
    from pytubefix import YouTube
    from pytubefix.exceptions import PytubeError
except ImportError:
    st.error("pytubefix 라이브러리가 설치되지 않았습니다. 'pip install pytubefix'를 실행하여 설치해주세요.")
    st.stop()

def get_video_info(url):
    st.write(f"처리 중인 URL: {url}")  # URL 확인을 위해 추가
    try:
        yt = YouTube(url)
        return {
            'title': yt.title,
            'thumbnail': yt.thumbnail_url,
            'channel': yt.author,
            'duration': f"{yt.length // 60}:{yt.length % 60:02d}",
            'streams': yt.streams.filter(only_audio=True)
        }
    except PytubeError as e:
        st.error(f"PytubeError: {str(e)}")
        return {'error': str(e)}
    except Exception as e:
        st.error(f"예상치 못한 오류: {str(e)}")
        return {'error': f"예상치 못한 오류가 발생했습니다: {str(e)}"}

def format_filesize(bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024
    return f"{bytes:.2f} TB"

st.set_page_config(page_title="YouTube Downloader", page_icon="🎵")
st.title("YouTube 음원 다운로더")

url = st.text_input("YouTube 링크를 입력하세요:", key="url_input")
enter_button = st.button("Enter")

if enter_button or st.session_state.url_input:
    url = st.session_state.url_input
    st.write(f"입력된 URL: {url}")  # 입력된 URL 확인
    
    if url:  # URL이 비어있지 않은 경우에만 처리
        video_info = get_video_info(url)
        
        if 'error' not in video_info:
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
            st.error(f"동영상 정보를 가져오는 중 오류가 발생했습니다: {video_info['error']}")
    else:
        st.warning("URL을 입력해주세요.")
