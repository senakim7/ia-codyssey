import os
import wave
import csv
from datetime import datetime

import pyaudio
import speech_recognition as sr


class VoiceRecorder:
    def __init__(self):
        # 오디오 녹음 관련 설정
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.records_dir = 'records'

        # STT 인식을 위한 객체 초기화
        self.recognizer = sr.Recognizer()

        # records 폴더가 없을 경우 생성
        if not os.path.exists(self.records_dir):
            os.makedirs(self.records_dir)

    def record_audio(self, duration=5):
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )

        print('녹음을 시작합니다...')
        frames = []

        for _ in range(0, int(self.rate / self.chunk * duration)):
            data = stream.read(self.chunk)
            frames.append(data)

        print('녹음이 완료되었습니다.')

        stream.stop_stream()
        stream.close()
        audio.terminate()

        now = datetime.now()
        file_name = now.strftime('%Y%m%d-%H%M%S') + '.wav'
        file_path = os.path.join(self.records_dir, file_name)

        wave_file = wave.open(file_path, 'wb')
        wave_file.setnchannels(self.channels)
        wave_file.setsampwidth(audio.get_sample_size(self.format))
        wave_file.setframerate(self.rate)
        wave_file.writeframes(b''.join(frames))
        wave_file.close()

        print(f'파일이 성공적으로 저장되었습니다: {file_path}')

    def transcribe_audio_to_csv(self):
        # records 폴더 안의 모든 파일을 확인
        files = os.listdir(self.records_dir)

        for file_name in files:
            if file_name.endswith('.wav'):
                wav_path = os.path.join(self.records_dir, file_name)
                csv_file_name = file_name.replace('.wav', '.csv')
                csv_path = os.path.join(self.records_dir, csv_file_name)

                # 이미 변환된 CSV 파일이 존재하면 건너뜀
                if csv_file_name in files:
                    continue

                print(f'\n음성 인식을 시작합니다: {file_name}')
                results = []
                chunk_duration = 5.0  # 5초 단위로 끊어서 인식 (시간 기록 목적)

                # STT 라이브러리를 이용해 오디오 파일 열기
                with sr.AudioFile(wav_path) as source:
                    audio_duration = source.DURATION
                    current_offset = 0.0

                    # 오디오 길이만큼 지정된 시간 단위로 반복해서 읽기
                    while current_offset < audio_duration:
                        audio_data = self.recognizer.record(source, duration=chunk_duration)
                        time_stamp = f'{current_offset:.1f}초-{current_offset + chunk_duration:.1f}초'

                        try:
                            # 한국어(ko-KR)로 음성 인식 요청
                            text = self.recognizer.recognize_google(audio_data, language='ko-KR')
                        except sr.UnknownValueError:
                            text = '[음성 인식 불가 - 침묵 또는 잡음]'
                        except sr.RequestError:
                            text = '[네트워크 연결 오류 - STT 서비스 접근 불가]'

                        results.append([time_stamp, text])
                        current_offset += chunk_duration

                # CSV 파일로 저장
                with open(csv_path, 'w', newline='', encoding='utf-8') as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(['시간', '인식된_텍스트'])
                    writer.writerows(results)

                print(f'텍스트 변환 완료 및 저장됨: {csv_path}')

    def search_keyword_in_records(self, keyword):
        print(f'\n--- "{keyword}" 키워드 검색 결과 ---')

        if not os.path.exists(self.records_dir):
            print('기록된 폴더가 없습니다.')
            return

        files = os.listdir(self.records_dir)
        found_match = False

        for file_name in files:
            if file_name.endswith('.csv'):
                csv_path = os.path.join(self.records_dir, file_name)

                # CSV 파일을 읽어서 키워드 검색
                with open(csv_path, 'r', encoding='utf-8') as csv_file:
                    reader = csv.reader(csv_file)
                    next(reader, None)  # 첫 번째 줄(헤더) 건너뛰기

                    for row in reader:
                        # row의 길이가 정상적인지 확인 후 처리
                        if len(row) == 2:
                            time_stamp = row[0]
                            text = row[1]

                            # 검색하려는 키워드가 텍스트 안에 포함되어 있다면 출력
                            if keyword in text:
                                print(f'- 파일명: {file_name} | 시간: {time_stamp} | 내용: {text}')
                                found_match = True

        if not found_match:
            print('일치하는 검색 결과가 없습니다.')


if __name__ == '__main__':
    recorder = VoiceRecorder()

    # 1. 기존에 수행했던 녹음 (테스트를 위해 5초간 진행)
    recorder.record_audio(duration=5)

    # 2. 문제 8: 녹음된 WAV 파일들을 찾아 텍스트로 변환하고 CSV로 저장
    recorder.transcribe_audio_to_csv()

    # 3. 보너스 과제: 저장된 CSV 파일 안에서 특정 키워드 검색
    # (예시: 방금 녹음하면서 말했던 단어를 넣어보세요)
    recorder.search_keyword_in_records('테스트')