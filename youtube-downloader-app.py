import streamlit as st
import io
import re
import yt_dlp

def is_valid_youtube_url(url):
    pattern = r'^(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+'
    return re.match(pattern, url) is not None

def get_video_info(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'no-check-certificate': True,
        'ignoreerrors': False,
        'no_warnings': False,
        'quiet': False,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info is None:
                raise Exception("동영상 정보를 가져올 수 없습니다.")
            return {
                'title': info.get('title', 'Unknown Title'),
                'thumbnail': info.get('thumbnail', ''),
                'channel': info.get('uploader', 'Unknown Uploader'),
                'duration': f"{info.get('duration', 0) // 60}:{info.get('duration', 0) % 60:02d}",
                'formats': [f for f in info.get('formats', []) if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
            }
    except yt_dlp.utils.DownloadError as e:
        return {'error': str(e)}
    except Exception as e:
        return {'error': f"예상치 못한 오류가 발생했습니다: {str(e)}"}

def format_filesize(bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024
    return f"{bytes:.2f} TB"

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
            
            st.subheader("음원 다운로드 옵션")
            for format in video_info['formats']:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"{format.get('acodec', 'Unknown')} ({format.get('ext', 'Unknown')})")
                with col2:
                    st.write(format_filesize(format.get('filesize', 0)))
                with col3:
                    if st.button("다운로드", key=format['format_id']):
                        try:
                            ydl_opts = {
                                'format': format['format_id'],
                                'outtmpl': '%(title)s.%(ext)s',
                            }
                            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                                info = ydl.extract_info(st.session_state.url_input, download=False)
                                filename = ydl.prepare_filename(info)
                                ydl.download([st.session_state.url_input])
                            
                            with open(filename, "rb") as file:
                                btn = st.download_button(
                                    label="파일 다운로드",
                                    data=file,
                                    file_name=filename,
                                    mime=f"audio/{format.get('ext', 'mp3')}"
                                )
                        except Exception as e:
                            st.error(f"다운로드 중 오류 발생: {str(e)}")
        else:
            st.error(video_info['error'])
            st.write("문제 해결 방법:")
            st.write("1. 입력한 URL이 올바른지 다시 한 번 확인해주세요.")
            st.write("2. 잠시 후 다시 시도해보세요. YouTube 서버 문제일 수 있습니다.")
            st.write("3. 다른 YouTube 동영상 링크를 시도해보세요.")
            st.write("4. 이 동영상이 귀하의 지역에서 제한되어 있거나, 비공개 또는 삭제되었을 수 있습니다.")
            st.write("5. YouTube의 서비스 약관을 확인하세요. 일부 콘텐츠는 다운로드가 제한될 수 있습니다.")
