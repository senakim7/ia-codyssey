import os


def caesar_cipher_decode(target_text, use_bonus_dict=False):
    """
    카이사르 암호가 적용된 문자열을 해독하는 함수입니다.
    알파벳(26자) 자릿수만큼 밀어서(Shift) 모든 경우의 수를 출력합니다.

    파라미터:
        target_text (str): 해독할 원본 암호문
        use_bonus_dict (bool): 보너스 과제(사전 기반 자동 탐색) 활성화 여부
    """
    # 보너스 과제용 텍스트 사전 (화성 기지, 생존, 문 개방과 관련된 유력 키워드)
    # 실제 암호문에 포함되어 있을 만한 영단어들을 소문자로 등록합니다.
    keyword_dictionary = [
        'emergency', 'storage', 'coffee', 'oxygen', 'escape',
        'open', 'door', 'system', 'survive', 'password', 'mars'
    ]

    print('=' * 60)
    print('  로마시대 카이사르 암호(Caesar Cipher) 해독 분석기')
    print('=' * 60)
    print(f'  입력된 원본 암호문: \'{target_text}\'\n')

    # 가능한 시프트 키(1~25) 목록
    decoded_candidates = {}
    auto_found_key = None

    # 1. 1부터 25까지 자릿수를 밀어가며 해독 시도
    for shift in range(1, 26):
        decoded_chars = []
        for char in target_text:
            # 소문자 처리
            if 'a' <= char <= 'z':
                shifted_char = chr((ord(char) - ord('a') - shift) % 26 + ord('a'))
                decoded_chars.append(shifted_char)
            # 대문자 처리
            elif 'A' <= char <= 'Z':
                shifted_char = chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
                decoded_chars.append(shifted_char)
            # 숫자 및 특수문자, 공백은 그대로 유지
            else:
                decoded_chars.append(char)

        decoded_text = ''.join(decoded_chars)
        decoded_candidates[shift] = decoded_text

        # 반복할 때마다 결과를 눈으로 확인할 수 있도록 출력
        print(f'  [Shift {shift:02d}] 결과: \'{decoded_text}\'')

        # [보너스 과제 로직] 사전에 있는 단어가 해독된 문자열에 포함되어 있는지 확인
        if use_bonus_dict:
            # 대소문자 구분 없이 검색하기 위해 소문자로 변환
            lower_decoded = decoded_text.lower()
            for word in keyword_dictionary:
                if word in lower_decoded:
                    print('\n' + '*' * 60)
                    print(f'  ★ [보너스 과제 성공] 사전 키워드 \'{word}\' 발견! ★')
                    print('  의미 있는 문장으로 판단되어 자동 탐색을 종료합니다.')
                    print('*' * 60)
                    auto_found_key = shift
                    break

            # 단어를 찾았다면 외부 바깥 루프(Shift 반복)도 멈춤
            if auto_found_key is not None:
                break

    print('=' * 60)

    # 2. 결과 선택 및 파일 저장 로직
    selected_result = None
    selected_shift = None

    # 보너스 기능으로 키를 자동으로 찾았을 경우
    if auto_found_key is not None:
        selected_shift = auto_found_key
        selected_result = decoded_candidates[auto_found_key]
    # 눈으로 직접 식별하여 번호를 입력해야 하는 기본 과제 모드
    else:
        while True:
            try:
                user_input = input('\n눈으로 식별하여 올바른 의미를 갖는 해독 번호(Shift 1~25)를 입력하세요: ')
                selected_shift = int(user_input)
                if 1 <= selected_shift <= 25:
                    selected_result = decoded_candidates[selected_shift]
                    break
                else:
                    print('경고: 1에서 25 사이의 숫자만 입력해야 합니다.')
            except ValueError:
                print('경고: 유효한 숫자를 입력해 주세요.')

    # 3. 최종 결과를 result.txt로 저장 (예외 처리 철저)
    if selected_result:
        print(f'\n최종 선택된 해독문: \'{selected_result}\' (Shift: {selected_shift})')
        try:
            with open('result.txt', 'w', encoding='utf-8') as f:
                f.write(selected_result)
            print('성공적으로 \'result.txt\' 파일에 최종 암호가 저장되었습니다. 문을 열어보세요!')
        except IOError as e:
            print(f'파일 저장 중 오류가 발생했습니다: {e}')


def main():
    """프로그램 메인 실행부 (파일 읽기 및 예외 처리)"""
    password_filepath = 'password.txt'

    # 파일 읽기 예외 처리
    try:
        with open(password_filepath, 'r', encoding='utf-8') as f:
            # 공백이나 줄바꿈 제거
            target_text = f.read().strip()

        if not target_text:
            print(f'오류: \'{password_filepath}\' 파일이 비어 있습니다.')
            return

    except FileNotFoundError:
        print(f'오류: \'{password_filepath}\' 파일을 찾을 수 없습니다.')
        print('이전 단계에서 생성된 password.txt 파일이 같은 폴더에 있는지 확인하세요.')
        return
    except IOError as e:
        print(f'파일을 읽는 중 입출력 오류가 발생했습니다: {e}')
        return

    # 함수 호출
    # 보너스 과제 기능을 켜려면 파라미터 use_bonus_dict=True 로 설정하세요.
    # 기본 과제(수동 입력) 모드로 검사하려면 use_bonus_dict=False 로 설정하면 됩니다.
    caesar_cipher_decode(target_text=target_text, use_bonus_dict=True)


if __name__ == '__main__':
    main()