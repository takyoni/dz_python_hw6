"""Исправленный отчёт по заказам."""

from collections import deque
from itertools import zip_longest
from pathlib import Path
import warnings


def read_orders(path):
    """Читаем заказы по строке."""
    with open(path, encoding='utf-8') as file:
        for line in file:
            if line.strip():
                yield line.strip().split(',')


def totals_by_user(orders):
    totals = {}
    for user, amount in orders:
        totals[user] = totals.get(user, 0) + float(amount)
    return totals


def has_large_orders(orders, threshold=1000):
    return any(float(amount) > threshold for _, amount in orders)


def vip_over_limit(totals, vip_users, vip_limits):
    result = []
    missing = object()
    for user, limit in zip_longest(vip_users, vip_limits, fillvalue=missing):
        if user is missing:
            raise ValueError('Есть лимит без пользователя')
        if limit is missing:
            warnings.warn(f'Для {user} не указан лимит: пропускаем',
                          UserWarning, stacklevel=2)
            continue
        if totals.get(user, 0) > limit:
            result.append(user)
    return result


def last_orders(path, n=5):
    if n < 0:
        raise ValueError('Количество строк не может быть отрицательным')
    if n == 0:
        return []
    with open(path, encoding='utf-8') as file:
        return [line.strip() for line in deque(file, maxlen=n)]


def build_report(path, vip_users, vip_limits):
    count = 0
    totals = {}
    has_large = False
    # Считаем всё за один проход.
    for user, amount in read_orders(path):
        amount = float(amount)
        count += 1
        totals[user] = totals.get(user, 0) + amount
        if amount > 1000:
            has_large = True
    return {
        'orders': count,
        'totals': totals,
        'has_large': has_large,
        'vip_over_limit': vip_over_limit(totals, vip_users, vip_limits),
        'last': last_orders(path, 3),
    }


if __name__ == '__main__':
    path = Path(__file__).with_name('orders.txt')
    path.write_text('anna,100\nbob,50\n\nanna,700\nkate,300\nbob,30\n',
                    encoding='utf-8')
    print(build_report(path, ['anna', 'bob', 'kate'], [500, 10]))
