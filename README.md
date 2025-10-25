# Bluhill Streamlit Documentation Portal 📚

Streamlit 기반의 마크다운 문서 배포 시스템으로, 사용자 인증 및 역할 기반 접근 제어 기능을 제공합니다.

## 주요 기능

- 🔐 **사용자 인증**: 로그인/로그아웃 시스템
- 👥 **역할 기반 접근 제어**: 공개, 사용자, 특별 사용자 권한 구분
- 📄 **마크다운 지원**: 풍부한 마크다운 문서 표시
- 🎨 **직관적인 UI**: Streamlit의 깔끔한 인터페이스

## 설치 및 실행

### 필수 요구사항

- Python 3.8 이상
- pip 패키지 관리자

### 설치 단계

1. **저장소 클론**
   ```bash
   git clone https://github.com/rukidding0918/bluhill-streamlit.git
   cd bluhill-streamlit
   ```

2. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

3. **애플리케이션 실행**
   ```bash
   streamlit run app.py
   ```

4. **브라우저 접속**
   
   자동으로 브라우저가 열리며 `http://localhost:8501`로 접속됩니다.

## 사용자 계정

테스트를 위한 기본 계정이 제공됩니다:

### 일반 사용자
- 사용자명: `user1` / 비밀번호: `password1`
- 사용자명: `user2` / 비밀번호: `password2`

### 특별 사용자 (관리자 승인)
- 사용자명: `special1` / 비밀번호: `special123`
- 사용자명: `special2` / 비밀번호: `special456`

### 관리자
- 사용자명: `admin1` / 비밀번호: `admin123`

## 콘텐츠 구조

```
content/
├── public/      # 🌐 공개 콘텐츠 (모든 사용자)
├── user/        # 👤 사용자 콘텐츠 (로그인 필요)
└── special/     # ⭐ 특별 콘텐츠 (특별 권한 필요)
```

### 콘텐츠 추가 방법

1. 적절한 디렉토리에 `.md` 파일 생성
2. 마크다운 형식으로 콘텐츠 작성
3. UTF-8 인코딩으로 저장
4. 애플리케이션 새로고침

## 사용자 관리

`users.yaml` 파일을 편집하여 사용자를 추가/수정할 수 있습니다:

```yaml
users:
  username:
    password: "password"
    role: "user"  # user, special, admin
    name: "Display Name"
```

## 역할 및 권한

| 역할 | 공개 콘텐츠 | 사용자 콘텐츠 | 특별 콘텐츠 |
|------|------------|--------------|------------|
| 비로그인 | ✅ | ❌ | ❌ |
| User | ✅ | ✅ | ❌ |
| Special | ✅ | ✅ | ✅ |
| Admin | ✅ | ✅ | ✅ |

## 테스트

이 프로젝트는 pytest를 사용한 포괄적인 테스트 스위트를 포함하고 있습니다.

### 테스트 실행

```bash
# 모든 테스트 실행
pytest

# 상세 출력과 함께 실행
pytest -v

# 코드 커버리지 포함
pytest --cov=app --cov-report=html

# 특정 테스트 파일만 실행
pytest tests/test_auth.py
```

### 테스트 구조

```
tests/
├── conftest.py              # 공통 fixture 및 설정
├── test_auth.py             # 인증 기능 테스트 (10 tests)
├── test_file_operations.py  # 파일 로딩 및 보안 테스트 (17 tests)
└── test_access_control.py   # 역할 기반 접근 제어 테스트 (16 tests)
```

### 테스트 커버리지

- **43개 테스트** 모두 통과
- **코드 커버리지**: 39% (핵심 비즈니스 로직)
- UI 컴포넌트는 수동 테스트 권장

### 테스트 카테고리

#### 🔐 인증 테스트
- 정상 로그인/로그아웃
- 잘못된 자격증명 처리
- 역할별 로그인 검증
- 사용자 데이터 로딩

#### 📁 파일 작업 테스트
- 마크다운 파일 로딩
- UTF-8 인코딩 처리
- 파일 목록 조회 및 필터링
- 엣지 케이스 (빈 파일, 대용량 파일 등)

#### 🛡️ 보안 테스트
- 경로 순회 공격 방지 (`../../../etc/passwd`)
- 절대 경로 접근 차단
- 심볼릭 링크 공격 방지
- 파일명 검증

#### 👥 접근 제어 테스트
- 역할별 권한 검증
- 권한 상승 공격 방지
- 세션 상태 관리
- 엣지 케이스 처리

### CI/CD 통합

GitHub Actions나 다른 CI 도구에서 테스트를 실행하려면:

```bash
pip install -r requirements.txt
pytest -v --cov=app --cov-report=xml
```

## 보안 고려사항

⚠️ **중요**: 현재 구현은 개발/데모 목적입니다. 프로덕션 환경에서는 다음을 고려하세요:

- 비밀번호 해싱 (bcrypt, argon2 등)
- HTTPS 사용
- 환경 변수를 통한 민감 정보 관리
- 세션 보안 강화
- 더 강력한 인증 메커니즘 (OAuth, JWT 등)

## 라이선스

MIT License

## 기여

이슈 및 풀 리퀘스트를 환영합니다!