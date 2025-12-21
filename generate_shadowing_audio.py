"""
Gemini Live API를 사용한 Shadowing 오디오 생성 스크립트 (v2)

각 문장을 개별 생성 후 공백을 삽입하여 합칩니다.

## 사용법
python generate_shadowing_audio.py

## 필요 패키지
pip install google-genai pydub
"""

import os
import asyncio
import wave
import subprocess
from pathlib import Path
import struct

from google import genai
from google.genai import types

# 오디오 설정
RECEIVE_SAMPLE_RATE = 24000
CHANNELS = 1
SAMPLE_WIDTH = 2  # 16-bit audio = 2 bytes
SILENCE_DURATION = 4.0  # 문장 사이 공백 (초)

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

# Day 4 Shadowing 문장들
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


async def generate_single_sentence(text: str, output_path: str) -> bool:
    """단일 문장을 오디오로 변환하여 WAV 저장"""
    print(f"  🎤 생성 중: {text[:30]}...")
    
    audio_chunks = []
    
    try:
        async with client.aio.live.connect(model=MODEL, config=CONFIG) as session:
            await session.send(
                input=f"Read this sentence naturally in a warm, conversational tone: {text}",
                end_of_turn=True
            )
            
            turn = session.receive()
            async for response in turn:
                if data := response.data:
                    audio_chunks.append(data)
        
        if not audio_chunks:
            print(f"    ❌ 오디오 데이터 없음")
            return False
        
        # PCM 데이터 결합 및 WAV 저장
        pcm_data = b"".join(audio_chunks)
        with wave.open(output_path, "wb") as wav_file:
            wav_file.setnchannels(CHANNELS)
            wav_file.setsampwidth(SAMPLE_WIDTH)
            wav_file.setframerate(RECEIVE_SAMPLE_RATE)
            wav_file.writeframes(pcm_data)
        
        return True
    except Exception as e:
        print(f"    ❌ 오류: {e}")
        return False


def create_silence_wav(duration: float, output_path: str):
    """지정된 길이의 무음 WAV 파일 생성"""
    num_samples = int(RECEIVE_SAMPLE_RATE * duration)
    silence_data = struct.pack('<' + 'h' * num_samples, *([0] * num_samples))
    
    with wave.open(output_path, "wb") as wav_file:
        wav_file.setnchannels(CHANNELS)
        wav_file.setsampwidth(SAMPLE_WIDTH)
        wav_file.setframerate(RECEIVE_SAMPLE_RATE)
        wav_file.writeframes(silence_data)


def combine_wav_files(wav_files: list, silence_path: str, output_path: str):
    """WAV 파일들을 공백과 함께 합치기"""
    print(f"\n📦 오디오 파일 합치는 중...")
    
    combined_data = b""
    
    for i, wav_path in enumerate(wav_files):
        # 문장 오디오 추가
        with wave.open(wav_path, "rb") as wav_file:
            combined_data += wav_file.readframes(wav_file.getnframes())
        
        # 마지막 문장이 아니면 공백 추가
        if i < len(wav_files) - 1:
            with wave.open(silence_path, "rb") as silence_file:
                combined_data += silence_file.readframes(silence_file.getnframes())
    
    # 합친 WAV 저장
    with wave.open(output_path, "wb") as output_wav:
        output_wav.setnchannels(CHANNELS)
        output_wav.setsampwidth(SAMPLE_WIDTH)
        output_wav.setframerate(RECEIVE_SAMPLE_RATE)
        output_wav.writeframes(combined_data)
    
    print(f"  ✅ WAV 저장 완료: {output_path}")


def convert_to_mp3(wav_path: str, mp3_path: str) -> bool:
    """WAV를 MP3로 변환"""
    try:
        subprocess.run([
            "ffmpeg", "-y", "-i", wav_path,
            "-codec:a", "libmp3lame", "-qscale:a", "2",
            mp3_path
        ], check=True, capture_output=True)
        print(f"  ✅ MP3 변환 완료: {mp3_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️ MP3 변환 실패: {e.stderr.decode()}")
        return False
    except FileNotFoundError:
        print("  ⚠️ ffmpeg가 설치되어 있지 않습니다.")
        return False


async def main():
    # 출력 디렉토리
    output_dir = Path("docs/assets/audio")
    temp_dir = output_dir / "temp_shadowing"
    output_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("🎤 Day 4 Shadowing 오디오 생성 (공백 삽입 버전)")
    print("=" * 60)
    print(f"📝 총 {len(SHADOWING_SENTENCES)}개 문장")
    print(f"⏱️ 문장 사이 공백: {SILENCE_DURATION}초")
    print("=" * 60)
    
    # 1. 각 문장 개별 생성
    wav_files = []
    for i, sentence in enumerate(SHADOWING_SENTENCES, 1):
        wav_path = temp_dir / f"sentence_{i:02d}.wav"
        success = await generate_single_sentence(sentence, str(wav_path))
        if success:
            wav_files.append(str(wav_path))
            print(f"    ✅ 문장 {i}/10 완료")
        else:
            print(f"    ❌ 문장 {i}/10 실패")
        
        # API 제한 방지를 위한 짧은 대기
        await asyncio.sleep(1)
    
    if len(wav_files) != len(SHADOWING_SENTENCES):
        print(f"\n⚠️ 일부 문장 생성 실패. {len(wav_files)}/{len(SHADOWING_SENTENCES)} 완료")
    
    # 2. 공백 WAV 파일 생성
    silence_path = temp_dir / "silence.wav"
    create_silence_wav(SILENCE_DURATION, str(silence_path))
    print(f"\n🔇 공백 파일 생성: {SILENCE_DURATION}초")
    
    # 3. 모든 파일 합치기
    combined_wav = output_dir / "week1_day4_shadowing.wav"
    combine_wav_files(wav_files, str(silence_path), str(combined_wav))
    
    # 4. MP3로 변환
    final_mp3 = output_dir / "week1_day4_shadowing.mp3"
    if convert_to_mp3(str(combined_wav), str(final_mp3)):
        # 임시 파일 정리
        import shutil
        shutil.rmtree(temp_dir)
        os.remove(combined_wav)
        print("\n🧹 임시 파일 정리 완료")
    
    print("\n" + "=" * 60)
    print("✅ Shadowing 오디오 생성 완료!")
    print(f"📁 파일 위치: {final_mp3}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
