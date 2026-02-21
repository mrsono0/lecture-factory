#!/bin/bash
# Sequential NotebookLM queries for AI-native_데이터분석
cd "$(dirname "$0")"
OUTDIR="../../../notebooklm_facts_output"
mkdir -p "$OUTDIR"
NB_ID="ai-native-데이터분석"

echo "=== Query 1/6: 환경 구축 ==="
rm -f data/browser_state/browser_profile/SingletonLock
python scripts/run.py ask_question.py --show-browser --notebook-id "$NB_ID" \
  --question "파트1 통합 AI 분석 환경 구축에 대해 상세히 알려줘. Antigravity 설치 과정, uv 설치와 가상환경 구성 방법, Gemini CLI 설치, GEMINI.md 작성 방법을 포함해서 구체적으로 설명해줘." \
  > "$OUTDIR/01_환경구축.txt" 2>&1
echo "Query 1 done: $?"

echo "=== Query 2/6: CRISP-DM & 프롬프트 ==="
rm -f data/browser_state/browser_profile/SingletonLock
python scripts/run.py ask_question.py --show-browser --notebook-id "$NB_ID" \
  --question "CRISP-DM 프레임워크와 AI 분석의 관계, 비즈니스 이해와 가설 설정, 프롬프트 기본 이해, 좋은 프롬프트와 나쁜 프롬프트 비교 예시, 기술 통계 개념(평균, 분산, 편차, IQR)을 상세히 설명해줘." \
  > "$OUTDIR/02_CRISP-DM_프롬프트.txt" 2>&1
echo "Query 2 done: $?"

echo "=== Query 3/6: 데이터 수집 & EDA ==="
rm -f data/browser_state/browser_profile/SingletonLock
python scripts/run.py ask_question.py --show-browser --notebook-id "$NB_ID" \
  --question "파트2 데이터 수집에 대해 알려줘. 데이터 수집 윤리, 웹크롤링과 웹스크래핑 차이, HTTP 통신 원리, HTML과 JSON 구조 차이, 서점 데이터 수집을 위한 프롬프트 작성법, Gemini CLI로 스크래핑 코드 생성, Pandas EDA 코드 생성 방법, 분석 보고서 PPTX 변환을 구체적으로 설명해줘." \
  > "$OUTDIR/03_데이터수집_EDA.txt" 2>&1
echo "Query 3 done: $?"

echo "=== Query 4/6: JSON 수집 & 전처리 ==="
rm -f data/browser_state/browser_profile/SingletonLock
python scripts/run.py ask_question.py --show-browser --notebook-id "$NB_ID" \
  --question "JSON 응답 데이터 수집 방법, Git 버전관리, 결측치와 이상치 정제 방법, 파생 변수 생성(Feature Engineering), 범용 전처리 프롬프트 템플릿 작성법을 상세히 설명해줘." \
  > "$OUTDIR/04_JSON수집_전처리.txt" 2>&1
echo "Query 4 done: $?"

echo "=== Query 5/6: 실전 프로젝트 & 리포팅 ==="
rm -f data/browser_state/browser_profile/SingletonLock
python scripts/run.py ask_question.py --show-browser --notebook-id "$NB_ID" \
  --question "파트4 실전 프로젝트에 대해 알려줘. 스타벅스 전국 매장 정보 수집(POST 전송, 폼데이터), 상업용 부동산 매물 JSON 수집, NotebookLM에 CSV 업로드, 분석 결과 종합과 가설 검증, AI 기반 마크다운 보고서 작성, python-pptx로 PPTX 자동 변환을 구체적으로 설명해줘." \
  > "$OUTDIR/05_실전프로젝트_리포팅.txt" 2>&1
echo "Query 5 done: $?"

echo "=== Query 6/6: 시각화 & Streamlit ==="
rm -f data/browser_state/browser_profile/SingletonLock
python scripts/run.py ask_question.py --show-browser --notebook-id "$NB_ID" \
  --question "파트6 데이터 시각화와 Streamlit에 대해 알려줘. Matplotlib/Seaborn 차트 생성 프롬프트 예시, 한글 폰트 깨짐 해결, Streamlit 대시보드 기획과 코드 생성, 로컬 CSV 연동 대시보드 배포 방법을 구체적으로 설명해줘." \
  > "$OUTDIR/06_시각화_Streamlit.txt" 2>&1
echo "Query 6 done: $?"

echo "=== ALL QUERIES COMPLETE ==="
