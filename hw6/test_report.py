"""Проверки обеих версий отчёта."""

import importlib
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import tracemalloc
import unittest
from unittest.mock import patch
import warnings

module = importlib.import_module(sys.argv[1] if len(sys.argv) > 1 else 'report_fixed')


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'orders.txt'
        self.path.write_text('anna,100\nbob,50\n\nanna,700\nkate,300\nbob,30\n',
                             encoding='utf-8')

    def test_read_orders_file_stays_open(self):
        self.assertEqual(list(module.read_orders(self.path)), [
            ['anna', '100'], ['bob', '50'], ['anna', '700'],
            ['kate', '300'], ['bob', '30'],
        ])

    def test_totals_for_non_adjacent_users(self):
        orders = iter([('anna', '100'), ('bob', '50'), ('anna', '700')])
        self.assertEqual(module.totals_by_user(orders), {'anna': 800, 'bob': 50})

    def test_no_large_orders(self):
        self.assertFalse(module.has_large_orders(iter([('anna', '100')])))
        self.assertFalse(module.has_large_orders(iter([])))
        self.assertFalse(module.has_large_orders(iter([('anna', '1000')])))
        self.assertTrue(module.has_large_orders(iter([('anna', '1001')])))

    def test_build_report_does_not_reuse_spent_iterator(self):
        # Подменяем чтение, чтобы закрытый файл не мешал этой проверке.
        orders = iter([('anna', '1200'), ('bob', '50')])
        with patch.object(module, 'read_orders', return_value=orders):
            report = module.build_report(self.path, [], [])
        self.assertEqual(report['orders'], 2)
        self.assertEqual(report['totals'], {'anna': 1200, 'bob': 50})
        self.assertTrue(report['has_large'])

    def test_missing_vip_limit_is_not_silent(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            result = module.vip_over_limit(
                {'anna': 800, 'bob': 80, 'kate': 300},
                ['anna', 'bob', 'kate'], [500, 10])
        self.assertEqual(result, ['anna', 'bob'])
        self.assertEqual(len(caught), 1)
        self.assertIn('kate', str(caught[0].message))

    def test_last_orders_uses_little_memory(self):
        with self.path.open('w', encoding='utf-8') as file:
            for _ in range(100_000):
                file.write('anna,100\n')
            file.write('bob,50\nkate,300\n')
        # Создание файла не входит в замер.
        tracemalloc.start()
        try:
            result = module.last_orders(self.path, 2)
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        self.assertEqual(result, ['bob,50', 'kate,300'])
        self.assertLess(peak, 1_000_000)

    def test_last_orders_zero(self):
        self.assertEqual(module.last_orders(self.path, 0), [])

    def test_last_orders_negative(self):
        with self.assertRaises(ValueError):
            module.last_orders(self.path, -1)

    def test_sample_report(self):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            report = module.build_report(self.path, ['anna', 'bob', 'kate'], [500, 10])
        self.assertEqual(report, {
            'orders': 5,
            'totals': {'anna': 800.0, 'bob': 80.0, 'kate': 300.0},
            'has_large': False,
            'vip_over_limit': ['anna', 'bob'],
            'last': ['anna,700', 'kate,300', 'bob,30'],
        })


if __name__ == '__main__':
    unittest.main(argv=[sys.argv[0]], verbosity=2)
