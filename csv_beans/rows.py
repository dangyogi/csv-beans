# rows.py

import math

from csv_app.row import *
from csv_app.table import Database, set_database_filename

set_database_filename("beans.csv")


class Months(Row):
    columns = (
        Column("month", parse=int, required=True),
        Column("year", parse=int, required=True),
        Date_column("start_date"),
        Date_column("end_date"),
        Column("num_at_meeting", "#@mtg", parse=int),
        Column("staff_at_breakfast", "stf@bf", parse=int),
        Column("tickets_claimed", "tkt_clm", parse=int),
        Column("month_str", "mth_str", calculated=True),
        Column("meals_served", "ml_srv", parse=int, calculated=True),
        Date_column("meeting_date", "mtg_date", calculated=True),
        Date_column("breakfast_date", "bf_date", calculated=True),
    )
    primary_keys = "year", "month"

    @property
    def month_str(self):
        return f"{abbr_month(self.month)} '{str(self.year)[2:]}"

    @property
    def prev_month(self):
        r'''returns (year, month)
        '''
        if self.month == 1:
            return self.year - 1, 12
        return self.year, self.month - 1

    @property
    def meals_served(self):
        if self.staff_at_breakfast is None or self.tickets_claimed is None:
            return None
        return self.staff_at_breakfast + self.tickets_claimed

    @property
    def meeting_date(self):
        return self.nth_day(1, TUESDAY)

    @property
    def breakfast_date(self):
        return self.nth_day(2, SATURDAY)

    def nth_day(self, n, day):
        firstday = date(self.year, self.month, 1).weekday()
        days_to_day = day - firstday
        if days_to_day >= 0:
            return date(self.year, self.month, days_to_day + 1 + 7 * (n - 1))
        return date(self.year, self.month, days_to_day + 8 + 7 * (n - 1))

class Globals(Row):
    columns = (
        Column("name", required=True),   # e.g., "meeting dinner", "breakfast"
        Column("int", parse=int),
        Column("decimal", parse=Decimal),
    )
    primary_key = "name"

class Accounts(Row):
    # account=varchar(50),              # e.g., "adv tickets", "door tickets", "50/50", "bf supplies"
    # section=varchar(50, null=True),   # e.g., "Cash Flow", "Balance"
    # category=varchar(50, null=True),  # e.g., "Breakfast", "Other", "Current Balance"
    # type=varchar(10, null=True),      # e.g., "Revenue", "Expenses"
    columns = (
        Column("account", required=True),
        Column("section"),
        Column("category"),
        Column("type"),
    )
    primary_key = "account"

