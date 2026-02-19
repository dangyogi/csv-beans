# tables.py

from statistics import mean

from csv_app.table import *
from .rows import Rows


class No_results(Exception):
    pass

class Months(table_unique):
    @staticmethod
    def inc_month(year, month):
        r'''Returns next month (regardless of the contents of this Table) as (year, month).

        Does not skip over May-Oct.
        '''
        if month == 12:
            return year + 1, 1
        return year, month + 1

    @staticmethod
    def dec_month(year, month):
        r'''Returns prior month (regardless of the contents of this Table) as (year, month).

        Does not skip over May-Oct.
        '''
        if month == 1:
            return year - 1, 12
        return year, month - 1

    def last_month(self):
        r'''Returns the row for the last month in the table.
        '''
        today = date.today()
        year = today.year
        month = today.month
        if (year, month) in self:
            year2, month2 = self.inc_month(year, month)
            while (year2, month2) in self:
                year, month = year2, month2
                year2, month2 = self.inc_month(year, month)
            return self[year, month]
        year, month = self.dec_month(year, month)
        while (year, month) not in self:
            year, month = self.dec_month(year, month)
        return self[year, month]

    def attr_by_month(self, month, attr):
        r'''Generates all non-None attr values with this month.

        Raises No_results if no rows are selected.
        '''
        results = False
        for row in self.values():
            if row.month == month:
                ans = getattr(row, attr)
                if ans is not None:
                    yield ans
                    results = True
        if not results:
            raise No_results

    def avg(self, month, attr):
        r'''Rounds answer to nearest integer.
        '''
        try:
            return round(mean(self.attr_by_month(month, attr)))
        except No_results:
            return None

    def avg_num_at_meeting(self, month):
        r'''Rounds answer to nearest integer.
        '''
        return self.avg(month, 'num_at_meeting')

    def avg_staff_at_breakfast(self, month):
        r'''Rounds answer to nearest integer.
        '''
        return self.avg(month, 'staff_at_breakfast')

    def avg_tickets_claimed(self, month):
        r'''Rounds answer to nearest integer.
        '''
        return self.avg(month, 'tickets_claimed')

    def avg_meals_served(self, month):
        r'''Rounds answer to nearest integer.
        '''
        return self.avg(month, 'meals_served')

load_rows(Rows, Months)


__all__ = "Decimal date datetime timedelta abbr_month Tables Database " \
          "load_database save_database load_csv load_all clear_all check_foreign_keys " \
          "CSV_dialect CSV_format".split()

