import re
import json
import chardet
import psycopg2


class Postgres:
    def __init__(self):
        self.cursor = None
        self.connection = None

        db_params = {
            'host': 'localhost',
            'database': 'test_db',
            'user': 'postgres',
            'password': 'password'
        }
        try:
            self.connection = psycopg2.connect(
                host=db_params['host'],
                database=db_params['database'],
                user=db_params['user'],
                password=db_params['password']
            )
            self.cursor = self.connection.cursor()

            # Создание таблицы если не существует
            create_table_query = '''
            CREATE TABLE IF NOT EXISTS combined_data (
                id SERIAL PRIMARY KEY,
                column1 TEXT,
                column2 TEXT
            );
            '''
            self.cursor.execute(create_table_query)
            self.connection.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(f'Ошибка при работе с базой данных: {error}')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()

    def insert_data(self, data: list) -> None:
        for row in data:
            self.cursor.execute('INSERT INTO combined_data (column1, column2) VALUES (%s, %s)', (row[0], row[1]))

    def pivot_table_query(self):
        """Возвращает запрос для разворота таблицы."""
        return self.cursor.execute('''
        SELECT column2, ARRAY_AGG(column1 ORDER BY column1) AS items FROM combined_data 
        GROUP BY column2 ORDER BY column2;
        ''')


def detect_encoding(file_path: str) -> str:
    """Определяет кодировку файла."""
    with open(file_path, 'rb') as file:
        raw_data = file.read(10000)  # Читаем первые 10 000 байт
        result = chardet.detect(raw_data)  # Определяем кодировку
        encoding = result['encoding']
    return encoding


def read_file(file_path: str) -> list:
    """Читает данные из первого файла и возвращает список списков."""
    data = []
    encoding = detect_encoding(file_path)  # Определяем кодировку, предоставленные файлы имеют разную
    with open(file_path, 'r', encoding=encoding) as file:
        file_text = re.sub(',', ';', file.read())
        print(file_text)
        for line in file_text.split('\n'):
            # Удаляем лишние пробелы и переносы строк, разделяем строку по разделителю
            columns = [col.strip().strip('"') for col in line.strip().split(';')]
            data.append(columns)
    return data


def combiner(data1: list, data2: list) -> list:
    """Объединяет два списка и сортирует их по второму столбцу."""
    combined_data = data1 + data2
    # Сортировка по второму столбцу (индекс 1)
    sorted_data = sorted(combined_data, key=lambda x: x[1].lower())
    return sorted_data


def save_to_json(data: list, json_file_path: str) -> None:
    """Сохраняет данные в формате JSON."""
    with open(json_file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def main():
    # Чтение данных из файлов
    file1_data = read_file('Тестовый файл1.txt')
    file2_data = read_file('Тестовый файл2.txt')

    combined_data = combiner(file1_data, file2_data)  # Объединение и сортировка данных
    save_to_json(combined_data, 'combined_data.json')  # Сохранение в формате JSON

    # Сохранение данных в базу данных PostgreSQL
    with Postgres() as db:
        db.insert_data(combined_data)
        print('Запрос для разворота таблицы:', db.pivot_table_query())


if __name__ == '__main__':
    main()