class bills:
    # If columns are added or deleted, you'll need to redo Starts.columns comment and Reconcile.columns!
    columns = (  # [0:7] are stored, [7] is calculated
        Column("coin", parse=Decimal, default=0),
        Column("b1", parse=int, default=0),
        Column("b5", parse=int, default=0),
        Column("b10", parse=int, default=0),
        Column("b20", parse=int, default=0),
        Column("b50", parse=int, default=0),
        Column("b100", parse=int, default=0),
        Column("total", parse=Decimal, calculated=True),
    )

    @property
    def bill_columns(self):
        return (col for col in bills.columns if not col.calculated)

    def __init__(self, coin=0, b1=0, b5=0, b10=0, b20=0, b50=0, b100=0):
        self.coin = coin
        self.b1 = b1
        self.b5 = b5
        self.b10 = b10
        self.b20 = b20
        self.b50 = b50
        self.b100 = b100

    @classmethod
    def value(cls, attr):
        r'''The monetary value of `attr`.
        '''
        if attr == 'coin':
            return 1
        assert attr[0] == 'b', f"expected attr starting with 'b', got {attr=}"
        return int(attr[1:])

    def copy(self):
        return bills(**self.as_attrs())

    def as_attrs(self):
        return {col.name: getattr(self, col.name) for col in self.bill_columns}

    def __add__(self, bill2):
        r'''Returns new bills object.
        '''
        return bills(**{col.name: getattr(self, col.name) + getattr(bill2, col.name) for col in self.bill_columns})

    def __sub__(self, bill2):
        r'''Returns new bills object.
        '''
        return bills(**{col.name: getattr(self, col.name) - getattr(bill2, col.name) for col in self.bill_columns})

    def __iadd__(self, bill2):
        r'''Adds bill2 to self.
        '''
        for col in self.bill_columns:
            self.add_to_attr(col.name, bill2)
        return self

    def __isub__(self, bill2):
        r'''Subtracts bill2 from self.
        '''
        for col in self.bill_columns:
            self.sub_from_attr(col.name, bill2)
        return self

    def add_to_attr(self, attr, inc):
        r'''If inc is bills, gets attr from inc; else inc must be the number to add.
        '''
        if isinstance(inc, bills):
            inc = getattr(inc, attr)
        setattr(self, attr, getattr(self, attr) + inc)

    def sub_from_attr(self, attr, dec):
        r'''If dec is bills, gets attr from dec; else dec must be the number to subtract.
        '''
        if isinstance(dec, bills):
            dec = getattr(dec, attr)
        setattr(self, attr, getattr(self, attr) - dec)

    @property
    def total(self):
        return sum(self.value(col.name) * getattr(self, col.name) for col in self.bill_columns)

    def print_header(self, file):
        r'''Appends bill column names to end of current print line.

        Terminates the line.
        '''
        print("| coin", end='', file=file)
        print("| b1", end='', file=file)
        print("| b5", end='', file=file)
        print("|b10", end='', file=file)
        print("|b20", end='', file=file)
        print("|b50", end='', file=file)
        print("|b100", end='', file=file)
        print("|total", file=file)

    def print(self, file):
        r'''Appends bill columns to end of current print line.

        Terminates the line.
        '''
        print(f"|{self.coin:5.02f}", end='', file=file)
        print(f"|{self.b1:3d}", end='', file=file)
        print(f"|{self.b5:3d}", end='', file=file)
        print(f"|{self.b10:3d}", end='', file=file)
        print(f"|{self.b20:3d}", end='', file=file)
        print(f"|{self.b50:3d}", end='', file=file)
        print(f"|{self.b100:4d}", end='', file=file)
        print(f"|{self.total:8.02f}", file=file)

class Starts(Row, bills):  # row first, so it's __init__ is used.
    # If columns are added or deleted, you'll need to redo Reconcile.columns!
    columns = (  # [0:9] are stored, [9:] are calculated
        Column("account", required=True),
        Column("detail", required=True),
    ) + bills.columns + (
        Column("section", hidden=True, calculated=True),
        Column("category", hidden=True, calculated=True),
        Column("type", hidden=True, calculated=True),
    )
    primary_keys = "account", "detail"
    foreign_keys = "Accounts",

    @property
    def section(self):
        return Database.Accounts[self.account].section

    @property
    def category(self):
        return Database.Accounts[self.account].category

    @property
    def type(self):
        return Database.Accounts[self.account].type

class Reconcile(Starts):
    columns = (
        Date_column("date", required=True),
    ) + Starts.columns[0:1] + (  # account column
        Column("detail"), # detail without required=True
    ) + Starts.columns[2:9] + (  # rest of Starts stored columns
        Column("donations", "don", parse=Decimal, default=0),
    ) + Starts.columns[9:] + (   # Starts calculated columns
        Column("ticket_price", "tkt_prc", parse=int, calculated=True),
        Column("tickets_sold", "tkts_sold", parse=int, calculated=True),
    )
    primary_keys = None

    @property
    def total(self):
        r'''Includes Start amount.
        '''
        return super().total - self.donations

    @property
    def ticket_price(self):
        if self.account.endswith(" tickets"):
            return Database.Globals[self.account[:-1] + " price"].int
        return None

    @property
    def tickets_sold(self):
        price = self.ticket_price
        if price is None:
            return None
        total = self.total
        start_key = self.account, "start"
        if start_key in Database.Starts:
            total -= Database.Starts[start_key].total
        return int(math.ceil(total / price))


# These must be in logical order based on what has to be defined first
Rows = (Months, Globals, Accounts, Starts, Reconcile,
       )


__all__ = "Decimal date datetime timedelta abbr_month bills Rows".split()


def run():
    create_database_py(Rows)

