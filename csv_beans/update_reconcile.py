# update_reconcile.py

r'''
  - read Reconcile.csv into Reconcile table
  - clears Reconcile.csv
'''

from datetime import date, timedelta
from collections import defaultdict
import math
import sys

from .database import *
from csv_app.report import *


def run():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--trial-run", "-t", action="store_true", default=False)
    parser.add_argument("--no-clear", "-n", action="store_true", default=False)
    parser.add_argument("reconcile_csv_file", nargs='?', default=None)

    args = parser.parse_args()

    load_database()
    last_row = Reconcile[-1]
    if last_row.account == "cash" and last_row.detail == "w/starts":
        starting_balance = last_row
        ending_balance = starting_balance.copy()
    else:
        starting_balance = None
    last_date = last_row.date
    starting_num_rows = len(Reconcile)
    recon_file = args.reconcile_csv_file or "Reconcile.csv"
    print("Copying", recon_file, "into database")
    rows_added = load_csv(recon_file, from_scratch=False)
    index = Reconcile.find_date(last_date, find_first=False)
    assert index == starting_num_rows, \
      f"Reconcile started with {starting_num_rows} rows up to {last_date}, now has {index} rows up to that date"
    date_column = Reconcile.row_class.column_map['date']
    total = 0
    for row in Reconcile[index:]:
        print(f"{date_column.to_csv(row.date)}: {row.account}({row.detail}) = {row.total}", end='')
        if row.donations:
            print(f", donations={row.donations}")
        else:
            print()
        if row.type == "Revenue":
            total += row.total
            if starting_balance is not None:
                ending_balance += row
                if (row.account, "start") in Starts:
                    ending_balance -= Starts[row.account, "start"]
        elif row.type == "Expenses":
            total -= row.total
            if starting_balance is not None:
                ending_balance -= row
    print("total", total)
    if starting_balance is not None:
        print("ending balance|coin|b1|b5|b10|b20|b50|b100|total")
        print("              ", end='')
        print(f"|{ending_balance.coin:4.3}", end='')
        print(f"|{ending_balance.b1:2}", end='')
        print(f"|{ending_balance.b5:2}", end='')
        print(f"|{ending_balance.b10:3}", end='')
        print(f"|{ending_balance.b20:3}", end='')
        print(f"|{ending_balance.b50:3}", end='')
        print(f"|{ending_balance.b100:4}", end='')
        print(f"|{ending_balance.total}")

    if args.trial_run:
        print("Trial_run: Database not saved")
    else:
        print("Saving database")
        save_database()
        if not args.no_clear:
            while (ans := input(f"Clear {recon_file}? (y) ").lower()) not in ("", "y", "yes", "n", "no"):
                print('Looking for "", "y", "yes", "n" or "no"')
            if ans in ("", "y", "yes"):
                print("Clearing", recon_file)
                with open(recon_file, "r") as file_in:
                    table_name = file_in.readline()
                    headers = file_in.readline()
                with open(recon_file, "w") as file_out:
                    print(table_name, end='', file=file_out)
                    print(headers, end='', file=file_out)
                return
        print("Preserving", recon_file)

