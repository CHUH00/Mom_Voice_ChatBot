# Mom Voice ChatBot 시연 시나리오

## 1. 사전 준비 (백엔드 기동)
1. `/Users/woojin/Desktop/CHUH00_Git/Mom_Voice_ChatBot` 디렉토리에서 터미널을 열고 `./start.sh`를 실행합니다.
2. 이 스크립트는 내부적으로 Redis, RQ 워커(비동기 AI 처리용), FastAPI 서버, 그리고 자동 Git Push 데몬을 한꺼번에 실행합니다.

## 2. 모바일 앱 실행 및 온보딩
1. 앱 폴더(`app_mobile/`)로 이동하여 시스템에 설치된 Flutter를 통해 앱을 실행합니다. (`flutter run -d macOS` 권장)
2. 첫 화면(OnboardingScreen)에서 **"본 앱은 실제 인물이 아님을 인지하며 명시적 제공에 동의합니다"** 체크박스를 누르고 안전 통과합니다.

## 3. 엄마 목소리 등록 및 분리 파이프라인 시연
1. '음성 등록' 화면에서 `파일 선택` 버튼을 누릅니다.
2. 준비된 `dataset/` 폴더 안의 혼합 대화 녹음 파일(예: 사용자와 엄마가 같이 말하는 녹음본)을 업로드합니다.
3. **[AI 파이프라인 처리 상세]**
   - **Audio Processor**: ffmpeg을 이용해 16kHz 모노 파일로 전처리합니다.
   - **Diarization**: Pyannote 3.1 모델이 동작하여 음원을 세그먼트 단위로 쪼갭니다.
   - **Speaker Verification**: SpeechBrain(ECAPA-TDNN) 모듈이 기존에 제공된 엄마 레퍼런스(`mom_1.wav` 등)와 유사도를 측정하여 엄마 화자 구간만 True로 마킹합니다.
   - **Reconstruction**: 엄마 구간만 붙여 새로운 `mom_only.wav`를 만들고, Faster-Whisper가 이를 텍스트(STT)로 변환해 DB에 저장합니다.

## 4. 페르소나 추출 및 대화 시연
1. 분리가 완료되면 자동으로 채팅 화면(ChatScreen)으로 진입합니다.
2. 채팅창에 "엄마, 오늘 나 면접 보고 왔어" 라고 입력합니다.
3. 백엔드의 Ollama (Llama-3) 모듈이, AI 파이프라인이 분석해둔 '엄마의 말투(톤, 잦은 감탄사, 어미)'를 Prompt Context로 불러옵니다.
4. **챗봇 답변**: 환각을 방지하는 모드가 발동하여, 사실을 꾸며내는 대신 "어머 고생했네, 밥은 먹었어?" 식으로 지정된 페르소나 스타일로 응답합니다.
5. **음성 합성**: 생성된 텍스트 응답은 즉시 XTTS-v2 모델로 넘어가 제공했던 엄마 음성(`dataset/mom_*.wav`)을 기반으로 Voice Cloning되어 출력/재생됩니다.
