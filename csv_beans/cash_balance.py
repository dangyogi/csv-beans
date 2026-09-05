# cash_balance.py

import logging
from io import StringIO

from .database import *


logger = logging.getLogger('csv-beans.cash_balance')

def cash_balance(step, app):
    r'''Appends to Reconcile table:

       <today>|cash|w/o starts|...
       <today>|cash|w/starts  |...
    '''
    # Find the last "cash", "w/starts" entry in Reconcile
    for i, recon in enumerate(reversed(Reconcile)):
        if recon.account == 'cash' and recon.detail == 'w/starts':
            balance = recon.copy()
            next_idx = len(Reconcile) - i - 1
            break
    else:
        raise ValueError('"cash", "w/starts" not found in Reconcile')

    if next_idx == len(Reconcile) - 1:
        logger.info("Reconcile already ends in cash_balance -- nothing to do")
        return step.mark_run(app)

    # Calculate balance from that point forward
    for recon in Reconcile[next_idx:]:
        if recon.type == "Revenue":
            balance += recon
            if (recon.account, "start",) in Starts:
                balance -= Starts[(recon.account, "start")]
        elif recon.type == "Expenses":
            if recon.donations != 0:
                raise ValueError(f"unexpected donations={recon.donations} "
                                 f"on {recon.date:{Date_format}}, "
                                 f"{recon.account}, {recon.detail} expense")
            balance -= recon
        else:
            if recon.type not in ("Bank", "Cash"):
                raise ValueError(
                   f"Reconcile row {recon.date:{Date_format}}, {recon.account} has unknown type {recon.type}"
                )

    eff_date = recon.date

    # Now balance should reflect our current cash, w/starts
    balance_no_starts = balance.copy()

    # Figure out the cash exchange:
    starts = bills()
    for start in Starts.values():
        if start.detail == 'start':
            balance_no_starts -= start

    # insert monthly initial balance
    Reconcile.insert(date=eff_date, account="cash", detail="w/o starts", **balance_no_starts.as_attrs())
    Reconcile.insert(date=eff_date, account="cash", detail="w/starts", **balance.as_attrs())

    # Give the user the results:
    logger.info("date      |account|detail    | coin| b1| b5|b10|b20|b50|b100|   total")
    buf = StringIO()
    def log(line_start, bills):
        buf.clear()
        buf.write(line_start)
        bills.print(file=buf)
        logger.info(buf.getvalue())
    log(f"{eff_date:{Date_format}}|cash   |w/o starts", balance_no_starts)
    log(f"{eff_date:{Date_format}}|cash   |w/starts  ", balance)

    app.set_changed()
    return step.mark_run(app)
