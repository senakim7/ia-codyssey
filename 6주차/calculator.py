import sys  # 파이썬 시스템 자체를 제어하기 위한 기본 내장 모듈입니다.
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit
from PyQt5.QtCore import Qt  # UI 정렬 등을 위한 상수 모듈입니다.


class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.current_input = ''
        self.previous_input = ''
        self.operator = None

        # [NEW] 버튼들을 딕셔너리(사전) 형태로 저장해둘 공간을 만듭니다.
        # 나중에 연산자 버튼의 색깔을 마음대로 바꾸려면, 그 버튼이 어디 있는지 이름표를 달아 기억해둬야 하기 때문입니다.
        self.btn_objects = {}

        self.init_ui()  # 화면을 그리는 함수 실행

    # 화면의 모양을 만들고 버튼을 배치하는 함수입니다.
    def init_ui(self):
        self.setWindowTitle('Calculator')
        self.setFixedSize(320, 480)

        vbox = QVBoxLayout()  # 수직(위아래)으로 쌓는 레이아웃

        # 화면 맨 위 숫자 표시창 설정
        self.display = QLineEdit('0')
        self.display.setAlignment(Qt.AlignRight)
        self.display.setReadOnly(True)
        self.display.setStyleSheet('font-size: 45px; border: none; padding: 10px;')
        vbox.addWidget(self.display)

        grid = QGridLayout()  # 바둑판(격자) 모양의 레이아웃
        grid.setSpacing(5)

        # 버튼의 글자와 위치(행, 열, 차지할 행 갯수, 차지할 열 갯수) 설계도
        buttons = [
            ('AC', 0, 0, 1, 1), ('+/-', 0, 1, 1, 1), ('%', 0, 2, 1, 1), ('÷', 0, 3, 1, 1),
            ('7', 1, 0, 1, 1), ('8', 1, 1, 1, 1), ('9', 1, 2, 1, 1), ('×', 1, 3, 1, 1),
            ('4', 2, 0, 1, 1), ('5', 2, 1, 1, 1), ('6', 2, 2, 1, 1), ('-', 2, 3, 1, 1),
            ('1', 3, 0, 1, 1), ('2', 3, 1, 1, 1), ('3', 3, 2, 1, 1), ('+', 3, 3, 1, 1),
            ('0', 4, 0, 1, 2), ('.', 4, 2, 1, 1), ('=', 4, 3, 1, 1)
        ]

        # 설계도를 바탕으로 실제 버튼을 찍어냅니다.
        for text, row, col, rowspan, colspan in buttons:
            button = QPushButton(text)

            # 숫자 '0'처럼 2칸을 차지하는 버튼을 위해 너비를 계산합니다.
            button_width = 70 * colspan + (5 if colspan > 1 else 0)
            button.setFixedSize(button_width, 70)
            button.setStyleSheet('font-size: 24px;')
            button.clicked.connect(self.on_click)  # 버튼이 눌리면 on_click 함수로 연결
            grid.addWidget(button, row, col, rowspan, colspan)  # 바둑판에 버튼 배치

            # [NEW] 방금 만든 버튼을 'text(버튼 글자)'라는 이름표를 달아서 btn_objects 딕셔너리에 저장합니다.
            # 예: self.btn_objects['+'] 안에는 '+' 버튼 객체가 통째로 들어갑니다.
            self.btn_objects[text] = button

        vbox.addLayout(grid)
        self.setLayout(vbox)
        self.show()

    # [NEW] 켜져 있는 주황색 불(강조 표시)을 모두 끄고 원래의 하얀색 버튼으로 되돌리는 함수입니다.
    def reset_operator_styles(self):
        # 사칙연산 기호 4개를 하나씩 꺼내면서 반복합니다.
        for op in ['+', '-', '×', '÷']:
            # 위에서 저장해둔 딕셔너리에서 해당 연산자 버튼을 찾아, 스타일을 기본 글자 크기(24px)로 덮어씌웁니다.
            # (주황색 배경색과 흰색 글씨 스타일을 지워버리는 효과)
            self.btn_objects[op].setStyleSheet('font-size: 24px;')

    # 버튼이 눌렸을 때 실행되는 메인 컨트롤 타워 함수입니다.
    def on_click(self):
        sender = self.sender()  # 누가 날 클릭했는지 확인
        text = sender.text()  # 그 버튼에 적힌 글씨 확인

        # 1. 숫자나 소수점을 눌렀을 때
        if text in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']:
            if text == '.' and '.' in self.current_input:
                return  # 소수점 중복 방지
            self.current_input += text  # 숫자를 이어 붙임
            self.update_display(self.current_input)  # 화면 갱신

            # [NEW] 숫자를 누르기 시작했다는 건 연산자 입력이 끝났다는 뜻이므로, 켜져있던 연산자 불을 끕니다.
            self.reset_operator_styles()

            # 2. 초기화(AC)를 눌렀을 때
        elif text == 'AC':
            self.current_input = ''
            self.previous_input = ''
            self.operator = None
            self.update_display('0')
            # [NEW] 모든 걸 초기화하므로 켜져있던 연산자 불도 끕니다.
            self.reset_operator_styles()

            # 3. 사칙연산 기호를 눌렀을 때
        elif text in ['+', '-', '×', '÷']:
            # [NEW] 다른 연산자에 불이 켜져 있을 수 있으니 일단 모든 연산자 불을 다 끕니다.
            self.reset_operator_styles()

            # [NEW] 방금 내가 누른 바로 그 연산자 버튼을 찾아, 배경을 주황색(#ff9f0a), 글씨를 흰색(white)으로 바꿉니다.
            self.btn_objects[text].setStyleSheet('font-size: 24px; background-color: #ff9f0a; color: white;')

            if self.current_input:  # 방금까지 입력하던 숫자가 있다면
                self.previous_input = self.current_input  # 이전 숫자로 저장해둠
                self.current_input = ''  # 현재 입력창은 비움
            self.operator = text  # 방금 누른 연산자를 기억함

        # 4. 계산(=) 버튼을 눌렀을 때
        elif text == '=':
            # 이전 숫자, 현재 숫자, 연산기호가 다 있어야만 계산
            if self.previous_input and self.current_input and self.operator:
                self.calculate()
            # [NEW] 계산이 끝났으니 켜져있던 연산자 불을 끕니다.
            self.reset_operator_styles()

            # 5. 양수/음수 전환 버튼
        elif text == '+/-':
            if self.current_input:
                if self.current_input.startswith('-'):
                    self.current_input = self.current_input[1:]  # - 떼기
                else:
                    self.current_input = '-' + self.current_input  # - 붙이기
                self.update_display(self.current_input)

        # 6. 퍼센트(%) 버튼
        elif text == '%':
            if self.current_input:
                try:
                    val = float(self.current_input) / 100  # 100으로 나눔
                    self.current_input = str(val)
                    self.update_display(self.current_input)
                except ValueError:
                    pass

    # 실제 계산을 수행하는 함수
    def calculate(self):
        try:
            num1 = float(self.previous_input)
            num2 = float(self.current_input)
            result = 0

            if self.operator == '+':
                result = num1 + num2
            elif self.operator == '-':
                result = num1 - num2
            elif self.operator == '×':
                result = num1 * num2
            elif self.operator == '÷':
                if num2 == 0:
                    self.update_display('Error')  # 0으로 나누면 에러
                    self.current_input = ''
                    self.previous_input = ''
                    self.operator = None
                    return
                result = num1 / num2

            if result.is_integer():
                result = int(result)  # 결과가 5.0이면 5로 깔끔하게 정수화

            self.current_input = str(result)
            self.update_display(self.current_input)  # 계산 결과 출력
            self.previous_input = ''
            self.operator = None
        except ValueError:
            self.update_display('Error')

    # 천 단위 콤마를 찍어주는 화면 출력 담당 함수
    def update_display(self, text):
        try:
            if text != 'Error' and text != '' and text != '-':
                if '.' in text:  # 소수점이 있는 경우
                    parts = text.split('.')
                    formatted_int = f'{int(parts[0]):,}'  # 정수 부분에만 콤마 찍기
                    self.display.setText(f'{formatted_int}.{parts[1]}')
                else:  # 소수점이 없는 경우
                    self.display.setText(f'{int(text):,}')  # 바로 콤마 찍기
            else:
                self.display.setText(text if text else '0')
        except ValueError:
            self.display.setText(text)


# 프로그램 실행을 위한 필수 코드
if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc = Calculator()
    sys.exit(app.exec_())