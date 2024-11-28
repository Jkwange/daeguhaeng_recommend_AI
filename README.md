# **대구행 추천 AI (DaeguHaeng Recommend AI)**  
관광지 추천 AI 플랫폼

> **주의**: 이 프로젝트는 **프론트엔드**, **백엔드**, **AI**가 각각 분리된 구조로 개발되었습니다.  
> 데이터셋은 직접 크롤링하여 전처리 및 데이터 분석 과정을 거쳐 사용되었습니다.

> 프론트엔드 : https://github.com/jaaesung/DaeguHang/tree/yoonagi1210
> 백엔드 : https://github.com/brothergiven/daeguhaeng_backend/tree/master
---

## **프로젝트 개요**  
**대구행 추천 AI**는 사용자의 취향과 데이터를 기반으로 개인화된 관광 추천을 제공하는 시스템입니다.  
여행 경험을 향상시키기 위해 머신러닝 모델을 활용하여 대구의 관광지별 맛집, 카페, 호텔, 모텔을 추천합니다.

---

## **시작하기 (Getting Started)**  

### **필수 사항 (Prerequisites)**  
프로그램 실행 전에 아래 사항을 확인하세요:
- Python (버전 3.8 이상)
- `pip` (Python 패키지 관리자)

### **필수 라이브러리 설치**  
터미널을 열고 다음 명령어를 실행하여 필요한 라이브러리를 설치해야 합니다
```bash
pip install flask numpy flask_cors pandas scikit-learn openpyxl
```
---

## **앱 실행 방법**  
1. 사용하려는 포트 번호가 `5000`인지 확인합니다.  
   - 만약 `5000`번 포트를 사용할 수 없다면, `app.py` 파일에서 포트 번호를 변경해야 합니다.
2. 터미널에서 다음 명령어를 실행하여 프로그램을 시작합니다
   ```bash
   python app.py
   ```

---

## **프로젝트 구조**
```plaintext
daeguhaeng_AI/
├── .vscode/             # VSCode 설정 파일 디렉토리
│   └── settings.json    # 프로젝트 관련 설정 파일
├── mnt/                 # 데이터 디렉토리
│   └── data/            # 데이터 파일 저장소
├── app.py               # Flask 기반의 백엔드 애플리케이션
└── README.md            # 프로젝트 설명서
