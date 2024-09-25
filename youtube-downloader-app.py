import streamlit as st
from pytubefix import YouTube
import os
import re
import requests
import xml.etree.ElementTree as ET
import asyncio
import concurrent.futures

async def get_video_info(url):
    try:
        with st.spinner('동영상 정보를 가져오는 중...'):
            loop = asyncio.get_event_loop()
            yt = await loop.run_in_executor(None, YouTube, url)
            captions = await loop.run_in_executor(None, lambda: yt.captions)
            st.write(f"Debug: pytubefix로 가져온 자막 정보: {captions}")

            # pytubefix로 자막을 가져오지 못한 경우 대체 방법 시도
            if not captions:
                captions = await get_captions_alternative(yt.video_id)
                st.write(f"Debug: 대체 방법으로 가져온 자막 정보: {captions}")

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

async def get_captions_alternative(video_id):
    try:
        captions_url = f"https://www.youtube.com/api/timedtext?v={video_id}&type=list"
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, requests.get, captions_url)
        root = ET.fromstring(response.content)

        captions = {}
        for track in root.findall('track'):
            lang_code = track.get('lang_code')
            lang_name = track.get('lang_translated')
            captions[lang_code] = {'name': lang_name}

        return captions
    except Exception as e:
        st.error(f"대체 방법으로 자막 정보를 가져오는 중 오류 발생: {str(e)}")
        return {}

async def download_subtitle(video_id, lang_code):
    try:
        subtitle_url = f"https://www.youtube.com/api/timedtext?v={video_id}&lang={lang_code}"
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, requests.get, subtitle_url)
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            srt_captions = convert_to_srt(root)
            
            filename = f"subtitle_{video_id}_{lang_code}.srt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(srt_captions)
            
            return filename
        else:
            st.error("자막을 다운로드할 수 없습니다.")
            return None
    except Exception as e:
        st.error(f"자막 다운로드 중 오류 발생: {str(e)}")
        return None

def convert_to_srt(root):
    srt_lines = []
    index = 1
    for i, text in enumerate(root.findall('text')):
        start = float(text.get('start'))
        duration = float(text.get('dur')) if text.get('dur') else 0
        end = start + duration
        
        srt_lines.append(f"{index}")
        srt_lines.append(f"{format_time(start)} --> {format_time(end)}")
        srt_lines.append(text.text if text.text else "")
        srt_lines.append("")
        
        index += 1
    
    return "\n".join(srt_lines)

def format_time(seconds):
    hours = int(seconds / 3600)
    minutes = int((seconds % 3600) / 60)
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}".replace(".", ",")

st.set_page_config(page_title="YouTube 자막 다운로더", page_icon="📝")
st.title("YouTube 자막 다운로더")

url = st.text_input("YouTube 링크를 입력하세요:", key="url_input")
enter_button = st.button("Enter")

if enter_button or st.session_state.url_input:
    url = st.session_state.url_input
    st.write(f"입력된 URL: {url}")
    
    if url:
        video_info = asyncio.run(get_video_info(url))
        
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
            st.write(f"Debug: 사용 가능한 자막: {available_captions}")
            
            if available_captions:
                selected_lang = st.selectbox(
                    "언어를 선택하세요:",
                    options=available_captions,
                    format_func=lambda x: f"{x} ({video_info['captions'][x]['name']})"
                )
                
                if st.button("자막 다운로드"):
                    with st.spinner('자막을 다운로드하는 중...'):
                        video_id = YouTube(url).video_id
                        subtitle_file = asyncio.run(download_subtitle(video_id, selected_lang))
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
