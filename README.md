# Rick Steves Audio Guide Analysis Dashboard

Rick Steves 포럼의 오디오 가이드 분석을 위한 대시보드입니다.

## 🚀 Streamlit Cloud 배포

### 배포 방법

1. **GitHub에 코드 푸시**

    ```bash
    git add .
    git commit -m "Add Streamlit deployment files"
    git push origin main
    ```

2. **Streamlit Cloud에서 배포**
    - [Streamlit Cloud](https://share.streamlit.io/)에 접속
    - GitHub 계정으로 로그인
    - "New app" 클릭
    - Repository: `your-username/ricksteves`
    - Main file path: `streamlit_app.py`
    - Deploy 클릭

### 배포 후 문제 해결

#### 흰 화면만 보이는 경우

1. **데이터 파일 경로 확인**

    - 모든 JSON 파일이 `src/transform/` 폴더에 있는지 확인
    - 파일 크기가 너무 크면 Git LFS 사용 고려

2. **로그 확인**

    - Streamlit Cloud 대시보드에서 "Manage app" → "Logs" 확인
    - 에러 메시지 확인

3. **메모리 문제**
    - `enhanced_posts.json` 파일이 45MB로 큼
    - 필요시 데이터를 분할하거나 압축 고려

### 로컬 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 대시보드 실행
cd src/load
streamlit run dashboard.py
```

### 프로젝트 구조

```
ricksteves/
├── src/
│   ├── load/
│   │   ├── dashboard.py          # 메인 대시보드
│   │   └── run_dashboard.py     # 로컬 실행 스크립트
│   └── transform/
│       ├── audio_guide_metrics.json
│       ├── museum_comparison.json
│       └── enhanced_posts.json
├── streamlit_app.py              # 배포용 메인 파일
├── requirements.txt              # 의존성
└── .streamlit/config.toml       # Streamlit 설정
```

### 주요 기능

-   🏛️ 박물관별 오디오 가이드 분석
-   📊 감정 분석 및 참여도 지표
-   🎯 테마 분석 및 키워드 추출
-   📋 포스트 필터링 및 검색
-   🌍 전역 통계 및 비교 분석
