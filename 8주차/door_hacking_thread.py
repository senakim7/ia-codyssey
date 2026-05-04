import zipfile
import multiprocessing
import string
import time
from datetime import datetime
import os

ZIP_FILE = 'emergency_storage_key.zip'
OUTPUT_FILE = 'password.txt'

CHARSET = string.ascii_lowercase + string.digits
BASE = len(CHARSET)
PASSWORD_LENGTH = 6

PROCESS_COUNT = multiprocessing.cpu_count()

start_time = time.time()
attempt_counter = multiprocessing.Value('i', 0)


def index_to_pw(idx):
    pw = ''
    for _ in range(PASSWORD_LENGTH):
        pw = CHARSET[idx % BASE] + pw
        idx //= BASE
    return pw


def worker(start, end, counter):
    try:
        zf = zipfile.ZipFile(ZIP_FILE)
        file_name = zf.namelist()[0]
    except Exception as e:
        print('ZIP 오류:', e)
        return

    for i in range(start, end):
        password = index_to_pw(i)

        with counter.get_lock():
            counter.value += 1
            count = counter.value

        try:
            # 🔥 핵심: extractall ❌ → open + read
            f = zf.open(file_name, pwd=password.encode())
            f.read(1)

            duration = time.time() - start_time

            print('\n[+] 성공!')
            print('[+] 비밀번호:', password)
            print('[+] 시도 횟수:', count)
            print('[+] 시간:', round(duration, 2), '초')

            with open(OUTPUT_FILE, 'w') as f:
                f.write(password)

            os._exit(0)

        except:
            pass

        if count % 100000 == 0:
            print(f'[{os.getpid()}] {count:,} 시도... {time.time() - start_time:.1f}초')


def unlock_zip():
    total = BASE ** PASSWORD_LENGTH
    chunk = total // PROCESS_COUNT

    print('[*] CPU:', PROCESS_COUNT)
    print('[*] 총 경우:', total)
    print('[*] 시작:', datetime.fromtimestamp(start_time))

    processes = []

    for i in range(PROCESS_COUNT):
        start = i * chunk
        end = total if i == PROCESS_COUNT - 1 else (i + 1) * chunk

        p = multiprocessing.Process(target=worker, args=(start, end, attempt_counter))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()


if __name__ == '__main__':
    unlock_zip()