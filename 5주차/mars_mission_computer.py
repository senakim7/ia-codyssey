import os  # 운영체제의 기본 기능(CPU 코어 수 확인 등)을 사용하기 위해 불러옵니다.
import json  # 수집한 데이터를 깔끔한 JSON 형식(텍스트)으로 만들어 출력하기 위해 불러옵니다.
import platform  # 현재 컴퓨터의 하드웨어와 운영체제(Windows인지 Linux인지 등) 기본 정보를 알기 위해 불러옵니다.
import subprocess  # ★ 핵심: 외부 라이브러리를 설치할 수 없으므로, 윈도우/리눅스의 '명령 프롬프트'에 명령어를 직접 입력하고 그 결과를 파이썬으로 가져오기 위해 불러옵니다.


class MissionComputer:
    """
    미션 컴퓨터의 정보를 수집하고 부하 상태를 파악하는 모든 기능을 담은 설계도(클래스)입니다.
    이렇게 클래스로 묶어두면 나중에 다른 우주 기지 컴퓨터에도 쉽게 재사용할 수 있습니다.
    """

    def __init__(self):
        # 이 클래스가 실행(인스턴스화)될 때 가장 먼저 자동으로 실행되는 준비 단계입니다.
        # 출력하고 싶은 항목이 적힌 setting.txt 파일을 미리 읽어와서 자기 자신(self)의 기억 공간에 저장해 둡니다.
        self.settings = self._load_settings()

    def _load_settings(self):
        """
        보너스 과제: setting.txt 파일을 읽어와서 어떤 정보만 출력할지 결정하는 숨겨진 메서드입니다.
        메서드 이름 앞에 '_'를 붙인 이유는 "이 클래스 내부에서만 쓸 거니까 밖에서는 건드리지 마세요"라는 의미(파이썬의 관례)입니다.
        """
        settings = []  # 읽어온 설정값들을 차곡차곡 담을 빈 바구니(리스트)를 만듭니다.

        try:
            # setting.txt 파일을 읽기 모드('r')로 엽니다. 글자가 깨지지 않게 utf-8 인코딩을 씁니다.
            with open('setting.txt', 'r', encoding='utf-8') as f:
                for line in f:  # 파일의 내용을 한 줄씩 읽어옵니다.
                    clean_line = line.strip()  # 양옆의 띄어쓰기나 줄바꿈 문자(엔터)를 깔끔하게 지웁니다.
                    if clean_line:  # 만약 지웠는데도 글자가 남아있다면 (즉, 빈 줄이 아니라면)
                        settings.append(clean_line)  # 바구니에 담습니다.

        except FileNotFoundError:
            # 우주 기지 컴퓨터에 setting.txt 파일이 누락되었을 수도 있습니다.
            # 파일이 없다고 프로그램이 뻗어버리면 안 되므로, 에러를 부드럽게 넘기고 안내 메시지만 띄웁니다.
            print('setting.txt 파일을 찾을 수 없어 전체 정보를 출력합니다.')
        except Exception as e:
            # 그 외에 파일에 접근할 권한이 없거나 하는 예상치 못한 에러를 방어합니다.
            print(f'설정 파일을 읽는 중 예기치 못한 오류가 발생했습니다: {e}')

        return settings  # 완성된 설정 바구니를 반환합니다. (파일이 없었다면 빈 바구니가 반환됩니다.)

    def _filter_data(self, data_dict):
        """
        수집한 방대한 데이터 중에서 setting.txt에 적힌 항목만 남기고 나머지는 버리는 역할을 합니다.
        """
        # 만약 settings 바구니가 비어있다면 (설정 파일이 없었다면) 필터링할 필요 없이 원본 데이터를 그대로 돌려줍니다.
        if not self.settings:
            return data_dict

        # 수집된 데이터(data_dict)를 하나씩 확인하면서, 그 이름(k)이 설정 바구니(self.settings)에 있을 때만 새 딕셔너리로 만듭니다.
        return {k: v for k, v in data_dict.items() if k in self.settings}

    def get_mission_computer_info(self):
        """
        미션 컴퓨터의 변하지 않는 기본 정보(OS, CPU 종류, 전체 메모리 등)를 수집합니다.
        """
        info = {}  # 정보를 담을 빈 딕셔너리를 만듭니다.

        try:
            # 기본 모듈들을 이용해 쉽게 알 수 있는 정보들을 수집합니다.
            info['os'] = platform.system()  # 예: 'Windows', 'Linux'
            info['os_version'] = platform.version()  # 예: '10.0.26200'
            info['cpu_type'] = platform.processor()  # 예: 'Intel64 Family 6...'
            info['cpu_cores'] = os.cpu_count()  # CPU의 두뇌(코어)가 몇 개인지 셉니다.

            memory_size = 'Unknown'  # 메모리 크기를 당장 알 수 없으니 일단 '알 수 없음'으로 설정합니다.

            # 여기서부터 외부 라이브러리 없이 메모리를 알아내는 핵심 기술이 들어갑니다.
            if info['os'] == 'Windows':
                # subprocess를 써서 윈도우 명령 프롬프트에 'wmic computersystem get TotalPhysicalMemory'를 숨겨서 입력합니다.
                # 이 명령어는 컴퓨터의 총 물리 메모리(바이트 단위)를 알려주는 윈도우 전용 명령어입니다.
                result = subprocess.check_output(['wmic', 'computersystem', 'get', 'TotalPhysicalMemory']).decode()

                # 명령어 결과에서 숫자만 골라내기 위해 줄바꿈(\n)으로 쪼개고, 숫자로만 이루어진 줄을 찾습니다.
                mem_bytes = [line.strip() for line in result.split('\n') if line.strip().isdigit()]

                if mem_bytes:  # 숫자를 성공적으로 찾았다면
                    # 바이트 단위를 기가바이트(GB)로 바꾸기 위해 1024의 3제곱으로 나눕니다.
                    # round(..., 2)를 써서 소수점 둘째 자리까지만 깔끔하게 자릅니다.
                    memory_size = f'{round(int(mem_bytes[0]) / (1024 ** 3), 2)} GB'

            elif info['os'] == 'Linux':
                # 미션 컴퓨터가 리눅스라면 wmic 명령어가 안 먹힙니다.
                # 대신 리눅스는 메모리 정보가 '/proc/meminfo'라는 파일에 항상 기록되므로 이 파일을 직접 열어서 읽습니다.
                with open('/proc/meminfo', 'r') as f:
                    for line in f:
                        if 'MemTotal' in line:  # 총 메모리 용량이 적힌 줄을 찾습니다.
                            mem_kb = int(line.split()[1])  # 숫자(킬로바이트)만 떼어냅니다.
                            memory_size = f'{round(mem_kb / (1024 ** 2), 2)} GB'  # KB를 GB로 변환합니다.
                            break

            info['memory_size'] = memory_size  # 최종 계산된 메모리 크기를 딕셔너리에 넣습니다.

        except Exception as e:
            # 명령어를 실행하다가 권한이 없어서 튕기더라도 시스템이 다운되지 않게 에러 메시지만 출력하고 넘어갑니다.
            print(f'시스템 정보를 수집하는 중 오류가 발생했습니다: {e}')

        # 설정 파일(setting.txt)을 기준으로 출력하지 않을 항목은 잘라냅니다.
        filtered_info = self._filter_data(info)

        # 파이썬 딕셔너리를 예쁜 형태의 JSON 문자열로 바꿔서 반환합니다. (한글 깨짐 방지를 위해 ensure_ascii=False 사용)
        return json.dumps(filtered_info, indent=4, ensure_ascii=False)

    def get_mission_computer_load(self):
        """
        미션 컴퓨터가 지금 얼마나 헐떡이고 있는지(CPU, 메모리 실시간 사용률)를 측정합니다.
        """
        load = {}  # 부하 정보를 담을 빈 딕셔너리입니다.

        try:
            os_system = platform.system()  # 현재 윈도우인지 리눅스인지 다시 확인합니다.
            cpu_usage = 'Unknown'
            memory_usage = 'Unknown'

            if os_system == 'Windows':
                # [CPU 부하 측정]
                # 윈도우 명령어인 'wmic cpu get loadpercentage'를 백그라운드에서 실행해 현재 CPU 사용률(%)을 가져옵니다.
                cpu_result = subprocess.check_output(['wmic', 'cpu', 'get', 'loadpercentage']).decode()
                # 결과 텍스트에서 숫자만 찾아냅니다.
                cpu_val = [line.strip() for line in cpu_result.split('\n') if line.strip().isdigit()]
                if cpu_val:
                    cpu_usage = f'{cpu_val[0]}%'

                # [메모리 부하 측정]
                # 윈도우 명령어 'wmic os get FreePhysicalMemory,TotalVisibleMemorySize /Value'를 실행합니다.
                # 이 명령어는 '남은 메모리'와 '전체 메모리'를 알려줍니다. (단위는 KB)
                mem_result = subprocess.check_output(
                    ['wmic', 'os', 'get', 'FreePhysicalMemory,TotalVisibleMemorySize', '/Value']).decode()
                mem_info = {}

                # 명령어 결과가 '항목=값' 형태로 나오기 때문에, '='를 기준으로 잘라서 딕셔너리에 정리합니다.
                for line in mem_result.split('\n'):
                    if '=' in line:
                        key, val = line.strip().split('=')
                        mem_info[key] = int(val)

                # '전체 메모리'와 '남은 메모리' 값을 무사히 가져왔다면 계산을 시작합니다.
                if 'TotalVisibleMemorySize' in mem_info and 'FreePhysicalMemory' in mem_info:
                    total = mem_info['TotalVisibleMemorySize']  # 전체 메모리
                    free = mem_info['FreePhysicalMemory']  # 안 쓰고 남은 메모리
                    used = total - free  # 현재 사용 중인 메모리 (전체 - 남은 거)
                    # (사용 중인 메모리 / 전체 메모리) * 100을 해서 % 퍼센트 단위로 만듭니다.
                    memory_usage = f'{round((used / total) * 100, 1)}%'

            elif os_system == 'Linux':
                # 리눅스 환경의 부하 측정은 /proc/stat 파일을 읽어서 복잡하게 계산해야 하므로,
                # 현재는 Windows 환경임이 확인되었기에 복잡도를 줄이고자 생략(또는 안내 문구) 처리했습니다.
                cpu_usage = 'Linux CPU measurement logic needed'
                memory_usage = 'Linux Mem measurement logic needed'

            # 계산된 사용량을 딕셔너리에 넣습니다.
            load['cpu_usage'] = cpu_usage
            load['memory_usage'] = memory_usage

        except Exception as e:
            print(f'실시간 부하 정보를 수집하는 중 오류가 발생했습니다: {e}')

        # 마찬가지로 설정 파일 기준에 맞춰 필터링하고 JSON으로 예쁘게 포장해서 돌려줍니다.
        filtered_load = self._filter_data(load)
        return json.dumps(filtered_load, indent=4, ensure_ascii=False)


# =====================================================================
# 여기서부터는 이 파이썬 파일이 실제로 '실행'되었을 때만 작동하는 부분입니다.
# 다른 파일에서 이 코드를 import해서 쓸 때는 아래 코드가 실행되지 않습니다.
# =====================================================================
if __name__ == '__main__':
    # 1. 요구사항에 따라 MissionComputer 설계도를 바탕으로 'runComputer'라는 실제 컴퓨터 객체를 만듭니다.
    runComputer = MissionComputer()

    # 2. 미션 컴퓨터의 기본 정보(정적 정보)를 모아서 화면에 출력합니다.
    print('--- 미션 컴퓨터 시스템 기본 정보 ---')
    print(runComputer.get_mission_computer_info())

    # 3. 미션 컴퓨터가 지금 얼마나 힘든지(부하 정보)를 모아서 화면에 출력합니다.
    print('\n--- 미션 컴퓨터 실시간 부하 상태 ---')
    print(runComputer.get_mission_computer_load())