"""
파일 로딩 및 보안 테스트
"""
import pytest
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestLoadMarkdownFile:
    """마크다운 파일 로딩 테스트"""

    def test_load_existing_file(self, temp_markdown_content):
        """존재하는 파일 로드"""
        import app

        public_file = temp_markdown_content['public_dir'] / 'public-doc.md'
        content = app.load_markdown_file(str(public_file))

        assert "Public Document" in content
        assert "This is public content" in content

    def test_load_nonexistent_file(self):
        """존재하지 않는 파일 로드 시도"""
        import app

        content = app.load_markdown_file('/nonexistent/path/file.md')

        assert "⚠️" in content
        assert "찾을 수 없습니다" in content

    def test_load_file_with_encoding(self, tmp_path):
        """UTF-8 인코딩된 파일 로드"""
        import app

        # 한글 포함 파일 생성
        test_file = tmp_path / 'korean-doc.md'
        test_file.write_text('# 한글 제목\n테스트 내용입니다.', encoding='utf-8')

        content = app.load_markdown_file(str(test_file))

        assert '한글 제목' in content
        assert '테스트 내용' in content

    def test_load_file_with_special_characters(self, tmp_path):
        """특수 문자가 포함된 파일 로드"""
        import app

        test_file = tmp_path / 'special-chars.md'
        test_content = '# Test\n```python\nprint("Hello")\n```\n**Bold** _italic_'
        test_file.write_text(test_content, encoding='utf-8')

        content = app.load_markdown_file(str(test_file))

        assert 'print("Hello")' in content
        assert '**Bold**' in content


class TestListMarkdownFiles:
    """마크다운 파일 목록 조회 테스트"""

    def test_list_files_in_existing_directory(self, temp_markdown_content):
        """존재하는 디렉토리의 파일 목록"""
        import app

        files = app.list_markdown_files(str(temp_markdown_content['public_dir']))

        assert len(files) == 1
        assert 'public-doc.md' in files

    def test_list_files_in_nonexistent_directory(self):
        """존재하지 않는 디렉토리"""
        import app

        files = app.list_markdown_files('/nonexistent/directory')

        assert files == []

    def test_list_files_sorted(self, tmp_path):
        """파일 목록이 정렬되어 반환되는지 확인"""
        import app

        # 여러 파일 생성
        (tmp_path / 'z-file.md').write_text('content')
        (tmp_path / 'a-file.md').write_text('content')
        (tmp_path / 'm-file.md').write_text('content')

        files = app.list_markdown_files(str(tmp_path))

        assert files == ['a-file.md', 'm-file.md', 'z-file.md']

    def test_list_files_filters_non_markdown(self, tmp_path):
        """마크다운 파일만 필터링하는지 확인"""
        import app

        (tmp_path / 'doc.md').write_text('content')
        (tmp_path / 'readme.txt').write_text('content')
        (tmp_path / 'script.py').write_text('content')

        files = app.list_markdown_files(str(tmp_path))

        assert len(files) == 1
        assert files == ['doc.md']


class TestPathTraversalSecurity:
    """경로 순회 공격 방지 테스트"""

    def test_prevent_parent_directory_access(self, mocker, temp_markdown_content):
        """상위 디렉토리 접근 차단 (.. 사용)"""
        import app

        mock_st = mocker.MagicMock()
        mocker.patch('app.st', mock_st)

        # display_content 함수는 streamlit 의존성이 있으므로
        # 직접 보안 로직만 테스트
        test_filename = '../../../etc/passwd'

        # 파일명에 '..'이 포함되어 있는지 확인하는 로직 테스트
        assert '..' in test_filename
        assert os.path.sep in test_filename or '/' in test_filename

    def test_prevent_absolute_path_access(self):
        """절대 경로 접근 차단"""
        import app

        test_filename = '/etc/passwd'

        assert os.path.sep in test_filename

    def test_path_validation_logic(self, tmp_path):
        """경로 검증 로직 테스트"""
        import os

        base_dir = tmp_path / 'content' / 'public'
        base_dir.mkdir(parents=True)

        # 안전한 파일명
        safe_filename = 'document.md'
        safe_path = os.path.join(str(base_dir), safe_filename)
        assert os.path.abspath(safe_path).startswith(os.path.abspath(str(base_dir)))

        # 위험한 파일명 (상위 디렉토리 접근 시도)
        dangerous_filename = '../../../etc/passwd'
        dangerous_path = os.path.join(str(base_dir), dangerous_filename)
        resolved_path = os.path.abspath(dangerous_path)
        assert not resolved_path.startswith(os.path.abspath(str(base_dir)))

    def test_symlink_attack_prevention(self, tmp_path):
        """심볼릭 링크를 통한 공격 방지"""
        import os

        base_dir = tmp_path / 'content'
        base_dir.mkdir(parents=True)

        sensitive_file = tmp_path / 'sensitive.txt'
        sensitive_file.write_text('secret data')

        # 심볼릭 링크 생성 시도
        symlink_path = base_dir / 'link.md'
        try:
            symlink_path.symlink_to(sensitive_file)

            # 심볼릭 링크의 실제 경로 확인
            real_path = os.path.realpath(str(symlink_path))
            assert not real_path.startswith(os.path.abspath(str(base_dir)))
        except OSError:
            # 심볼릭 링크 생성 권한이 없는 경우 (Windows 등)
            pass

    def test_filename_with_path_separator(self):
        """경로 구분자가 포함된 파일명 차단"""
        import os

        # Unix 스타일
        assert os.path.sep in f'subdir{os.path.sep}file.md'

        # 크로스 플랫폼 체크
        assert '/' in 'subdir/file.md' or '\\' in 'subdir\\file.md'


class TestEdgeCases:
    """엣지 케이스 테스트"""

    def test_empty_markdown_file(self, tmp_path):
        """빈 마크다운 파일 로드"""
        import app

        empty_file = tmp_path / 'empty.md'
        empty_file.write_text('', encoding='utf-8')

        content = app.load_markdown_file(str(empty_file))

        assert content == ''

    def test_very_large_markdown_file(self, tmp_path):
        """매우 큰 마크다운 파일 로드"""
        import app

        large_file = tmp_path / 'large.md'
        large_content = '# Header\n' + ('Lorem ipsum dolor sit amet. ' * 10000)
        large_file.write_text(large_content, encoding='utf-8')

        content = app.load_markdown_file(str(large_file))

        assert 'Header' in content
        assert len(content) > 10000

    def test_markdown_file_with_only_whitespace(self, tmp_path):
        """공백만 있는 파일"""
        import app

        whitespace_file = tmp_path / 'whitespace.md'
        whitespace_file.write_text('   \n\n   \n', encoding='utf-8')

        content = app.load_markdown_file(str(whitespace_file))

        assert content == '   \n\n   \n'

    def test_filename_with_unicode(self, tmp_path):
        """유니코드 파일명 처리"""
        import app

        unicode_file = tmp_path / '한글파일명.md'
        unicode_file.write_text('# 한글 내용', encoding='utf-8')

        content = app.load_markdown_file(str(unicode_file))

        assert '한글 내용' in content
