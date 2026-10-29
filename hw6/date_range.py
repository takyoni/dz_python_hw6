"""Диапазон дат с шагом в днях."""

from datetime import date
from operator import index


class DateRange:
    def __init__(self, start, stop, step=1):
        step = index(step)
        if step <= 0:
            raise ValueError('Шаг должен быть положительным')
        self.start = start
        self.stop = stop
        self.step = step
        # Храним номера дней в range.
        self._days = range(start.toordinal(), stop.toordinal(), step)

    def __iter__(self):
        # У каждого обхода своя позиция. С return self она была бы общей:
        # вложенный цикл мешал бы внешнему, а повторный обход был бы пустым.
        for day in self._days:
            yield date.fromordinal(day)

    def __len__(self):
        return len(self._days)

    def __getitem__(self, item):
        if isinstance(item, slice):
            if item.step is not None and index(item.step) <= 0:
                raise ValueError('Шаг среза должен быть положительным')
            days = self._days[item]
            if not days:
                return DateRange(self.start, self.start, days.step)
            # Ограничиваем stop, чтобы не выйти за date.max.
            stop = min(days.stop, self.stop.toordinal())
            return DateRange(date.fromordinal(days.start),
                             date.fromordinal(stop), days.step)
        return date.fromordinal(self._days[item])

    def __contains__(self, day):
        if type(day) is not date:
            return False
        return day.toordinal() in self._days

    def __reversed__(self):
        for day in reversed(self._days):
            yield date.fromordinal(day)

    def __repr__(self):
        return f'DateRange({self.start!r}, {self.stop!r}, {self.step!r})'

    def __eq__(self, other):
        if not isinstance(other, DateRange):
            return NotImplemented
        # Равны, если выдают одни и те же даты.
        return self._days == other._days


if __name__ == '__main__':
    r = DateRange(date(2026, 10, 1), date(2026, 10, 11), 3)
    print(r)
    print('Даты:', list(r))
    print('Последняя дата:', r[-1])
    print('В обратном порядке:', list(reversed(r)))
    print('Срез [1:3]:', list(r[1:3]))
    print('Срез [::2]:', list(r[::2]))
