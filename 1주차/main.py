def read_large_file_in_reverse(file_path, chunk_size=8192):
    """
    O(1) 메모리 공간 복잡도를 유지하며 대용량 로그 파일을 역순으로 읽어 들이는 제너레이터 함수.
    이진 모드로 청크 단위 탐색을 수행하여 메모리 초과(MemoryError)를 원천적으로 방지함.
    """
    with open(file_path, 'rb') as file_obj:
        segment = None
        offset = 0
        file_obj.seek(0, 2)  # os.SEEK_END 대신 파이썬 내장 상수 2 사용
        file_size = remaining_size = file_obj.tell()

        while remaining_size > 0:
            offset = min(file_size, offset + chunk_size)
            file_obj.seek(file_size - offset)
            buffer = file_obj.read(min(remaining_size, chunk_size))

            if remaining_size == file_size and buffer and buffer[-1] == ord('\n'):
                buffer = buffer[:-1]

            remaining_size -= chunk_size
            lines = buffer.split(b'\n')

            if segment is not None:
                lines[-1] += segment

            segment = lines[0] 
            lines = lines[1:]

            for line in reversed(lines):
                yield line.decode('utf-8')

        if segment is not None:
            yield segment.decode('utf-8')

def main():
    print('Hello Mars')

    log_filename = 'mission_computer_main.log'
    error_filename = 'error_log.txt'
    
    critical_keywords = ('unstable', 'explosion', 'powered down')

    try:
        with open(error_filename, 'w', encoding='utf-8') as error_file:
            print('\n--- 로그 역순 출력 시작 ---')
            
            for line in read_large_file_in_reverse(log_filename):
                print(line)
                
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in critical_keywords):
                    error_file.write(line + '\n')
                    
            print('--- 로그 역순 출력 종료 ---\n')
            
        print('시스템 안내: 에러 로그 분리 저장(error_log.txt)이 완료되었습니다.')
                    
    except FileNotFoundError:
        print('Error: mission_computer_main.log 파일을 찾을 수 없습니다.')
    except Exception as e:
        print(f'Unexpected Error: 예상치 못한 치명적 오류가 발생했습니다. 상세: {e}')

if __name__ == '__main__':
    main()