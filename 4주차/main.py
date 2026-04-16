import time
import json
import threading
import random
import os  # [추가] 시스템 기본 기능
import platform  # [추가] 시스템 종류 확인
import subprocess  # [추가] 시스템 명령어 실행 (wmic)


class DummySensor:
    def read_data(self):
        return {
            'mars_base_internal_temperature': round(random.uniform(20.0, 25.0), 2),
            'mars_base_external_temperature': round(random.uniform(-60.0, -20.0), 2),
            'mars_base_internal_humidity': round(random.uniform(30.0, 50.0), 2),
            'mars_base_external_illuminance': round(random.uniform(100.0, 1000.0), 2),
            'mars_base_internal_co2': round(random.uniform(400.0, 600.0), 2),
            'mars_base_internal_oxygen': round(random.uniform(19.0, 21.0), 2)
        }


class MissionComputer:
    def __init__(self):
        # [기존 기능] 환경 변수 및 화성 시간 측정용
        self.env_values = {
            'mars_base_internal_temperature': 0.0,
            'mars_base_external_temperature': 0.0,
            'mars_base_internal_humidity': 0.0,
            'mars_base_external_illuminance': 0.0,
            'mars_base_internal_co2': 0.0,
            'mars_base_internal_oxygen': 0.0
        }
        self.ds = DummySensor()
        self.is_running = True
        self.history_data = []
        self.mission_start_time = time.time()

        # [추가 기능] 시스템 정보 설정을 위한 setting.txt 읽어오기
        self.settings = self._load_settings()

    # ---------------------------------------------------------
    # [추가된 구역] 미션 컴퓨터 시스템 진단 메서드들
    # ---------------------------------------------------------
    def _load_settings(self):
        settings = []
        try:
            with open('setting.txt', 'r', encoding='utf-8') as f:
                for line in f:
                    clean_line = line.strip()
                    if clean_line:
                        settings.append(clean_line)
        except FileNotFoundError:
            # 파일이 없어도 정상 작동하도록 예외처리
            pass
        return settings

    def _filter_data(self, data_dict):
        if not self.settings:
            return data_dict
        return {k: v for k, v in data_dict.items() if k in self.settings}

    def get_mission_computer_info(self):
        info = {}
        try:
            info['os'] = platform.system()
            info['os_version'] = platform.version()
            info['cpu_type'] = platform.processor()
            info['cpu_cores'] = os.cpu_count()

            memory_size = 'Unknown'
            if info['os'] == 'Windows':
                result = subprocess.check_output(['wmic', 'computersystem', 'get', 'TotalPhysicalMemory']).decode()
                mem_bytes = [line.strip() for line in result.split('\n') if line.strip().isdigit()]
                if mem_bytes:
                    memory_size = f'{round(int(mem_bytes[0]) / (1024 ** 3), 2)} GB'
            elif info['os'] == 'Linux':
                with open('/proc/meminfo', 'r') as f:
                    for line in f:
                        if 'MemTotal' in line:
                            mem_kb = int(line.split()[1])
                            memory_size = f'{round(mem_kb / (1024 ** 2), 2)} GB'
                            break
            info['memory_size'] = memory_size
        except Exception as e:
            pass

        filtered_info = self._filter_data(info)
        return json.dumps(filtered_info, indent=4, ensure_ascii=False)

    def get_mission_computer_load(self):
        load = {}
        try:
            os_system = platform.system()
            cpu_usage = 'Unknown'
            memory_usage = 'Unknown'

            if os_system == 'Windows':
                cpu_result = subprocess.check_output(['wmic', 'cpu', 'get', 'loadpercentage']).decode()
                cpu_val = [line.strip() for line in cpu_result.split('\n') if line.strip().isdigit()]
                if cpu_val:
                    cpu_usage = f'{cpu_val[0]}%'

                mem_result = subprocess.check_output(
                    ['wmic', 'os', 'get', 'FreePhysicalMemory,TotalVisibleMemorySize', '/Value']).decode()
                mem_info = {}
                for line in mem_result.split('\n'):
                    if '=' in line:
                        key, val = line.strip().split('=')
                        mem_info[key] = int(val)

                if 'TotalVisibleMemorySize' in mem_info and 'FreePhysicalMemory' in mem_info:
                    total = mem_info['TotalVisibleMemorySize']
                    free = mem_info['FreePhysicalMemory']
                    used = total - free
                    memory_usage = f'{round((used / total) * 100, 1)}%'

            load['cpu_usage'] = cpu_usage
            load['memory_usage'] = memory_usage
        except Exception as e:
            pass

        filtered_load = self._filter_data(load)
        return json.dumps(filtered_load, indent=4, ensure_ascii=False)

    # ---------------------------------------------------------
    # [기존 구역] 화성 시간 및 센서 데이터 처리 메서드들
    # ---------------------------------------------------------
    def get_mars_time(self):
        earth_elapsed = time.time() - self.mission_start_time
        mars_elapsed = earth_elapsed / 1.02749
        mars_sols = int(mars_elapsed // 86400)
        leftover = mars_elapsed % 86400
        mars_hours = int(leftover // 3600)
        leftover = leftover % 3600
        mars_minutes = int(leftover // 60)
        mars_seconds = int(leftover % 60)
        return f"Sol {mars_sols} - {mars_hours:02d}:{mars_minutes:02d}:{mars_seconds:02d}"

    def get_sensor_data(self):
        while self.is_running:
            new_data = self.ds.read_data()
            self.env_values.update(new_data)
            self.history_data.append(new_data)

            print(f'\n====================================')
            print(f'   현재 화성 기지 시간: {self.get_mars_time()}')
            print(f'====================================')
            print('[현재 화성 기지 환경]')
            print(json.dumps(self.env_values, indent=4))

            if len(self.history_data) >= 60:
                self._print_5min_average()
                self.history_data.clear()

            for _ in range(5):
                if not self.is_running:
                    break
                time.sleep(1)

    def _print_5min_average(self):
        print('\n[알림: 5분 평균 데이터 출력]')
        avg_values = {}
        for key in self.env_values.keys():
            total_sum = sum(data[key] for data in self.history_data)
            avg_values[key] = round(total_sum / len(self.history_data), 2)
        print(json.dumps(avg_values, indent=4))


if __name__ == '__main__':
    # 인스턴스화
    RunComputer = MissionComputer()

    # --- [과제 요구사항] 시스템 정보 출력 확인 ---
    print('>>> 시스템 정보 스캔 시작...\n')
    print('--- 미션 컴퓨터 시스템 기본 정보 ---')
    print(RunComputer.get_mission_computer_info())

    print('\n--- 미션 컴퓨터 실시간 부하 상태 ---')
    print(RunComputer.get_mission_computer_load())
    print('\n>>> 센서 데이터 모니터링을 시작합니다...\n')
    # -----------------------------------------------

    # 기존 스레드(센서 데이터 가져오기) 실행
    sensor_thread = threading.Thread(target=RunComputer.get_sensor_data)
    sensor_thread.daemon = True
    sensor_thread.start()

    while RunComputer.is_running:
        try:
            user_input = input('특정 키(S)를 입력하면 시스템이 정지됩니다.\n')
            if user_input.lower() == 's':
                RunComputer.is_running = False
                print('System stopped....')
                break
        except KeyboardInterrupt:
            RunComputer.is_running = False
            print('System stopped....')
            break
