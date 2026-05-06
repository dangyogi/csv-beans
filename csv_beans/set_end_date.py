# set_end_date.py

r'''Sets end_date in current Month.
'''

import sys

sys.path.append('.')
from database import *


def run():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--end-day", "-d", type=int, default=None)
    parser.add_argument("--end-month", "-m", type=int, default=None)

    args = parser.parse_args()
    end_month = args.end_month
    end_day = args.end_day

    load_database()

    last_month = list(Months.values())[-1]
    print(f"last_month: {last_month.month_str}, ", end='')
    end_year = last_month.year
    if end_month is None:
        end_month = last_month.month
        if end_day is None:
            next_month = date(end_year, end_month, 28) + timedelta(days=4)
            end_day = (next_month.replace(day=1) - timedelta(days=1)).day
    else:
        if end_month < last_month.month and end_month == 1:
            end_year += 1
        if end_day is None:
            print("ERROR: Must also specify end_day (-d) when end_month (-m) is specified", sys.stderr)
            sys.exit(1)

    print(f"{end_year=}, {end_month=}, {end_day=}")
    end_date = date(end_year, end_month, end_day)

    if last_month.end_date is not None:
        print(f"end_date={last_month.end_date:%b %d, %y}")
        ans = input(f"Override current end_date with {end_date:%b %d, %y}? (y/n)")
        if ans[0].lower() == 'n':
            print("Terminated, Database not saved", file=sys.stderr)
            sys.exit(1)

    ans = input(f"Set {last_month.month_str}.end_date to {end_date:%b %d, %y}? (y/n)")
    last_month.end_date = end_date

    if not ans or ans[0].lower() == 'y':
        print("Saving Database")
        save_database()
    else:
        print("Trial_run: Database not saved")

