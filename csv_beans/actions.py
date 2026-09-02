# actions.py

import logging

from csv_app.action import *
from csv_app.report import dump_table
from tui_app.tui import get_app
from tui_app.table_screen import table_screen
from tui_app.row_screen import row_screen
from . import tables
from .database import *


logger = logging.getLogger('csv-beans.actions')

def table(table_name, validate_fn=None, mark_run=True):
    def run_table_screen(step, app):
        if mark_run:
            step.mark_run(app)
        return table_screen(tables.Tables[table_name], back=app.screen, validate_fn=validate_fn)
    return run_table_screen

def stub(step, app):
    logger.info(f"stub {step.name}")
    app.set_changed()
    return step.mark_run(app)

def save(step, app):
    logger.info(f"save {step.name}")
    step.mark_run(app)    # sets app.changed, run this first so mark is saved
    if not app.testing:
        save_database()
    app.reset_changed()
    return 'REFRESH'

def print(table_name):
    def print_table(step, app):
        dump_table(table_name, pdf=True, load=False)
        return step.mark_run(app)
    return print_table

class ExitStep(Step):
    def __init__(self, id, task, abort=False, ok_fn=None):
        super().__init__(id, task, self.fn, ok_fn=ok_fn)
        self.abort = abort

    @property
    def can_run(self):
        return self.app.changed == self.abort

    def fn(self, step, app):
        if self.abort:
            return "APP_ABORT"
        return "APP_EXIT"


def last_month_update(global_validate=None):
    return lambda step, app: \
             row_screen.for_update(Months.last_month(), app.screen,
                                   global_validate=global_validate,
                                   callback=lambda: step.mark_run(app))

def create_month(step, app):
    def year_is(year):                       # already an int (convert_fn=int)
        def month_is(month):                 # already an int
            if app.testing:
                if not (1 <= month <= 12):
                    raise ValueError(f"{month=} must be 1-12")
            else:
                if not (1 <= month <= 4 or 11 <= month <= 12):
                    raise ValueError(f"{month=} must be 1-4 or 11-12")
            logger.info(f"month_is: {month=}")
            Months.insert(year=year, month=month, served_fudge=1.35, consumed_fudge=0.9)
            app.set_changed()
            return step.mark_run(app)
        logger.info(f"year_is: {year=}")
        today = date.today()
        if not (today.year <= year <= today.year + 1):
            raise ValueError(f"Invalid {year=}, must be between {today.year} and {today.year + 1}")
        app.screen.ask_question("month", month_is, str(next_mth), convert_fn=int)
    last_month = Months.last_month()
    yr, mth = last_month.year, last_month.month
    if mth == 4:
        next_yr, next_mth = yr, 11
    else:
        next_yr, next_mth = Months.inc_month(yr, mth)
    logger.info(f"create_month: {yr=}, {mth=}, {next_yr=}, {next_mth=}")
    app.screen.ask_question("year", year_is, str(next_yr), convert_fn=int)

# Task(id, *prereqs, column_break=False, can_rerun_after_commit=False)
# Note(id, task)
# Step(id, task, fn, *prereqs, ok_fn=None, can_rerun=False, can_rerun_after_commit=False,
#      commits_task=False, disable_prereqs=False)

# Before Member Meeting (if new transactions)
Task1 = Task(1, can_rerun_after_commit=True)

# record petty cash as "petty cash"
Step(101, Task1, stub, can_rerun=True)

# other in: "donations", "revenue"(w/detail)
Note(102, Task1)

# other out: "Xmas donation", "expense"(w/detail)
Note(103, Task1)

# update reconcile
Step(104, Task1, stub, 101)

# run cash balance
Step(105, Task1, stub, 104)

# count cash, compare to "cash w/starts"
Step(106, Task1, stub, 105)

# run treasurer report
Step(107, Task1, stub, 106)

# print treasurer report
Step(108, Task1, stub, 107)

# review treasurer report
Step(109, Task1, stub, 108)

# discard previous treasurer report
Step(110, Task1, stub, 109, commits_task=True)

# Create New Month Folder
Task2 = Task(2, 1)

# create new month
Step(201, Task2, stub) #create_month)

# write start/end dates on New Month Folder
Step(202, Task2, stub, 201)

