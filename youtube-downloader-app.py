import streamlit as st

def count_characters(text):
    with_spaces = len(text)
    without_spaces = len(text.replace(" ", ""))
    return with_spaces, without_spaces

st.title("실시간 글자 수 계산기")

# 결과를 표시할 빈 요소 생성
result = st.empty()

def update_count():
    # 현재 입력된 텍스트에 대해 글자 수 계산
    char_count_with_spaces, char_count_without_spaces = count_characters(user_input)
    
    # 결과 업데이트
    result.write(f"공백 포함 글자 수: {char_count_with_spaces}\n"
                 f"공백 제거 글자 수: {char_count_without_spaces}")

# 텍스트 입력 영역 생성 (콜백 함수 지정)
user_input = st.text_area("텍스트를 입력하세요:", on_change=update_count)

# 초기 상태 표시
if not user_input:
    result.write("텍스트를 입력하면 실시간으로 글자 수가 여기에 표시됩니다.")
else:
    update_count()
