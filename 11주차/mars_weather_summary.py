import csv
import pymysql


class MySQLHelper:
    # port의 기본값을 3306으로 설정합니다.
    def __init__(self, host, user, password, db, port=3306, charset='utf8'):
        self.host = host
        self.user = user
        self.password = password
        self.db = db
        self.port = port
        self.charset = charset
        self.connection = None

    def connect(self):
        self.connection = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.db,  # <--- 'database'로 변경!
            port=self.port,
            charset=self.charset
        )

    def disconnect(self):
        if self.connection:
            self.connection.close()

    def execute_insert(self, query, args=None):
        with self.connection.cursor() as cursor:
            cursor.execute(query, args)
        self.connection.commit()


def read_and_insert_weather_data(file_path, db_helper):
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)

        # 첫 번째 줄이 헤더(weather_id,mars_date,temp,stom)이므로 건너뜁니다.
        next(reader)

        query = 'INSERT INTO mars_weather (mars_date, temp, storm) VALUES (%s, %s, %s)'

        for row in reader:
            # row[0]은 weather_id 이므로 무시합니다. (DB에서 자동 증가됨)
            mars_date = row[1]

            # 소수점이 있는 글자(예: '21.4')를 실수(float)로 먼저 바꾼 뒤 정수(int)로 변환합니다.
            temp = int(float(row[2]))

            storm = int(row[3])

            db_helper.execute_insert(query, (mars_date, temp, storm))


def main():
    host_name = 'localhost'
    user_name = 'root'
    user_password = ''
    db_name = 'mars_mission'

    # 포트를 3306으로 명시하여 클래스를 생성합니다.
    db_helper = MySQLHelper(
        host=host_name,
        user=user_name,
        password=user_password,
        db=db_name,
        port=3306
    )

    try:
        db_helper.connect()
        print('MySQL 데이터베이스 연결 성공')

        file_path = 'mars_weathers_data.csv'
        read_and_insert_weather_data(file_path, db_helper)

        print('화성 날씨 데이터가 성공적으로 입력되었습니다.')

    except Exception as e:
        print('오류가 발생했습니다: ' + str(e))

    finally:
        db_helper.disconnect()
        print('MySQL 데이터베이스 연결 종료')


if __name__ == '__main__':
    main()