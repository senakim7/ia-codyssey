import time
import json
import threading
import random
# 시간을 더 정밀하게 다루기 위한 기본 도구(물론 허용됩니다!)
import datetime


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

        # [추가된 부분] 컴퓨터에 전원이 들어온 '지구 시간'을 찰칵! 사진 찍듯 기록해 둡니다.
        # 이것이 화성 임무의 시작 시간(Sol 0)이 됩니다.
        self.mission_start_time = time.time()

    def get_mars_time(self):
        # [핵심 수학 원리]
        # 지구의 1일은 86,400초입니다. (24시간 * 60분 * 60초)
        # 화성의 1일(Sol)은 약 88,775초입니다.
        # 즉, 화성의 시간은 지구보다 1.02749배 천천히 흐릅니다. (88775 / 86400)

        # 1. 전원이 켜진 후 '지구 시간'으로 몇 초가 지났는지 계산합니다.
        earth_elapsed = time.time() - self.mission_start_time

        # 2. 이 시간을 1.02749로 나누면 '화성 시간'으로 몇 초가 지났는지 알 수 있습니다.
        mars_elapsed = earth_elapsed / 1.02749

        # 3. 화성 시간 초(second)를 다시 일(Sol), 시간, 분, 초로 예쁘게 나눕니다.
        # // 는 몫을 구하는 기호, % 는 나머지를 구하는 기호입니다!
        mars_sols = int(mars_elapsed // 86400)
        leftover = mars_elapsed % 86400
        mars_hours = int(leftover // 3600)
        leftover = leftover % 3600
        mars_minutes = int(leftover // 60)
        mars_seconds = int(leftover % 60)

        # f"..." 는 문자를 예쁘게 조립해 주는 기능입니다.
        # :02d 는 숫자가 한 자리여도 '01', '09'처럼 두 자리로 보여달라는 뜻이에요.
        return f"Sol {mars_sols} - {mars_hours:02d}:{mars_minutes:02d}:{mars_seconds:02d}"

    def get_sensor_data(self):
        while self.is_running:
            new_data = self.ds.read_data()
            self.env_values.update(new_data)
            self.history_data.append(new_data)

            # [추가된 부분] 방금 만든 화성 시계를 출력합니다!
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
    RunComputer = MissionComputer()

    sensor_thread = threading.Thread(target=RunComputer.get_sensor_data)
    sensor_thread.daemon = True
    sensor_thread.start()

    while RunComputer.is_running:
        try:
            user_input = input('특정 키(S)를 입력하면 시스템이 정지됩니다.\n')
            if user_input.lower() == 's':
                RunComputer.is_running = False
                print('Sytem stoped....')
                break
        except KeyboardInterrupt:
            RunComputer.is_running = False
            print('Sytem stoped....')
            break