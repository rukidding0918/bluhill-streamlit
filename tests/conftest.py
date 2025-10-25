"""
pytest 설정 및 공통 fixture 정의
"""
import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture
def sample_users():
    """테스트용 사용자 데이터"""
    return {
        'testuser': {
            'password': 'testpass123',
            'role': 'user',
            'name': 'Test User'
        },
        'specialuser': {
            'password': 'specialpass456',
            'role': 'special',
            'name': 'Special Test User'
        },
        'adminuser': {
            'password': 'adminpass789',
            'role': 'admin',
            'name': 'Admin Test User'
        }
    }


@pytest.fixture
def temp_users_yaml(tmp_path, sample_users):
    """임시 users.yaml 파일 생성"""
    import yaml

    users_file = tmp_path / "users.yaml"
    with open(users_file, 'w', encoding='utf-8') as f:
        yaml.dump({'users': sample_users}, f)

    return users_file


@pytest.fixture
def temp_markdown_content(tmp_path):
    """임시 마크다운 콘텐츠 디렉토리 구조 생성"""
    content_dir = tmp_path / "content"

    # 디렉토리 생성
    public_dir = content_dir / "public"
    user_dir = content_dir / "user"
    special_dir = content_dir / "special"

    public_dir.mkdir(parents=True)
    user_dir.mkdir(parents=True)
    special_dir.mkdir(parents=True)

    # 테스트 마크다운 파일 생성
    (public_dir / "public-doc.md").write_text(
        "# Public Document\nThis is public content.",
        encoding='utf-8'
    )
    (user_dir / "user-doc.md").write_text(
        "# User Document\nThis is user content.",
        encoding='utf-8'
    )
    (special_dir / "special-doc.md").write_text(
        "# Special Document\nThis is special content.",
        encoding='utf-8'
    )

    return {
        'content_dir': content_dir,
        'public_dir': public_dir,
        'user_dir': user_dir,
        'special_dir': special_dir
    }


@pytest.fixture
def mock_session_state():
    """Streamlit 세션 상태 모킹"""
    class SessionState:
        def __init__(self):
            self.logged_in = False
            self.username = None
            self.role = None
            self.user_name = None

    return SessionState()
