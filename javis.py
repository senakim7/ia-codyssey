import os
import wave
from datetime import datetime

import pyaudio


class VoiceRecorder:
    def __init__(self):
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.records_dir = 'records'

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

        # 설정한 duration(초) 만큼 마이크 데이터를 읽어와 리스트에 저장
        for _ in range(0, int(self.rate / self.chunk * duration)):
            data = stream.read(self.chunk)
            frames.append(data)

        print('녹음이 완료되었습니다.')

        # 오디오 스트림 종료 및 리소스 해제
        stream.stop_stream()
        stream.close()
        audio.terminate()

        # 현재 시간을 기준으로 파일명 생성 (년월일-시간분초 포맷)
        now = datetime.now()
        file_name = now.strftime('%Y%m%d-%H%M%S') + '.wav'
        file_path = os.path.join(self.records_dir, file_name)

        # wave 모듈을 사용해 wav 파일로 저장
        wave_file = wave.open(file_path, 'wb')
        wave_file.setnchannels(self.channels)
        wave_file.setsampwidth(audio.get_sample_size(self.format))
        wave_file.setframerate(self.rate)
        wave_file.writeframes(b''.join(frames))
        wave_file.close()

        print(f'파일이 성공적으로 저장되었습니다: {file_path}')

    def show_records_by_date(self, start_date, end_date):
        if not os.path.exists(self.records_dir):
            print('저장된 녹음 파일이 없습니다.')
            return

        files = os.listdir(self.records_dir)
        matched_files = []

        # 특정 날짜 범위에 해당하는 파일 필터링
        for file_name in files:
            if file_name.endswith('.wav'):
                file_date = file_name.split('-')[0]
                if start_date <= file_date <= end_date:
                    matched_files.append(file_name)

        if matched_files:
            print(f'\n{start_date} 부터 {end_date} 까지의 녹음 파일 목록:')
            for matched_file in matched_files:
                print(f'- {matched_file}')
        else:
            print('\n해당 기간에 일치하는 녹음 파일이 없습니다.')


if __name__ == '__main__':
    recorder = VoiceRecorder()

    # 기본 5초 동안 음성을 녹음하고 records 폴더에 저장합니다.
    recorder.record_audio(duration=5)

    # 보너스 과제: 특정 날짜 범위의 녹음 파일 목록을 출력합니다.
    # 예시: 2026년 5월 1일부터 2026년 5월 31일까지의 기록 검색
    recorder.show_records_by_date('20260501', '20260531')