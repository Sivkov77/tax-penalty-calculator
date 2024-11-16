import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


def get_key_rate():
    url = "https://cbr.ru/hd_base/KeyRate/"  # Адрес страницы с ключевой ставкой ЦБ РФ
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Найдем последнюю запись о ключевой ставке
        rate_table = soup.find('table', class_='data')
        if rate_table:
            rows = rate_table.find_all('tr')
            if len(rows) > 1:
                # Предположим, что первая строка таблицы содержит заголовок, а вторая строка - последние данные
                last_row = rows[1]
                rate_cell = last_row.find_all('td')[1]  # Вторая ячейка содержит значение ключевой ставки
                rate = rate_cell.text.strip()
                return float(rate.replace(',', '.'))
        raise Exception("Не удалось найти ключевую ставку на странице")
    else:
        raise Exception("Не удалось получить данные с сайта Центрального банка РФ")


def calculate_penalties(amount, due_date, payment_date, key_rate):
    key_rate = key_rate / 100  # Преобразуем процентную ставку в дробное число

    # Преобразуем строки дат в объекты datetime
    due_date = datetime.strptime(due_date, "%Y-%m-%d")
    payment_date = datetime.strptime(payment_date, "%Y-%m-%d")

    overdue_days = (payment_date - due_date).days
    if overdue_days <= 0:
        return 0, overdue_days, key_rate  # Нет просрочки, нет пеней

    penalty = 0

    # Рассчитываем пени по тройной формуле
    if overdue_days <= 30:
        penalty += amount * overdue_days * (1 / 300) * key_rate
    elif 31 <= overdue_days <= 90:
        penalty += amount * 30 * (1 / 300) * key_rate
        penalty += amount * (overdue_days - 30) * (1 / 150) * key_rate
    else:
        penalty += amount * 30 * (1 / 300) * key_rate
        penalty += amount * 60 * (1 / 150) * key_rate
        penalty += amount * (overdue_days - 90) * (1 / 300) * key_rate

    return round(penalty, 2), overdue_days, key_rate


# Пример использования
if __name__ == "__main__":
    try:
        amount = float(input("Введите сумму налога в рублях: "))
        due_date = input("Введите срок уплаты налога (в формате ГГГГ-ММ-ДД): ")
        payment_date = input("Введите дату фактической уплаты налога (в формате ГГГГ-ММ-ДД): ")

        use_cbr_rate = input(
            "Вы хотите использовать ключевую ставку с сайта Центрального банка РФ? (да/нет): ").strip().lower()
        if use_cbr_rate == 'да':
            key_rate = get_key_rate()
        else:
            key_rate = float(input("Введите ключевую ставку в процентах: "))

        penalty, overdue_days, key_rate = calculate_penalties(amount, due_date, payment_date, key_rate)

        # Вывод всех исходных параметров и результата в визуально привлекательном формате
        print("\n--- Расчет пеней ---\n")
        print(f"Ключевая ставка: {key_rate * 100:.2f}% действует с 16 сентября 2024 года\n")
        print(f"Чиновники решили сделать особенный расчет пеней в 2025 году – по тройной формуле.\n")
        print(f"Пени с 1-го по 30-й день просрочки платежа считаются исходя из 1/300 ключевой ставки,\n"
              f"с 31-го по 90-й день — из 1/150, и с 91-го дня вновь по 1/300.\n")
        print(f"Формула:\n"
              f"Пени = отрицательное сальдо ЕНС × 30 дней × 1/300 ключевой ставки\n"
              f"      + отрицательное сальдо ЕНС × 60 дней × 1/150 ключевой ставки\n"
              f"      + отрицательное сальдо ЕНС × количество дней с 91-го дня × 1/300 ключевой ставки\n")
        print(f"Пример расчета:\n")
        print(f"Сумма налога: {amount} руб.\n"
              f"Срок уплаты налога: {due_date}\n"
              f"Дата фактической уплаты налога: {payment_date}\n"
              f"Количество дней просрочки: {overdue_days}\n"
              f"Ключевая ставка ЦБ РФ: {key_rate * 100:.2f}%\n")
        print(f"Тогда за период просрочки компания должна будет заплатить пени в размере: {penalty} руб.\n")
        print(
            f"До конца 2024 года действует льготная ставка по пеням — их начисляют исходя из 1/300 ключевой ставки независимо от срока просрочки налогового платежа.\n")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
