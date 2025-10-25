import streamlit as st
import yaml
import os
from pathlib import Path

# 보안 참고사항:
# 이 구현은 개발/데모 목적입니다. 프로덕션 환경에서는:
# - 비밀번호 해싱 (bcrypt, argon2 등) 구현
# - 마크다운 콘텐츠 sanitization (unsafe_allow_html 사용 시 XSS 위험)
# - 환경 변수를 통한 민감 정보 관리
# - HTTPS 사용 필수

# 페이지 설정
st.set_page_config(
    page_title="Bluhill Documentation",
    page_icon="📚",
    layout="wide"
)

# 사용자 데이터 로드
@st.cache_resource
def load_users():
    """users.yaml 파일에서 사용자 정보를 로드합니다."""
    try:
        with open('users.yaml', 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data.get('users', {})
    except FileNotFoundError:
        st.error("users.yaml 파일을 찾을 수 없습니다.")
        return {}

# 세션 상태 초기화
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'role' not in st.session_state:
    st.session_state.role = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None

def login(username, password):
    """사용자 로그인을 처리합니다."""
    users = load_users()
    if username in users and users[username]['password'] == password:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.role = users[username]['role']
        st.session_state.user_name = users[username]['name']
        return True
    return False

def logout():
    """사용자 로그아웃을 처리합니다."""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.user_name = None

def load_markdown_file(filepath):
    """마크다운 파일을 읽어 반환합니다."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"⚠️ 파일을 찾을 수 없습니다: {filepath}"
    except Exception as e:
        return f"⚠️ 파일을 읽는 중 오류가 발생했습니다: {str(e)}"

def list_markdown_files(directory):
    """디렉토리 내의 마크다운 파일 목록을 반환합니다."""
    path = Path(directory)
    if not path.exists():
        return []
    return sorted([f.name for f in path.glob('*.md')])

def display_content(content_type):
    """콘텐츠 타입에 따라 마크다운 파일을 표시합니다."""
    directory_map = {
        'public': 'content/public',
        'user': 'content/user',
        'special': 'content/special'
    }
    
    directory = directory_map.get(content_type)
    if not directory:
        return
    
    files = list_markdown_files(directory)
    
    if not files:
        st.info(f"📄 {content_type} 콘텐츠가 아직 없습니다.")
        return
    
    # 파일 선택
    selected_file = st.selectbox(
        f"📄 {content_type.upper()} 문서 선택",
        files,
        key=f"file_select_{content_type}"
    )
    
    if selected_file:
        # 경로 순회 공격 방지: 파일명에 '..' 또는 경로 구분자가 없는지 확인
        if '..' in selected_file or os.path.sep in selected_file:
            st.error("⚠️ 잘못된 파일명입니다.")
            return
        
        filepath = os.path.join(directory, selected_file)
        # 최종 경로가 의도한 디렉토리 내에 있는지 확인
        if not os.path.abspath(filepath).startswith(os.path.abspath(directory)):
            st.error("⚠️ 잘못된 파일 경로입니다.")
            return
        
        content = load_markdown_file(filepath)
        st.markdown(content, unsafe_allow_html=True)

# 메인 애플리케이션
def main():
    # 사이드바 - 로그인/로그아웃
    with st.sidebar:
        st.title("🔐 인증")
        
        if not st.session_state.logged_in:
            st.subheader("로그인")
            username = st.text_input("사용자명", key="login_username")
            password = st.text_input("비밀번호", type="password", key="login_password")
            
            if st.button("로그인", use_container_width=True):
                if login(username, password):
                    st.success(f"환영합니다, {st.session_state.user_name}님!")
                    st.rerun()
                else:
                    st.error("사용자명 또는 비밀번호가 잘못되었습니다.")
        else:
            st.success(f"👤 {st.session_state.user_name}")
            st.info(f"🎭 역할: {st.session_state.role}")
            
            if st.button("로그아웃", use_container_width=True):
                logout()
                st.rerun()
        
        st.divider()
        
        # 사용자 안내
        with st.expander("ℹ️ 테스트 계정"):
            st.markdown("""
            **일반 사용자:**
            - user1 / password1
            - user2 / password2
            
            **특별 사용자:**
            - special1 / special123
            - special2 / special456
            
            **관리자:**
            - admin1 / admin123
            """)
    
    # 메인 콘텐츠 영역
    st.title("📚 Bluhill 문서")
    
    # 탭 생성
    tabs = ["🌐 공개 콘텐츠"]
    if st.session_state.logged_in:
        tabs.append("👤 사용자 콘텐츠")
    if st.session_state.logged_in and st.session_state.role in ['special', 'admin']:
        tabs.append("⭐ 특별 콘텐츠")
    
    selected_tab = st.tabs(tabs)
    
    # 공개 콘텐츠 탭
    with selected_tab[0]:
        st.header("🌐 공개 콘텐츠")
        st.info("누구나 볼 수 있는 공개 문서입니다.")
        display_content('public')
    
    # 사용자 콘텐츠 탭
    if st.session_state.logged_in:
        with selected_tab[1]:
            st.header("👤 사용자 콘텐츠")
            st.info("로그인한 사용자만 볼 수 있는 문서입니다.")
            display_content('user')
    
    # 특별 콘텐츠 탭
    if st.session_state.logged_in and st.session_state.role in ['special', 'admin']:
        with selected_tab[2]:
            st.header("⭐ 특별 콘텐츠")
            st.info("관리자가 승인한 특별 사용자만 볼 수 있는 문서입니다.")
            display_content('special')

if __name__ == "__main__":
    main()
