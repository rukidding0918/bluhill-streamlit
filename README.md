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