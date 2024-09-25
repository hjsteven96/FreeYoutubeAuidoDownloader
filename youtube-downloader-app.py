import streamlit as st
from pytubefix import YouTube
import os
import re

def get_video_info(url):
    try:
        yt = YouTube(url)
        captions = yt.captions
        st.write(f"Debug: 가져온 자막 정보: {captions}")  # 디버그 정보 추가
        
        # 자막이 비어있을 경우 다시 한 번 시도
        if not captions:
            yt = YouTube(url)
            captions = yt.captions
            st.write(f"Debug: 두 번째 시도 자막 정보: {captions}")  # 디버그 정보 추가
        
        return {
            'title': yt.title,
            'thumbnail': yt.thumbnail_url,
            'channel': yt.author,
            'duration': f"{yt.length // 60}:{yt.length % 60:02d}",
            'captions': captions
        }
    except Exception as e:
        st.error(f"동영상 정보를 가져오는 중 오류 발생: {str(e)}")
        return {'error': str(e)}

def download_subtitle(url, lang_code):
    try:
        yt = YouTube(url)
        caption = yt.captions[lang_code]
        srt_caption = caption.generate_srt_captions()
        
        # 파일명에서 부적절한 문자 제거
        filename = re.sub(r'[^\w\-_\. ]', '_', yt.title)
        filepath = f"{filename}_{lang_code}.srt"
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(srt_caption)
        
        return filepath
    except Exception as e:
        st.error(f"자막 다운로드 중 오류 발생: {str(e)}")
        return None

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
            
            available_captions = list(video_info['captions'].keys())
            st.write(f"Debug: 사용 가능한 자막: {available_captions}")  # 디버그 정보 추가
            
            if available_captions:
                selected_lang = st.selectbox(
                    "언어를 선택하세요:",
                    options=available_captions,
                    format_func=lambda x: f"{x} ({video_info['captions'][x].name})"
                )
                
                if st.button("자막 다운로드"):
                    subtitle_file = download_subtitle(url, selected_lang)
                    if subtitle_file:
                        st.success(f"자막 다운로드 완료: {subtitle_file}")
                        
                        with open(subtitle_file, 'r', encoding='utf-8') as file:
                            subtitle_content = file.read()
                        
                        st.download_button(
                            label="자막 파일 다운로드",
                            data=subtitle_content,
                            file_name=subtitle_file,
                            mime="text/plain"
                        )
                        
                        # 파일 삭제
                        os.remove(subtitle_file)
            else:
                st.warning("이 동영상에는 사용 가능한 자막이 없습니다.")
        else:
            st.error(f"동영상 정보를 가져오는 데 실패했습니다. 다른 URL을 시도해보세요.")
    else:
        st.warning("URL을 입력해주세요.")

st.write("pytubefix 버전 정보:")
st.code(f"!pip show pytubefix")
