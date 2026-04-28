import sys  # 컴퓨터에게 "프로그램을 켜고 끌 수 있는 도구 상자 좀 가져와!" 라고 말하는 거예요.
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit
from PyQt5.QtCore import Qt  # 글자를 오른쪽 끝에 예쁘게 맞춰주는 자(ruler) 같은 도구예요.

class Calculator(QWidget):  # "자, 이제부터 'Calculator'라는 계산기 로봇의 설계도를 그릴 거야!"
    def __init__(self):  # 로봇의 전원을 처음 켤 때, 머릿속을 텅 비워주는 초기화 작업이에요.
        super().__init__()
        
        # 로봇의 '기억 장치(메모리)'
        self.current_input = ''  # 방금 내가 누른 숫자들
        self.previous_input = ''  # 더하기나 빼기를 누르기 전에 입력했던 옛날 숫자
        self.operator = None  # 어떤 기호를 눌렀는지 기억하는 곳
        
        self.btn_objects = {}  # 버튼들의 이름표를 모아두는 상자

        self.init_ui()  # "자, 이제 로봇의 얼굴과 버튼들을 조립해!"

    def init_ui(self):  # 화면을 예쁘게 꾸미는 마법
        self.setWindowTitle('Calculator')
        self.setFixedSize(320, 480)

        vbox = QVBoxLayout()  # 상자들을 위에서 아래로 차곡차곡 쌓아주는 세로형 정리함

        self.display = QLineEdit('0')  # 숫자가 나오는 네모난 화면
        self.display.setAlignment(Qt.AlignRight)  # 숫자를 화면 오른쪽 끝으로 붙임
        self.display.setReadOnly(True)  # 키보드 입력 금지, 버튼만 허용
        self.display.setStyleSheet('font-size: 45px; border: none; padding: 10px;')
        vbox.addWidget(self.display)

        grid = QGridLayout()  # 버튼들을 바둑판 모양으로 놓을 바둑판 정리함
        grid.setSpacing(5)

        # 버튼 위치 보물지도
        buttons = [
            ('AC', 0, 0, 1, 1), ('+/-', 0, 1, 1, 1), ('%', 0, 2, 1, 1), ('÷', 0, 3, 1, 1),
            ('7', 1, 0, 1, 1), ('8', 1, 1, 1, 1), ('9', 1, 2, 1, 1), ('×', 1, 3, 1, 1),
            ('4', 2, 0, 1, 1), ('5', 2, 1, 1, 1), ('6', 2, 2, 1, 1), ('-', 2, 3, 1, 1),
            ('1', 3, 0, 1, 1), ('2', 3, 1, 1, 1), ('3', 3, 2, 1, 1), ('+', 3, 3, 1, 1),
            ('0', 4, 0, 1, 2), ('.', 4, 2, 1, 1), ('=', 4, 3, 1, 1)
        ]

        for text, row, col, rowspan, colspan in buttons:
            button = QPushButton(text)
            button_width = 70 * colspan + (5 if colspan > 1 else 0)
            button.setFixedSize(button_width, 70)
            button.setStyleSheet('font-size: 24px;')
            button.clicked.connect(self.on_click)  # 버튼 눌리면 on_click으로 연결!
            grid.addWidget(button, row, col, rowspan, colspan)
            self.btn_objects[text] = button

        vbox.addLayout(grid)
        self.setLayout(vbox)
        self.show()

    def reset_operator_styles(self):  # 연산자 버튼에 켜진 불(색깔)을 모두 끄는 마법
        for op in ['+', '-', '×', '÷']:
            self.btn_objects[op].setStyleSheet('font-size: 24px;')

    def on_click(self):  # 버튼이 눌렸을 때의 컨트롤 타워
        sender = self.sender()
        text = sender.text()

        # 1. 숫자나 소수점(.)을 눌렀을 때
        if text in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']:
            if text == '.' and '.' in self.current_input:
                return  # 점(.) 중복 방지
            self.current_input += text
            self.update_display(self.current_input)
            self.reset_operator_styles()
            
        # 2. AC(전부 지우기) 버튼
        elif text == 'AC':
            self.reset()
            
        # 3. 더하기, 빼기 같은 기호
        elif text in ['+', '-', '×', '÷']:
            self.reset_operator_styles()
            self.btn_objects[text].setStyleSheet('font-size: 24px; background-color: #ff9f0a; color: white;')
            if self.current_input:
                self.previous_input = self.current_input
                self.current_input = ''
            self.operator = text
            
        # 4. 등호(=) 정답 구하기
        elif text == '=':
            self.equal()
            
        # 5. 플러스/마이너스(+/-) 부호 바꾸기
        elif text == '+/-':
            self.negative_positive()
            
        # 6. 퍼센트(%)
        elif text == '%':
            self.percent()

    # --- 여기서부터 진짜 수학 시간! (계산기 두뇌) ---
    def add(self, n1, n2): return n1 + n2
    def subtract(self, n1, n2): return n1 - n2
    def multiply(self, n1, n2): return n1 * n2
    def divide(self, n1, n2):
        if n2 == 0:
            raise ZeroDivisionError('Division by zero')  # 0으로 나누기 방어!
        return n1 / n2

    def reset(self):  # 싹 다 잊어버려라 얍!
        self.current_input = ''
        self.previous_input = ''
        self.operator = None
        self.update_display('0')
        self.reset_operator_styles()

    def negative_positive(self):  # 양수/음수 마법
        if self.current_input:
            if self.current_input.startswith('-'):
                self.current_input = self.current_input[1:]
            else:
                self.current_input = '-' + self.current_input
            self.update_display(self.current_input)

    def percent(self):  # 퍼센트 마법
        if self.current_input:
            try:
                val = float(self.current_input) / 100
                self.current_input = str(val)
                self.update_display(self.current_input)
            except ValueError:
                pass

    def equal(self):  # '=' 눌렀을 때 실행되는 곳
        if self.previous_input and self.current_input and self.operator:
            try:
                num1 = float(self.previous_input)
                num2 = float(self.current_input)
                result = 0

                if self.operator == '+': result = self.add(num1, num2)
                elif self.operator == '-': result = self.subtract(num1, num2)
                elif self.operator == '×': result = self.multiply(num1, num2)
                elif self.operator == '÷': result = self.divide(num1, num2)

                # 보너스 과제: 소수점 6자리까지만 남기고 반올림!
                result = round(result, 6)

                if result.is_integer():
                    result = int(result)  # 5.0 이면 5로 꼬리 떼기

                self.current_input = str(result)
                self.update_display(self.current_input)
                self.previous_input = ''
                self.operator = None
                self.reset_operator_styles()
            
            except ZeroDivisionError:
                self.update_display('Error: Div by 0')
                self.reset_state_on_error()
            except OverflowError:
                self.update_display('Error: Overflow')
                self.reset_state_on_error()

    def reset_state_on_error(self):
        self.current_input = ''
        self.previous_input = ''
        self.operator = None

    def update_display(self, text):
        # 보너스 과제: 글자가 많아지면 폰트 크기 줄이기 마법!
        length = len(text)
        if length > 12: font_size = 25
        elif length > 9: font_size = 35
        else: font_size = 45
            
        self.display.setStyleSheet(f'font-size: {font_size}px; border: none; padding: 10px;')

        try:
            if text and not text.startswith('Error') and text != '-':
                if '.' in text:
                    parts = text.split('.')
                    formatted_int = f'{int(parts[0]):,}'  # 1,000 단위 콤마 찍기
                    self.display.setText(f'{formatted_int}.{parts[1]}')
                else:
                    self.display.setText(f'{int(text):,}')
            else:
                self.display.setText(text if text else '0')
        except ValueError:
            self.display.setText(text)

# 진짜 실행 버튼
if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc = Calculator()
    sys.exit(app.exec_())
