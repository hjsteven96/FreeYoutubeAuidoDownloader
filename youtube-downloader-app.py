import streamlit as st
import yt_dlp
import json

def get_video_info(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'writesubtitles': True,
        'allsubtitles': True,
        'skip_download': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info['title'],
                'thumbnail': info['thumbnail'],
                'channel': info['channel'],
                'duration': f"{info['duration'] // 60}:{info['duration'] % 60:02d}",
                'subtitles': info.get('subtitles', {}),
                'automatic_captions': info.get('automatic_captions', {})
            }
    except Exception as e:
        st.error(f"동영상 정보를 가져오는 중 오류 발생: {str(e)}")
        return {'error': str(e)}

def download_subtitle(url, lang, subtitle_type='subtitles'):
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'subtitleslangs': [lang],
        'subtitlesformat': 'srt',
        'outtmpl': '%(title)s.%(ext)s'
    }
    if subtitle_type == 'automatic_captions':
        ydl_opts['writeautomaticsub'] = True
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return f"{info['title']}.{lang}.srt"

st.set_page_config(page_title="YouTube 자막 다운로더", page_icon="📝")
st.title("YouTube 자막 다운로더")

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
            
            st.subheader("자막 다운로드 옵션")
            
            subtitle_options = []
            for subtitle_type in ['subtitles', 'automatic_captions']:
                for lang, subtitles in video_info[subtitle_type].items():
                    subtitle_options.append((lang, subtitle_type))
            
            if subtitle_options:
                selected_lang, selected_type = st.selectbox(
                    "언어 및 자막 유형을 선택하세요:",
                    options=subtitle_options,
                    format_func=lambda x: f"{x[0]} ({'자막' if x[1] == 'subtitles' else '자동 생성'})"
                )
                
                if st.button("자막 다운로드"):
                    try:
                        subtitle_file = download_subtitle(url, selected_lang, selected_type)
                        st.success(f"자막 다운로드 완료: {subtitle_file}")
                        
                        with open(subtitle_file, 'r', encoding='utf-8') as file:
                            subtitle_content = file.read()
                        
                        st.download_button(
                            label="자막 파일 다운로드",
                            data=subtitle_content,
                            file_name=subtitle_file,
                            mime="text/plain"
                        )
                    except Exception as e:
                        st.error(f"자막 다운로드 중 오류 발생: {str(e)}")
            else:
                st.warning("이 동영상에는 사용 가능한 자막이 없습니다.")
        else:
            st.error(f"동영상 정보를 가져오는 데 실패했습니다. 다른 URL을 시도해보세요.")
    else:
        st.warning("URL을 입력해주세요.")

st.write("yt-dlp 버전 정보:")
st.code(f"!pip show yt-dlp")
