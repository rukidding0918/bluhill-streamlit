import streamlit as st
import yaml
import os
from pathlib import Path
from datetime import datetime
import uuid

# 보안 참고사항:
# 이 구현은 개발/데모 목적입니다. 프로덕션 환경에서는:
# - 비밀번호 해싱 (bcrypt, argon2 등) 구현
# - 마크다운 콘텐츠 sanitization (unsafe_allow_html 사용 시 XSS 위험)
# - 환경 변수를 통한 민감 정보 관리
# - HTTPS 사용 필수

# 페이지 설정
st.set_page_config(
    page_title="블루힐 한의원",
    page_icon="🏥",
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

# 데이터 로드 함수들
def load_data(filename):
    """YAML 파일에서 데이터를 로드합니다."""
    try:
        filepath = f'data/{filename}'
        if not os.path.exists(filepath):
            return []
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            # inquiries, reviews, columns 키에서 데이터 추출
            key = filename.replace('.yaml', '')
            return data.get(key, []) if data else []
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {str(e)}")
        return []

def save_data(filename, data):
    """데이터를 YAML 파일에 저장합니다."""
    try:
        filepath = f'data/{filename}'
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        key = filename.replace('.yaml', '')
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump({key: data}, f, allow_unicode=True, default_flow_style=False)
        return True
    except Exception as e:
        st.error(f"데이터 저장 중 오류 발생: {str(e)}")
        return False

# 세션 상태 초기화
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'role' not in st.session_state:
    st.session_state.role = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'selected_menu' not in st.session_state:
    st.session_state.selected_menu = '의료진'
if 'selected_category' not in st.session_state:
    st.session_state.selected_category = '한의원'

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

def display_markdown_content(filename):
    """마크다운 콘텐츠를 표시합니다."""
    filepath = os.path.join('content/public', filename)

    # 경로 순회 공격 방지
    if '..' in filename or os.path.sep in filename:
        st.error("⚠️ 잘못된 파일명입니다.")
        return

    if not os.path.abspath(filepath).startswith(os.path.abspath('content/public')):
        st.error("⚠️ 잘못된 파일 경로입니다.")
        return

    content = load_markdown_file(filepath)

    # 칼럼 페이지인 경우 저장된 칼럼 목록도 표시
    if filename == "03_칼럼.md":
        st.markdown(content)
        st.divider()

        columns_data = load_data('columns.yaml')
        if columns_data:
            st.subheader("📰 작성된 칼럼")
            for col in sorted(columns_data, key=lambda x: x['created_at'], reverse=True):
                with st.expander(f"📝 {col['title']} - {col['created_at'][:10]}"):
                    st.markdown(f"**작성자**: {col['author']}")
                    st.markdown(f"**작성일**: {col['created_at']}")
                    st.divider()
                    st.markdown(col['content'])
        else:
            st.info("아직 작성된 칼럼이 없습니다.")
    else:
        st.markdown(content)

def show_inquiry_page():
    """문의 페이지를 표시합니다."""
    st.header("💬 문의하기")

    if st.session_state.logged_in:
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("💬 문의글 작성")
            with st.form("inquiry_form"):
                title = st.text_input("제목", max_chars=100)
                content = st.text_area("내용", height=200)
                is_private = st.checkbox("비공개 문의 (작성자와 관리자만 볼 수 있습니다)")

                submitted = st.form_submit_button("문의글 등록", use_container_width=True)

                if submitted:
                    if not title or not content:
                        st.error("제목과 내용을 모두 입력해주세요.")
                    else:
                        inquiries = load_data('inquiries.yaml')
                        new_inquiry = {
                            'id': str(uuid.uuid4()),
                            'author': st.session_state.username,
                            'author_name': st.session_state.user_name,
                            'title': title,
                            'content': content,
                            'is_private': is_private,
                            'answered': False,
                            'answer': None,
                            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        inquiries.append(new_inquiry)
                        if save_data('inquiries.yaml', inquiries):
                            st.success("문의글이 등록되었습니다!")
                            st.rerun()

        with col2:
            st.subheader("💬 문의글 목록")
            inquiries = load_data('inquiries.yaml')

            if not inquiries:
                st.info("아직 작성된 문의글이 없습니다.")
            else:
                # 사용자별 필터링
                if st.session_state.role != 'admin':
                    inquiries = [
                        inq for inq in inquiries
                        if not inq['is_private'] or inq['author'] == st.session_state.username
                    ]

                for inq in sorted(inquiries, key=lambda x: x['created_at'], reverse=True):
                    privacy_badge = "🔒 비공개" if inq['is_private'] else "🌐 공개"
                    answer_badge = "✅ 답변완료" if inq['answered'] else "⏳ 대기중"

                    with st.expander(f"{privacy_badge} {answer_badge} | {inq['title']} - {inq['author_name']} ({inq['created_at'][:10]})"):
                        st.markdown(f"**작성자**: {inq['author_name']}")
                        st.markdown(f"**작성일**: {inq['created_at']}")
                        st.markdown(f"**공개여부**: {privacy_badge}")
                        st.divider()
                        st.markdown("**문의 내용:**")
                        st.write(inq['content'])

                        if inq['answered']:
                            st.divider()
                            st.markdown("**답변:**")
                            st.info(inq['answer'])
    else:
        st.warning("⚠️ 문의글 작성은 로그인이 필요합니다.")
        st.divider()

        # 공개 문의글은 비로그인 상태에서도 볼 수 있음
        st.subheader("💬 공개 문의글 목록")
        inquiries = load_data('inquiries.yaml')
        inquiries = [inq for inq in inquiries if not inq['is_private']]

        if not inquiries:
            st.info("아직 작성된 공개 문의글이 없습니다.")
        else:
            for inq in sorted(inquiries, key=lambda x: x['created_at'], reverse=True):
                answer_badge = "✅ 답변완료" if inq['answered'] else "⏳ 대기중"

                with st.expander(f"{answer_badge} | {inq['title']} - {inq['author_name']} ({inq['created_at'][:10]})"):
                    st.markdown(f"**작성자**: {inq['author_name']}")
                    st.markdown(f"**작성일**: {inq['created_at']}")
                    st.divider()
                    st.markdown("**문의 내용:**")
                    st.write(inq['content'])

                    if inq['answered']:
                        st.divider()
                        st.markdown("**답변:**")
                        st.info(inq['answer'])

def show_review_page():
    """후기 페이지를 표시합니다."""
    st.header("⭐ 진료후기")

    if st.session_state.logged_in:
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("⭐ 후기 작성")
            with st.form("review_form"):
                title = st.text_input("제목", max_chars=100)
                content = st.text_area("내용", height=200)

                submitted = st.form_submit_button("후기 등록", use_container_width=True)

                if submitted:
                    if not title or not content:
                        st.error("제목과 내용을 모두 입력해주세요.")
                    else:
                        reviews = load_data('reviews.yaml')
                        new_review = {
                            'id': str(uuid.uuid4()),
                            'author': st.session_state.username,
                            'author_name': st.session_state.user_name,
                            'title': title,
                            'content': content,
                            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        reviews.append(new_review)
                        if save_data('reviews.yaml', reviews):
                            st.success("후기가 등록되었습니다!")
                            st.rerun()

        with col2:
            st.subheader("⭐ 치료 후기 목록")
            reviews = load_data('reviews.yaml')

            if not reviews:
                st.info("아직 작성된 후기가 없습니다.")
            else:
                for review in sorted(reviews, key=lambda x: x['created_at'], reverse=True):
                    with st.expander(f"⭐ {review['title']} - {review['author_name']} ({review['created_at'][:10]})"):
                        st.markdown(f"**작성자**: {review['author_name']}")
                        st.markdown(f"**작성일**: {review['created_at']}")
                        st.divider()
                        st.markdown(review['content'])
    else:
        st.warning("⚠️ 후기 작성은 로그인이 필요합니다.")
        st.divider()

        # 후기는 비로그인 상태에서도 볼 수 있음
        st.subheader("⭐ 치료 후기 목록")
        reviews = load_data('reviews.yaml')

        if not reviews:
            st.info("아직 작성된 후기가 없습니다.")
        else:
            for review in sorted(reviews, key=lambda x: x['created_at'], reverse=True):
                with st.expander(f"⭐ {review['title']} - {review['author_name']} ({review['created_at'][:10]})"):
                    st.markdown(f"**작성자**: {review['author_name']}")
                    st.markdown(f"**작성일**: {review['created_at']}")
                    st.divider()
                    st.markdown(review['content'])

def show_admin_inquiry_management():
    """관리자 문의글 관리 페이지를 표시합니다."""
    st.header("🔧 문의글 관리")

    # 필터
    filter_option = st.radio(
        "필터",
        ["전체", "답변 대기", "답변 완료"],
        horizontal=True
    )

    inquiries = load_data('inquiries.yaml')

    if not inquiries:
        st.info("아직 작성된 문의글이 없습니다.")
        return

    # 필터링
    if filter_option == "답변 대기":
        inquiries = [inq for inq in inquiries if not inq['answered']]
    elif filter_option == "답변 완료":
        inquiries = [inq for inq in inquiries if inq['answered']]

    for idx, inq in enumerate(sorted(inquiries, key=lambda x: x['created_at'], reverse=True)):
        privacy_badge = "🔒 비공개" if inq['is_private'] else "🌐 공개"
        answer_badge = "✅ 답변완료" if inq['answered'] else "⏳ 대기중"

        with st.expander(f"{privacy_badge} {answer_badge} | {inq['title']} - {inq['author_name']} ({inq['created_at'][:10]})"):
            st.markdown(f"**작성자**: {inq['author_name']} ({inq['author']})")
            st.markdown(f"**작성일**: {inq['created_at']}")
            st.markdown(f"**공개여부**: {privacy_badge}")
            st.divider()
            st.markdown("**문의 내용:**")
            st.write(inq['content'])

            st.divider()

            # 답변 폼
            if inq['answered']:
                st.markdown("**답변:**")
                st.info(inq['answer'])
                if st.button("답변 수정", key=f"edit_{inq['id']}"):
                    st.session_state[f"editing_{inq['id']}"] = True
                    st.rerun()

                if st.session_state.get(f"editing_{inq['id']}", False):
                    new_answer = st.text_area("답변 수정", value=inq['answer'], key=f"answer_edit_{inq['id']}")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("수정 완료", key=f"save_edit_{inq['id']}", use_container_width=True):
                            all_inquiries = load_data('inquiries.yaml')
                            for i, item in enumerate(all_inquiries):
                                if item['id'] == inq['id']:
                                    all_inquiries[i]['answer'] = new_answer
                                    break
                            if save_data('inquiries.yaml', all_inquiries):
                                st.session_state[f"editing_{inq['id']}"] = False
                                st.success("답변이 수정되었습니다!")
                                st.rerun()
                    with col2:
                        if st.button("취소", key=f"cancel_edit_{inq['id']}", use_container_width=True):
                            st.session_state[f"editing_{inq['id']}"] = False
                            st.rerun()
            else:
                answer = st.text_area("답변 작성", key=f"answer_{inq['id']}", height=150)
                if st.button("답변 등록", key=f"submit_{inq['id']}", use_container_width=True):
                    if answer:
                        all_inquiries = load_data('inquiries.yaml')
                        for i, item in enumerate(all_inquiries):
                            if item['id'] == inq['id']:
                                all_inquiries[i]['answered'] = True
                                all_inquiries[i]['answer'] = answer
                                break
                        if save_data('inquiries.yaml', all_inquiries):
                            st.success("답변이 등록되었습니다!")
                            st.rerun()
                    else:
                        st.error("답변 내용을 입력해주세요.")

def show_admin_column_form():
    """관리자 칼럼 작성 폼을 표시합니다."""
    st.header("📝 칼럼 작성")

    with st.form("column_form"):
        title = st.text_input("제목", max_chars=100)
        content = st.text_area("내용", height=400)

        submitted = st.form_submit_button("칼럼 등록", use_container_width=True)

        if submitted:
            if not title or not content:
                st.error("제목과 내용을 모두 입력해주세요.")
            else:
                columns = load_data('columns.yaml')
                new_column = {
                    'id': str(uuid.uuid4()),
                    'author': st.session_state.user_name,
                    'title': title,
                    'content': content,
                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                columns.append(new_column)
                if save_data('columns.yaml', columns):
                    st.success("칼럼이 등록되었습니다!")
                    st.rerun()

    # 기존 칼럼 목록
    st.divider()
    st.subheader("📰 작성된 칼럼 목록")
    columns = load_data('columns.yaml')

    if columns:
        for col in sorted(columns, key=lambda x: x['created_at'], reverse=True):
            with st.expander(f"📝 {col['title']} - {col['created_at'][:10]}"):
                st.markdown(f"**작성자**: {col['author']}")
                st.markdown(f"**작성일**: {col['created_at']}")
                st.divider()
                st.markdown(col['content'])

                if st.button("삭제", key=f"delete_col_{col['id']}"):
                    all_columns = load_data('columns.yaml')
                    all_columns = [c for c in all_columns if c['id'] != col['id']]
                    if save_data('columns.yaml', all_columns):
                        st.success("칼럼이 삭제되었습니다!")
                        st.rerun()
    else:
        st.info("아직 작성된 칼럼이 없습니다.")

# 메인 애플리케이션
def main():
    # 사이드바 - 로그인/로그아웃
    with st.sidebar:
        st.title("🏥 블루힐 한의원")
        st.divider()

        # 로그인/로그아웃 섹션
        st.subheader("🔐 인증")

        if not st.session_state.logged_in:
            with st.expander("로그인", expanded=False):
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

        # 메뉴 섹션
        st.subheader("📋 메뉴")

        # 한의원 메뉴
        with st.expander("🏥 한의원", expanded=True):
            if st.button("👨‍⚕️ 의료진", use_container_width=True, key="menu_staff"):
                st.session_state.selected_menu = '의료진'
                st.session_state.selected_category = '한의원'
                st.rerun()
            if st.button("📍 위치 및 진료시간", use_container_width=True, key="menu_location"):
                st.session_state.selected_menu = '위치및진료시간'
                st.session_state.selected_category = '한의원'
                st.rerun()
            if st.button("📰 칼럼", use_container_width=True, key="menu_column"):
                st.session_state.selected_menu = '칼럼'
                st.session_state.selected_category = '한의원'
                st.rerun()

        # 진료과목 메뉴
        with st.expander("💊 진료과목", expanded=False):
            if st.button("💊 통증치료", use_container_width=True, key="menu_pain"):
                st.session_state.selected_menu = '통증치료'
                st.session_state.selected_category = '진료과목'
                st.rerun()
            if st.button("🤲 추나요법", use_container_width=True, key="menu_chuna"):
                st.session_state.selected_menu = '추나요법'
                st.session_state.selected_category = '진료과목'
                st.rerun()
            if st.button("🦌 녹용한약", use_container_width=True, key="menu_nokyong"):
                st.session_state.selected_menu = '녹용한약'
                st.session_state.selected_category = '진료과목'
                st.rerun()
            if st.button("💎 공진단", use_container_width=True, key="menu_gongjin"):
                st.session_state.selected_menu = '공진단'
                st.session_state.selected_category = '진료과목'
                st.rerun()

        # 진료후기 메뉴
        if st.button("⭐ 진료후기", use_container_width=True, key="menu_review"):
            st.session_state.selected_menu = '진료후기'
            st.session_state.selected_category = '기타'
            st.rerun()

        # 문의 메뉴
        if st.button("💬 문의", use_container_width=True, key="menu_inquiry"):
            st.session_state.selected_menu = '문의'
            st.session_state.selected_category = '기타'
            st.rerun()

        # 관리자 메뉴
        if st.session_state.role == 'admin':
            st.divider()
            st.subheader("🔧 관리자 메뉴")

            if st.button("📋 문의글 관리", use_container_width=True, key="menu_admin_inquiry"):
                st.session_state.selected_menu = '문의글관리'
                st.session_state.selected_category = '관리자'
                st.rerun()

            if st.button("📝 칼럼 작성", use_container_width=True, key="menu_admin_column"):
                st.session_state.selected_menu = '칼럼작성'
                st.session_state.selected_category = '관리자'
                st.rerun()

        # 테스트 계정 안내
        st.divider()
        with st.expander("ℹ️ 테스트 계정"):
            st.markdown("""
            **일반 사용자:**
            - user1 / password1
            - user2 / password2

            **관리자:**
            - admin1 / admin123
            """)

    # 메인 콘텐츠 영역
    # 파일 매핑
    file_mapping = {
        '의료진': '01_의료진.md',
        '위치및진료시간': '02_위치및진료시간.md',
        '칼럼': '03_칼럼.md',
        '통증치료': '04_통증치료.md',
        '추나요법': '05_추나요법.md',
        '녹용한약': '06_녹용한약.md',
        '공진단': '07_공진단.md'
    }

    # 선택된 메뉴에 따라 콘텐츠 표시
    if st.session_state.selected_category == '관리자':
        if st.session_state.selected_menu == '문의글관리':
            show_admin_inquiry_management()
        elif st.session_state.selected_menu == '칼럼작성':
            show_admin_column_form()
    elif st.session_state.selected_category == '기타':
        if st.session_state.selected_menu == '진료후기':
            show_review_page()
        elif st.session_state.selected_menu == '문의':
            show_inquiry_page()
    else:
        # 한의원 또는 진료과목 메뉴
        menu = st.session_state.selected_menu
        filename = file_mapping.get(menu)

        if filename:
            # 제목 표시
            emoji_map = {
                '의료진': '👨‍⚕️',
                '위치및진료시간': '📍',
                '칼럼': '📰',
                '통증치료': '💊',
                '추나요법': '🤲',
                '녹용한약': '🦌',
                '공진단': '💎'
            }
            emoji = emoji_map.get(menu, '📄')
            st.title(f"{emoji} {menu}")
            st.divider()

            display_markdown_content(filename)
        else:
            st.error("선택한 메뉴를 찾을 수 없습니다.")

if __name__ == "__main__":
    main()
