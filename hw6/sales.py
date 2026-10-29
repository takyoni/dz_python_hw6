"""Обработка продаж по строкам."""

import heapq
from pathlib import Path


def read_sales(path, errors=None):
    with open(path, encoding='utf-8') as file:
        header_found = False
        for number, line in enumerate(file, 1):
            text = line.rstrip('\r\n')
            if not text.strip() or text.lstrip().startswith('#'):
                continue
            if not header_found:
                header_found = True
                continue
            try:
                day, category, product, qty, price = text.split(',')
                qty = int(qty)
                price = float(price)
            except ValueError:
                if errors is not None:
                    errors.append((number, text))
                continue
            yield dict(date=day, category=category, product=product,
                       qty=qty, price=price)


def daily_revenue(rows):
    day = None
    total = 0
    for row in rows:
        if day is not None and row['date'] != day:
            yield day, round(total, 2)
            total = 0
        day = row['date']
        total += row['qty'] * row['price']
    if day is not None:
        yield day, round(total, 2)


# Если даты перемешаны, один день разобьётся на несколько сумм.
# Тогда нужен словарь сумм по датам и сортировка дат в конце.
# Это займёт O(D) памяти вместо O(1), где D это число разных дат.


def running_revenue(daily):
    total = 0
    for day, revenue in daily:
        total += revenue
        yield day, round(total, 2)


def revenue_by_category(rows):
    totals = {}
    for row in rows:
        category = row['category']
        totals[category] = totals.get(category, 0) + row['qty'] * row['price']
    return {category: round(total, 2) for category, total in totals.items()}


def best_days(daily, n=3):
    # Храним только n лучших дней.
    return heapq.nlargest(n, daily, key=lambda item: item[1])


SAMPLE = '''# выгрузка продаж
date,category,product,qty,price

2026-10-01,books,Dune,2,500
2026-10-01,food,tea,3,120.5
2026-10-02,books,Solaris,1,450
# комментарий посреди файла
2026-10-02,food,coffee,много,300
2026-10-02,toys,ball,4,250
2026-10-03,food,tea,10,120.5
2026-10-03,books,Dune
'''


if __name__ == '__main__':
    path = Path(__file__).with_name('sales_sample.csv')
    path.write_text(SAMPLE, encoding='utf-8')
    errors = []
    print('Выручка по дням:', list(daily_revenue(read_sales(path, errors))))
    print('Битые строки:', errors)
    print('Нарастающий итог:', list(running_revenue(daily_revenue(read_sales(path)))))
    print('По категориям:', revenue_by_category(read_sales(path)))
    print('Лучшие дни:', best_days(daily_revenue(read_sales(path)), 2))
