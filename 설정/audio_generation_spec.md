# 오디오 생성 기술 명세서
> The Second Self 영어 학습 프로젝트 오디오 생성 가이드

## 📋 개요

이 문서는 학습 콘텐츠용 TTS 오디오 생성 시 참고해야 할 기술 명세입니다.

---

## 🔧 기술 스택

| 항목 | 값 |
|------|-----|
| API | Gemini Live API (`google-genai`) |
| 모델 | `models/gemini-2.5-flash-native-audio-preview-12-2025` |
| 샘플링 레이트 | 24000 Hz |
| 채널 | Mono (1) |
| 비트 | 16-bit (2 bytes) |
| 출력 형식 | MP3 (ffmpeg 변환) |

---

## 🎤 음성 설정

### 기본 음성 (스토리/쉐도잉)
- **음성명:** `Zephyr`
- **특성:** 남성, 따뜻하고 자연스러운 톤

### 역할극 음성
| 역할 | 음성명 | 특성 |
|------|--------|------|
| A (남성) | `Puck` | 남성 음성 |
| B (여성) | `Kore` | 여성 음성 |

---

## 📁 오디오 유형별 명세

### 1. 스토리 오디오 (Story)
| 항목 | 값 |
|------|-----|
| 용도 | Day 1, Day 5 Reading 페이지 |
| 파일명 패턴 | `week{N}_day{D}_story.mp3` |
| 음성 | Zephyr |
| 프롬프트 | `Read this text naturally in a warm, conversational tone. Speak as if you're a friendly American man casually introducing himself to a new friend. Use natural rhythm, linking between words, and authentic emotion: {text}` |
| 공백 삽입 | 없음 (연속 재생) |

### 2. 쉐도잉 오디오 (Shadowing)
| 항목 | 값 |
|------|-----|
| 용도 | Day 4 Speaking 페이지 |
| 파일명 패턴 | `week{N}_day4_shadowing.mp3` |
| 음성 | Zephyr |
| 프롬프트 | `Read this sentence naturally in a warm, conversational tone: {sentence}` |
| 문장간 공백 | **4초** |
| 생성 방식 | 각 문장을 개별 생성 후 공백과 함께 합치기 |

### 3. 역할극 오디오 (Role Play)
| 항목 | 값 |
|------|-----|
| 용도 | Day 4 Speaking 페이지 |
| 파일명 패턴 | `week{N}_day4_roleplay.mp3` |
| 음성 | A: Puck, B: Kore |
| 프롬프트 | `Read this line naturally in a friendly conversational tone: {line}` |
| 대사간 공백 | **3초** |
| 생성 방식 | 각 대사를 화자별 음성으로 개별 생성 후 공백과 함께 합치기 |

---

## 📂 파일 저장 위치

```
docs/assets/audio/
├── week1_day2_story.mp3
├── week1_day4_shadowing.mp3
├── week1_day4_roleplay.mp3
├── week2_day2_story.mp3
└── ...
```

---

## 🛠️ 생성 스크립트

### 스토리/리스닝 오디오
```bash
# 스크립트: generate_tts_audio.py
export GEMINI_API_KEY="API_KEY"
python3 generate_tts_audio.py
```

### 쉐도잉 오디오 (공백 포함)
```bash
# 스크립트: generate_shadowing_audio.py
export GEMINI_API_KEY="API_KEY"
python3 generate_shadowing_audio.py
```

### 역할극 오디오 (다중 화자)
```bash
# 스크립트: generate_roleplay_audio.py
export GEMINI_API_KEY="API_KEY"
python3 generate_roleplay_audio.py
```

---

## ⚠️ 주의사항

1. **프롬프트 최적화**
   - ❌ "slowly and clearly", "as if teaching English" → 부자연스러운 발음 유발
   - ✅ "naturally", "warm, conversational tone" → 자연스러운 발화

2. **공백 생성**
   - 쉐도잉: 따라 말할 시간 확보 (4초)
   - 역할극: 대화 흐름 유지하면서 구분 (3초)

3. **오디오 플레이어 UI**
   - 컨트롤: 재생, 일시정지, 처음부터
   - 속도 조절: 0.75x, 1.0x, 1.25x
   - 오디오 플레이어는 콘텐츠(문장, 대본) **전**에 배치

---

## 📝 체크리스트

새 오디오 생성 시:
- [ ] 올바른 음성 선택 (Zephyr / Puck / Kore)
- [ ] 프롬프트 최적화 확인
- [ ] 공백 시간 확인 (쉐도잉: 4초, 역할극: 3초)
- [ ] 파일명 규칙 준수
- [ ] HTML 페이지에 오디오 플레이어 추가
- [ ] 플레이어 위치 확인 (콘텐츠 전)
