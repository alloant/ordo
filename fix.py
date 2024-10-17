#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tinydb import TinyDB, Query
from tinydb.operations import delete
from prettytable import PrettyTable as PT
from prettytable.colortable import ColorTable as CT, Theme
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
from os.path import exists
import os
import shutil


"""
dbFix = TinyDB(f'rst/fix/feasts_ordo.json')
db = TinyDB('rst/fix/new_feasts_ordo.json')

fixed = db.table('fixed')
move = db.table('move')


for feast in dbFix.all():
    if feast['id'] == '':
        move.insert(dict(feast))
    else:
        fixed.insert(dict(feast))

db.close()

dbOther = TinyDB(f'rst/data/other.json')
db = TinyDB('rst/data/new_other.json')

work = db.table('work')


for feast in sorted(dbOther.table('work').all(), key=lambda x: x['id']):
    work.insert(dict(feast))

db.close()
"""

dbOld = TinyDB('rst/data/old/fix.json')
dbCalendar = TinyDB('rst/data/calendar.json')
dbOther = TinyDB('rst/data/other.json')

print('old:',len(dbOld.all()))

rcf = len(dbCalendar.table('fixed').all())
rcm = len(dbCalendar.table('move').all())
rof = len(dbOther.table('fixed').all())
rom = len(dbOther.table('move').all())

print('new:',rcf+rcm+rof+rom)
