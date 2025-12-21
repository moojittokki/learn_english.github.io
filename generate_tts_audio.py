"""
Gemini Live API를 사용한 TTS 오디오 생성 스크립트

Day 2 Listening 페이지용 스토리 오디오를 생성합니다.

## 사용법
python generate_tts_audio.py

## 필요 패키지
pip install google-genai pyaudio

## 환경 변수
export GEMINI_API_KEY="your_api_key"
"""

import os
import asyncio
import wave
import subprocess
from pathlib import Path

from google import genai
from google.genai import types

# 오디오 설정
RECEIVE_SAMPLE_RATE = 24000
CHANNELS = 1
SAMPLE_WIDTH = 2  # 16-bit audio = 2 bytes

# 모델 설정
MODEL = "models/gemini-2.5-flash-native-audio-preview-12-2025"

# API 클라이언트
client = genai.Client(
    http_options={"api_version": "v1beta"},
    api_key=os.environ.get("GEMINI_API_KEY"),
)

# Live API 설정
CONFIG = types.LiveConnectConfig(
    response_modalities=["AUDIO"],
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Zephyr")
        )
    ),
)

# Day 1/Day 2 스토리 텍스트
STORY_TEXT = """
Hello! My name is James. I am 32 years old. I am a software engineer. I work at a tech company in Seoul.

I am from the United States, but I live in Korea now. I am married. My wife's name is Yuna. She is Korean. She is a teacher at an elementary school.

We have one daughter. Her name is Sophie. She is 5 years old. She is very cute and energetic.

My family is small but happy. I love my life in Seoul!
"""

# Day 4 Shadowing 문장들 (개별 문장, 약간의 간격을 두고 천천히)
SHADOWING_SENTENCES = [
    "Hello! My name is James.",
    "I am 32 years old.",
    "I am a software engineer.",
    "I work at a tech company in Seoul.",
    "I am married.",
    "My wife's name is Yuna.",
    "She is a teacher.",
    "We have one daughter.",
    "My family is small but happy.",
    "I love my life in Seoul!"
]


async def generate_audio(text: str, output_path: str):
    """텍스트를 오디오로 변환하여 저장"""
    print(f"🎤 오디오 생성 중: {output_path}")
    
    audio_chunks = []
    
    async with client.aio.live.connect(model=MODEL, config=CONFIG) as session:
        # 텍스트 전송 - 자연스러운 대화 톤으로
        await session.send(
            input=f"Read this text naturally in a warm, conversational tone. Speak as if you're a friendly American man casually introducing himself to a new friend. Use natural rhythm, linking between words, and authentic emotion: {text}",
            end_of_turn=True
        )
        
        # 오디오 응답 수신
        turn = session.receive()
        async for response in turn:
            if data := response.data:
                audio_chunks.append(data)
            if text := response.text:
                print(f"  (텍스트 응답: {text[:50]}...)" if len(text) > 50 else f"  (텍스트 응답: {text})")
    
    if not audio_chunks:
        print("❌ 오디오 데이터를 받지 못했습니다.")
        return False
    
    # PCM 데이터 결합
    pcm_data = b"".join(audio_chunks)
    
    # WAV 파일로 저장
    wav_path = output_path.replace(".mp3", ".wav")
    with wave.open(wav_path, "wb") as wav_file:
        wav_file.setnchannels(CHANNELS)
        wav_file.setsampwidth(SAMPLE_WIDTH)
        wav_file.setframerate(RECEIVE_SAMPLE_RATE)
        wav_file.writeframes(pcm_data)
    
    print(f"  ✅ WAV 저장 완료: {wav_path}")
    
    # MP3로 변환 (ffmpeg 사용)
    try:
        subprocess.run([
            "ffmpeg", "-y", "-i", wav_path,
            "-codec:a", "libmp3lame", "-qscale:a", "2",
            output_path
        ], check=True, capture_output=True)
        print(f"  ✅ MP3 변환 완료: {output_path}")
        
        # WAV 파일 삭제
        os.remove(wav_path)
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️ MP3 변환 실패. WAV 파일 유지: {wav_path}")
        print(f"     ffmpeg 오류: {e.stderr.decode()}")
        return True  # WAV는 성공했으므로 True
    except FileNotFoundError:
        print("  ⚠️ ffmpeg가 설치되어 있지 않습니다. WAV 파일 유지.")
        return True


async def main():
    # 출력 디렉토리
    output_dir = Path("docs/assets/audio")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 50)
    print("🎤 Day 4 Shadowing 오디오 생성")
    print("=" * 50)
    
    # Shadowing 문장들을 하나의 텍스트로 합치기 (문장 사이에 쉼표로 구분)
    # 각 문장 후 약간의 멈춤을 위해 줄바꿈 추가
    shadowing_text = "\n\n".join(SHADOWING_SENTENCES)
    
    output_file = output_dir / "week1_day4_shadowing.mp3"
    success = await generate_audio(shadowing_text, str(output_file))
    
    if success:
        print("\n" + "=" * 50)
        print("✅ 오디오 생성 완료!")
        print(f"📁 파일 위치: {output_file}")
        print("=" * 50)
    else:
        print("\n❌ 오디오 생성 실패")


if __name__ == "__main__":
    asyncio.run(main())
