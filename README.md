# Mom Voice ChatBot

엄마 목소리를 분리, 학습하여 페르소나 챗봇을 만드는 프로젝트입니다.

## 핵심 기능
- 오디오 파일 내 엄마 화자 분리 및 복원 (Diarization & Source Separation)
- Faster-Whisper 기반 STT
- LLM 기반 페르소나 및 대화 메모리 (RAG)
- 엄마 목소리 TTS 재합성

## 실행 방법 (Mac 기준)
1. 의존성 시스템 패키지 설치
   ```bash
   brew install ffmpeg redis
   ```
2. 파이썬 환경 세팅
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. 환경변수 설정
   ```bash
   cp .env.example .env
   # .env 파일에 필요한 토큰(HF_TOKEN) 등을 입력하세요.
   ```
4. Redis 및 FastAPI, Worker 실행
   ```bash
   redis-server &
   uvicorn backend.main:app --reload &
   rq worker &
   ```

## 10단계: 남은 한계와 개선 우선순위

1. **처리 속도 최적화 (Priority: High)**
   - 초기 버전에 포함된 Pyannote와 Faster-Whisper, SpeechBrain은 VRAM을 많이 소모하며 CPU 추론 시 상당한 시간이 걸립니다.
   - **개선안**: TensorRT 적용 또는 외부 API(OpenAI 기반) 어댑터를 활성화하는 모드로 전환하여 하이브리드 구성을 구체화합니다.

2. **겹침(Overlap) 음성 완벽한 복원 (Priority: Medium)**
   - 현재 파이프라인은 Diarization을 통해 겹침을 인지하고 Cosine Similarity로 가장 가까운 채널을 추출하지만, 완벽한 백그라운드 노이즈 분리는 한계가 있습니다.
   - **개선안**: HTDemucs 등 최신 Source Separation 모델을 분할 파이프라인 앞에 배치하여 음원을 1차 정제합니다.

3. **페르소나 연속성 (Priority: Medium)**
   - 현재 Chatbot은 추출된 규칙을 Context로 주입하는 방식의 완전한 의존성을 갖습니다. 사용 기간이 길어질수록 컨텍스트 제한에 걸릴 수 있습니다.
   - **개선안**: ChromaDB를 연동하여 Vector 검색을 통해 과거 대화를 실시간 RAG로 불러오도록 확장합니다. (모델 템플릿에는 ChromaDB 의존성이 명시됨)

4. **모바일 권한 및 오디오 스트리밍 (Priority: Low)**
   - 현재 Flutter 녹음 기능은 단일 파일 업로드 기준입니다. 
   - **개선안**: WebSocket 연동을 통해 실시간 STT 및 TTS 스트리밍 재생을 지원하여 더 자연스러운 대화를 구현합니다.
