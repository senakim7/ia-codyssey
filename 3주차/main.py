import random  # 무작위 숫자(난수)를 뽑아주는 도구를 가져옵니다. 가짜 센서 값을 만들 때 씁니다.
import datetime  # 현재 날짜와 시간을 확인하는 도구를 가져옵니다. 파일에 기록 시간을 남길 때 씁니다.


class DummySensor:
    # DummySensor라는 이름의 '센서 기계 설계도'를 그리는 시작점입니다.
    def __init__(self):
        # 초기 설정 함수입니다. 기계 전원을 처음 켰을 때 가장 먼저 실행되는 준비 작업입니다.
        # 기계 내부에 데이터를 담아둘 보관함(사전 객체)을 만들고, 처음엔 모두 0.0으로 비워둡니다.
        self.env_values = {
            'mars_base_internal_temperature': 0.0,
            'mars_base_external_temperature': 0.0,
            'mars_base_internal_humidity': 0.0,
            'mars_base_external_illuminance': 0.0,
            'mars_base_internal_co2': 0.0,
            'mars_base_internal_oxygen': 0.0
        }

    def set_env(self):
        # 빈 보관함에 가짜 환경 데이터를 무작위로 생성해서 채워 넣는 함수입니다.
        # random.uniform()으로 주어진 범위의 난수를 뽑고, round()로 소수점 자리를 예쁘게 반올림합니다.
        self.env_values['mars_base_internal_temperature'] = round(random.uniform(18.0, 30.0), 2)
        self.env_values['mars_base_external_temperature'] = round(random.uniform(0.0, 21.0), 2)
        self.env_values['mars_base_internal_humidity'] = round(random.uniform(50.0, 60.0), 2)
        self.env_values['mars_base_external_illuminance'] = round(random.uniform(500.0, 715.0), 2)
        self.env_values['mars_base_internal_co2'] = round(random.uniform(0.02, 0.1), 4)
        self.env_values['mars_base_internal_oxygen'] = round(random.uniform(4.0, 7.0), 2)

    def get_env(self):
        # 지금까지 측정한 환경 값을 가져오고, 동시에 파일에 기록(Log)을 남기는 함수입니다.

        # 1. 현재 컴퓨터의 정확한 시간을 가져와서 사람이 보기 편한 글자 형태로 포장합니다.
        now = datetime.datetime.now()
        time_str = now.strftime('%Y-%m-%d %H:%M:%S')

        # 2. 파일에 쓸 한 줄의 문장을 만듭니다. (f-스트링을 써서 값들을 콤마로 이어 붙입니다)
        log_data = (
            f"{time_str}, "
            f"{self.env_values['mars_base_internal_temperature']}, "
            f"{self.env_values['mars_base_external_temperature']}, "
            f"{self.env_values['mars_base_internal_humidity']}, "
            f"{self.env_values['mars_base_external_illuminance']}, "
            f"{self.env_values['mars_base_internal_co2']}, "
            f"{self.env_values['mars_base_internal_oxygen']}\n"
        )

        # 3. 'sensor_log.txt' 파일을 열고, 기존 내용을 지우지 않고 맨 밑에 이어 씁니다. ('a' 모드)
        with open('sensor_log.txt', 'a', encoding='utf-8') as f:
            f.write(log_data)

        # 4. 최종 결과물(최신 센서 값이 담긴 보관함 전체)을 밖으로 뱉어내어 전달(Return)합니다.
        return self.env_values


# 여기서부터 진짜 프로그램이 시작된다는 신호입니다.
if __name__ == '__main__':
    # 설계도를 바탕으로 실제 기계 1대를 뚝딱 만들어 'ds'라는 이름을 붙여줍니다.
    ds = DummySensor()

    # 기계의 set_env 버튼을 눌러 가짜 데이터를 마구 생성해서 보관함을 채웁니다.
    ds.set_env()

    # 기계의 get_env 버튼을 눌러 파일에 기록을 남기고, 최신 센서 값들을 'current_env'라는 이름으로 받습니다.
    current_env = ds.get_env()

    # 사람이 볼 수 있게 화면(모니터)에 측정 결과를 예쁘게 출력해 줍니다.
    print('--- 화성 기지 환경 센서 측정 결과 ---')
    for key, value in current_env.items():
        print(f'{key}: {value}')
    print('\n[안내] 측정 결과가 sensor_log.txt 파일에 성공적으로 기록되었습니다.')