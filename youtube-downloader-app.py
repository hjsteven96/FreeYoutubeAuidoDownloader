import streamlit as st
import yt_dlp
import os

def get_video_info(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {'youtube': {'player_client': ['android']}},
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info['title'],
                'thumbnail': info['thumbnail'],
                'channel': info['channel'],
                'duration': f"{info['duration'] // 60}:{info['duration'] % 60:02d}",
                'formats': [f for f in info['formats'] if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
            }
    except yt_dlp.utils.DownloadError as e:
        if "Sign in to confirm you're not a bot" in str(e):
            st.error("YouTube가 봇 확인을 요구하고 있습니다. 브라우저에서 직접 YouTube에 로그인한 후 다시 시도해주세요.")
            st.info("또는 잠시 후에 다시 시도해보세요. 이 문제는 일시적일 수 있습니다.")
        else:
            st.error(f"동영상 정보를 가져오는 중 오류 발생: {str(e)}")
        return {'error': str(e)}
    except Exception as e:
        st.error(f"예상치 못한 오류 발생: {str(e)}")
        return {'error': str(e)}

def format_filesize(bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024
    return f"{bytes:.2f} TB"

def download_audio(url, format_id):
    ydl_opts = {
        'format': format_id,
        'outtmpl': '%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'extractor_args': {'youtube': {'player_client': ['android']}},
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return os.path.join(os.getcwd(), f"{info['title']}.mp3")

st.set_page_config(page_title="YouTube Downloader", page_icon="🎵")
st.title("YouTube 음원 다운로더")

url = st.text_input("YouTube 링크를 입력하세요:", key="url_input")
enter_button = st.button("Enter")

if enter_button or st.session_state.url_input:
    url = st.session_state.url_input
    st.write(f"입력된 URL: {url}")
    
    if url:
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
            for format in video_info['formats']:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"{format['acodec']} - {format.get('abr', 'Unknown')}kbps")
                with col2:
                    st.write(format_filesize(format['filesize']) if format.get('filesize') else 'Unknown size')
                with col3:
                    if st.button("다운로드", key=format['format_id']):
                        try:
                            download_path = download_audio(url, format['format_id'])
                            st.success(f"다운로드 완료: {download_path}")
                        except Exception as e:
                            st.error(f"다운로드 중 오류 발생: {str(e)}")
        else:
            st.error(f"동영상 정보를 가져오는 데 실패했습니다. 다른 URL을 시도해보세요.")
    else:
        st.warning("URL을 입력해주세요.")

st.write("yt-dlp 버전 정보:")
st.code(f"!pip show yt-dlp")
