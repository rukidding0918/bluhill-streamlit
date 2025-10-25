"""
인증 기능 테스트
"""
import pytest
import sys
import os

# app.py를 import하기 위한 경로 설정
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestLogin:
    """로그인 기능 테스트"""

    def test_successful_login(self, mocker, sample_users, mock_session_state):
        """정상적인 로그인 테스트"""
        # app 모듈 import
        import app

        # load_users 함수를 모킹하여 테스트 사용자 데이터 반환
        mocker.patch('app.load_users', return_value=sample_users)
        mocker.patch('app.st.session_state', mock_session_state)

        # 로그인 시도
        result = app.login('testuser', 'testpass123')

        assert result is True
        assert mock_session_state.logged_in is True
        assert mock_session_state.username == 'testuser'
        assert mock_session_state.role == 'user'
        assert mock_session_state.user_name == 'Test User'

    def test_login_wrong_password(self, mocker, sample_users, mock_session_state):
        """잘못된 비밀번호로 로그인 시도"""
        import app

        mocker.patch('app.load_users', return_value=sample_users)
        mocker.patch('app.st.session_state', mock_session_state)

        result = app.login('testuser', 'wrongpassword')

        assert result is False
        assert mock_session_state.logged_in is False
        assert mock_session_state.username is None

    def test_login_nonexistent_user(self, mocker, sample_users, mock_session_state):
        """존재하지 않는 사용자로 로그인 시도"""
        import app

        mocker.patch('app.load_users', return_value=sample_users)
        mocker.patch('app.st.session_state', mock_session_state)

        result = app.login('nonexistent', 'password')

        assert result is False
        assert mock_session_state.logged_in is False

    def test_login_special_user(self, mocker, sample_users, mock_session_state):
        """특별 사용자 로그인"""
        import app

        mocker.patch('app.load_users', return_value=sample_users)
        mocker.patch('app.st.session_state', mock_session_state)

        result = app.login('specialuser', 'specialpass456')

        assert result is True
        assert mock_session_state.role == 'special'

    def test_login_admin_user(self, mocker, sample_users, mock_session_state):
        """관리자 사용자 로그인"""
        import app

        mocker.patch('app.load_users', return_value=sample_users)
        mocker.patch('app.st.session_state', mock_session_state)

        result = app.login('adminuser', 'adminpass789')

        assert result is True
        assert mock_session_state.role == 'admin'

    def test_login_empty_credentials(self, mocker, sample_users, mock_session_state):
        """빈 자격증명으로 로그인 시도"""
        import app

        mocker.patch('app.load_users', return_value=sample_users)
        mocker.patch('app.st.session_state', mock_session_state)

        result = app.login('', '')

        assert result is False
        assert mock_session_state.logged_in is False


class TestLogout:
    """로그아웃 기능 테스트"""

    def test_logout(self, mocker, mock_session_state):
        """로그아웃 테스트"""
        import app

        # 로그인 상태로 설정
        mock_session_state.logged_in = True
        mock_session_state.username = 'testuser'
        mock_session_state.role = 'user'
        mock_session_state.user_name = 'Test User'

        mocker.patch('app.st.session_state', mock_session_state)

        # 로그아웃 실행
        app.logout()

        # 세션 상태가 초기화되었는지 확인
        assert mock_session_state.logged_in is False
        assert mock_session_state.username is None
        assert mock_session_state.role is None
        assert mock_session_state.user_name is None

    def test_logout_when_not_logged_in(self, mocker, mock_session_state):
        """로그인하지 않은 상태에서 로그아웃"""
        import app

        mocker.patch('app.st.session_state', mock_session_state)

        # 로그아웃 실행 (에러가 발생하지 않아야 함)
        app.logout()

        assert mock_session_state.logged_in is False
        assert mock_session_state.username is None


class TestLoadUsers:
    """사용자 데이터 로딩 테스트"""

    def test_load_users_success(self, mocker, temp_users_yaml, sample_users):
        """users.yaml 파일 정상 로드"""
        import app

        # open 함수를 모킹하여 임시 파일 사용
        original_open = open

        def mock_open(file, *args, **kwargs):
            if 'users.yaml' in str(file):
                return original_open(temp_users_yaml, *args, **kwargs)
            return original_open(file, *args, **kwargs)

        mocker.patch('builtins.open', side_effect=mock_open)

        # st.cache_resource 데코레이터를 우회하기 위해 함수 직접 호출
        users = app.load_users.__wrapped__()

        assert users == sample_users
        assert 'testuser' in users
        assert users['testuser']['role'] == 'user'

    def test_load_users_file_not_found(self, mocker):
        """users.yaml 파일이 없을 때"""
        import app

        # 파일이 없는 경우를 시뮬레이션
        mocker.patch('builtins.open', side_effect=FileNotFoundError)
        mock_error = mocker.patch('app.st.error')

        users = app.load_users.__wrapped__()

        assert users == {}
        mock_error.assert_called_once()
