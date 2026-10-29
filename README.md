# ДЗ к лекции 6

Решения в `hw6`. Дополнительные библиотеки не нужны.

- `sales.py`: обработка продаж по строкам.
- `date_range.py`: диапазон дат, включая срезы с положительным шагом.
- `report.py`: исходный код из задания.
- `report_fixed.py`: исправленный отчёт.
- `review.md`: найденные ошибки.

Запуск из этой папки:

```bash
python3 hw6/sales.py
python3 hw6/date_range.py
python3 hw6/report_fixed.py
```

При запуске sales.py и report_fixed.py рядом создаются файлы с примерами
из задания: sales_sample.csv и orders.txt. При повторном запуске они перезаписываются.
Функции read_sales(path) и read_orders(path) могут читать любой указанный файл.

Проверки:

```bash
python3 hw6/test_report.py report_fixed
python3 hw6/test_report.py report
python3 hw6/memory_check.py
```

Все 9 тестов проходят на `report_fixed.py` и находят ошибки в `report.py`.
Предупреждение про Кейт ожидаемо: у неё нет лимита.

`memory_check.py` создаёт временный файл на 1 095 000 строк и удаляет его
после замера. Пик памяти на Python 3.11.2 составил 29 298 байт, меньше 1 МБ.