# move Bylaws to New Month Folder
Step(203, Task2, stub, 202)

# make 4 copies of treasurer's report
Step(204, Task2, stub, 108, 202)

# put 1 in old month, 3 in new month
Note(205, Task2)

# file old month folder away
Step(206, Task2, stub, 204)

# place new petty cash record in month folder
Step(207, Task2, stub, 202)

# print new treasurer checklist
Step(208, Task2, stub, 202, commits_task=True)

# place treasurer checklist in month folder
Note(209, Task2)

# Day after member meeting
Task3 = Task(3, 2, can_rerun_after_commit=True)

# set meeting attendance
Step(301, Task3, stub, 2, can_rerun=True)

# record meeting dinner reimb as "meeting dinner"
Step(302, Task3, stub, 301, can_rerun=True)

# place dinner receipt in new month folder
Step(303, Task3, stub, 302, commits_task=True)


# Week before breakfast
Task4 = Task(4, 3, can_rerun_after_commit=True)

# get receipts from shoppers
Step(401, Task4, stub, 3, can_rerun=True)

# compare receipts with P.O.s
Step(402, Task4, stub, 401)

# note differences on P.O.
Note(403, Task4)

# issue reimbs with attached receipt and P.O.
Step(404, Task4, stub, 402)

# staple reimb receipt to P.O. and receipt
Step(405, Task4, stub, 404)

# record reimbs as "Sam's card", "bf supplies",
Step(406, Task4, stub, 405)

# "expense, bf" (w/detail)
Note(407, Task4)

# place stapled reimbs in month folder
Step(408, Task4, stub, 406)

# set aside door ticket sales slip, donation slip
Step(409, Task4, stub, 408)

# 20x1, 2x5, 2x10 = 50
Note(410, Task4)

# set aside 50/50 ticket sales slip, donation slip
Step(411, Task4, stub, 409)

# 10x1, 2x5, 2x10 = 40
Note(412, Task4)

# place calculator in briefcase
Step(413, Task4, stub, 411, commits_task=True)

# Day after breakfast
Task5 = Task(5, 4, column_break=True, can_rerun_after_commit=True)

# remove calculator from briefcase
Step(501, Task5, stub, 4)

# record staff attendance
Step(502, Task5, stub, 501)

# record tickets claimed
Step(503, Task5, stub, 502)

# count revenue cash
Step(504, Task5, stub, 503)

# record breakfast revenue as "adv tickets",
Step(505, Task5, stub, 504)

# "door tickets", "50/50" & "bf donations"
Note(506, Task5)

# place slips in month folder
Step(507, Task5, stub, 505)

# update Reconcile
Step(508, Task5, stub, 505)

# run cash balance
Step(509, Task5, stub, 508)

# count cash, compare to "cash w/starts"
Step(510, Task5, stub, 509)

# run cash swap
Step(511, Task5, stub, 510)

# exchange "cash out" for "Cash In"
Step(512, Task5, stub, 511)

# count cash, should match "cash w/starts"
Step(513, Task5, stub, 512)

# run treasurer report
Step(514, Task1, stub, 513)

# print treasurer report
Step(515, Task1, stub, 514)

# review treasurer report
Step(516, Task1, stub, 515, commits_task=True)


# view/edit tables
Task6 = Task(6)

# Months
Step(601, Task6, table("Months", mark_run=False), can_rerun=True)

# Globals
Step(602, Task6, table("Globals", mark_run=False), can_rerun=True)

# Accounts
Step(603, Task6, table("Accounts", mark_run=False), can_rerun=True)

# Starts
Step(604, Task6, table("Starts", mark_run=False), can_rerun=True)

# Pending
Step(605, Task6, table("Pending", mark_run=False), can_rerun=True)

# Reconcile
Step(606, Task6, table("Reconcile", mark_run=False), can_rerun=True)

# Steps
Step(607, Task6, table("Steps", mark_run=False), can_rerun=True)


# other
Task7 = Task(7)

# save database
Step(701, Task7, save, ok_fn=lambda: get_app().changed, can_rerun=True)

# git commit/push
Step(702, Task7, stub, can_rerun=True)

# exit
ExitStep(703, Task7, ok_fn=lambda: not get_app().changed)

# abort
ExitStep(704, Task7, abort=True, ok_fn=lambda: get_app().changed)


