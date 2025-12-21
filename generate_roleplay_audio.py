"""
Gemini Live API를 사용한 역할극(Role Play) 오디오 생성 스크립트

A/B 두 화자를 다른 목소리로 생성하고 공백을 삽입하여 합칩니다.

## 사용법
python generate_roleplay_audio.py
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
SAMPLE_WIDTH = 2
SILENCE_DURATION = 3.0  # 대사 사이 공백 (초)

# 모델 설정
MODEL = "models/gemini-2.5-flash-native-audio-preview-12-2025"

# API 클라이언트
client = genai.Client(
    http_options={"api_version": "v1beta"},
    api_key=os.environ.get("GEMINI_API_KEY"),
)

# 역할극 대사 (A는 James - 남성, B는 Yuna - 여성)
ROLEPLAY_LINES = [
    ("A", "Hi! Nice to meet you. My name is James."),
    ("B", "Nice to meet you too, James. I'm Yuna. What do you do?"),
    ("A", "I'm a software engineer. I work at a tech company. How about you?"),
    ("B", "I'm a teacher. I teach at an elementary school."),
    ("A", "That's great! Where are you from?"),
    ("B", "I'm from Korea. And you?"),
    ("A", "I'm from the United States, but I live in Korea now."),
    ("B", "Wonderful! It was nice talking to you."),
    ("A", "You too! See you later!"),
]

# 화자별 음성 설정
VOICE_CONFIG_A = types.LiveConnectConfig(
    response_modalities=["AUDIO"],
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck")  # 남성 음성
        )
    ),
)

VOICE_CONFIG_B = types.LiveConnectConfig(
    response_modalities=["AUDIO"],
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore")  # 여성 음성
        )
    ),
)


async def generate_line(speaker: str, text: str, output_path: str) -> bool:
    """대사를 오디오로 변환하여 WAV 저장"""
    config = VOICE_CONFIG_A if speaker == "A" else VOICE_CONFIG_B
    voice_name = "Puck (James)" if speaker == "A" else "Kore (Yuna)"
    print(f"  🎤 [{speaker}] {voice_name}: {text[:35]}...")
    
    audio_chunks = []
    
    try:
        async with client.aio.live.connect(model=MODEL, config=config) as session:
            await session.send(
                input=f"Read this line naturally in a friendly conversational tone: {text}",
                end_of_turn=True
            )
            
            turn = session.receive()
            async for response in turn:
                if data := response.data:
                    audio_chunks.append(data)
        
        if not audio_chunks:
            print(f"    ❌ 오디오 데이터 없음")
            return False
        
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
        with wave.open(wav_path, "rb") as wav_file:
            combined_data += wav_file.readframes(wav_file.getnframes())
        
        if i < len(wav_files) - 1:
            with wave.open(silence_path, "rb") as silence_file:
                combined_data += silence_file.readframes(silence_file.getnframes())
    
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
    output_dir = Path("docs/assets/audio")
    temp_dir = output_dir / "temp_roleplay"
    output_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("🎭 Day 4 Role Play 오디오 생성")
    print("=" * 60)
    print(f"📝 총 {len(ROLEPLAY_LINES)}개 대사")
    print(f"🎤 A (James): Puck 음성")
    print(f"🎤 B (Yuna): Kore 음성")
    print(f"⏱️ 대사 사이 공백: {SILENCE_DURATION}초")
    print("=" * 60)
    
    wav_files = []
    for i, (speaker, line) in enumerate(ROLEPLAY_LINES, 1):
        wav_path = temp_dir / f"line_{i:02d}.wav"
        success = await generate_line(speaker, line, str(wav_path))
        if success:
            wav_files.append(str(wav_path))
            print(f"    ✅ 대사 {i}/{len(ROLEPLAY_LINES)} 완료")
        else:
            print(f"    ❌ 대사 {i}/{len(ROLEPLAY_LINES)} 실패")
        
        await asyncio.sleep(1)
    
    if len(wav_files) != len(ROLEPLAY_LINES):
        print(f"\n⚠️ 일부 대사 생성 실패. {len(wav_files)}/{len(ROLEPLAY_LINES)} 완료")
    
    silence_path = temp_dir / "silence.wav"
    create_silence_wav(SILENCE_DURATION, str(silence_path))
    print(f"\n🔇 공백 파일 생성: {SILENCE_DURATION}초")
    
    combined_wav = output_dir / "week1_day4_roleplay.wav"
    combine_wav_files(wav_files, str(silence_path), str(combined_wav))
    
    final_mp3 = output_dir / "week1_day4_roleplay.mp3"
    if convert_to_mp3(str(combined_wav), str(final_mp3)):
        import shutil
        shutil.rmtree(temp_dir)
        os.remove(combined_wav)
        print("\n🧹 임시 파일 정리 완료")
    
    print("\n" + "=" * 60)
    print("✅ Role Play 오디오 생성 완료!")
    print(f"📁 파일 위치: {final_mp3}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
