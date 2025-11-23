#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
from tinydb import TinyDB, Query
from prettytable import PrettyTable as PT
from datetime import date, timedelta, datetime
import csv
from bs4 import BeautifulSoup as BS
import os

def json_to_csv(year):
    db = TinyDB(f'Results/{year}/ordo.json', indent=4)
    Day = Query()

    with open(f'Results/{year}/ordo.csv','w') as file:
        csvf = csv.writer(file)
        
        headers = ['date','feast','color','title','mass','comments']
        csvf.writerow(['date_nice'] + headers)
        for day in db.all():
            dt = datetime.strptime(day['date'],"%Y/%m/%d")
            row = [dt.strftime('%d %b')] + [day[key] if key in day else '' for key in headers]
            if 'subtitle' in day:
                row[4] += f" ({day['subtitle']})"
            if 'ep' in day:
                row[5] += f", EP-{day['ep']}"

            csvf.writerow(row)

    db.close()
