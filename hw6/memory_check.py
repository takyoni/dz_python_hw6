import random
from datetime import date, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
import tracemalloc

from sales import best_days, daily_revenue, read_sales

# Python 3.11.2, 1 095 000 строк: пик памяти 29 298 байт, меньше 1 МБ.


def make_big(path='sales_big.csv', days=365, rows_per_day=3000):
    random.seed(0)
    cats = {'books': ['Dune', 'Solaris'], 'food': ['tea', 'coffee'], 'toys': ['ball', 'lego']}
    start = date(2025, 1, 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write('date,category,product,qty,price\n')
        for d in range(days):
            day = (start + timedelta(days=d)).isoformat()
            for _ in range(rows_per_day):
                c = random.choice(list(cats))
                qty = random.randint(1, 5) if random.random() > 0.001 else 'oops'
                f.write(f'{day},{c},{random.choice(cats[c])},{qty},{random.randint(50, 900)}\n')


if __name__ == '__main__':
    with TemporaryDirectory() as folder:
        path = Path(folder) / 'sales_big.csv'
        make_big(path)
        print('Строк продаж:', 365 * 3000)
        print('Размер файла:', path.stat().st_size, 'байт')
        # Замеряем обработку. Ошибки в список не собираем.
        tracemalloc.start()
        try:
            result = best_days(daily_revenue(read_sales(path)))
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        print('Лучшие дни:', result)
        print('Пик памяти:', peak, 'байт')
        assert peak < 1_000_000, 'Пик памяти больше 1 МБ'
