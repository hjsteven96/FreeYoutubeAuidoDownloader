import streamlit as st

def count_characters(text):
    with_spaces = len(text)
    without_spaces = len(text.replace(" ", ""))
    return with_spaces, without_spaces

st.title("글자 수 계산기")

user_input = st.text_area("텍스트를 입력하세요:")

if user_input:
    char_count_with_spaces, char_count_without_spaces = count_characters(user_input)
    st.write(f"공백 포함 글자 수: {char_count_with_spaces}")
    st.write(f"공백 제거 글자 수: {char_count_without_spaces}")
else:
    st.write("텍스트를 입력하면 글자 수가 여기에 표시됩니다.")
