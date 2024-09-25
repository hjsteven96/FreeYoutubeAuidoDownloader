import streamlit as st
from streamlit.components.v1 import html

def count_characters(text):
    with_spaces = len(text)
    without_spaces = len(text.replace(" ", ""))
    return with_spaces, without_spaces

st.title("실시간 글자 수 계산기")

# JavaScript 코드
js_code = """
<script>
function updateCount() {
    const text = document.getElementById('text-input').value;
    const withSpaces = text.length;
    const withoutSpaces = text.replace(/\s/g, '').length;
    document.getElementById('result').innerText = `공백 포함 글자 수: ${withSpaces}\n공백 제거 글자 수: ${withoutSpaces}`;
}
</script>
"""

# HTML 코드
html_code = f"""
{js_code}
<textarea id="text-input" oninput="updateCount()" rows="5" style="width: 100%; padding: 10px;"></textarea>
<div id="result" style="margin-top: 10px;">텍스트를 입력하면 실시간으로 글자 수가 여기에 표시됩니다.</div>
"""

# HTML 컴포넌트 렌더링
html(html_code, height=200)

st.markdown("---")
st.write("위의 텍스트 영역에 글자를 입력하면 실시간으로 글자 수가 업데이트됩니다.")
