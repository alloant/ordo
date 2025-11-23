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

class ordo_day:
    def __init__(self, rst):
        self.option1 = rst[0]
        self.option2 = rst[1] if len(rst) > 1 else None

    def __getitem__(self,index):
        if self.option2 and index in self.option2:
            if not index in self.option1:
                if index == 'feast':
                    if 'Sunday' in self.option1['title']:
                        return 'C' if 'C' < self.option2['feast'] else self.option2['feast']
                elif index in ['mass','ep','color','lg']:
                    return ''
                return self.option2[index]

            if index == 'feast':
                return self.option1['feast'] if self.option1['feast'] < self.option2['feast'] else self.option2['feast']
            elif index == 'comments':
                if index in self.option1 and self.option1[index]:
                    return f"{self.option1['comments']}, {self.option2['comments']}"
                else:
                    return self.option2p[index]

        if index in self.option1:
            if index == 'feast':
                if not self.option1['feast'] and 'Sunday' in self.option1['title']:
                    return 'C'
            return self.option1[index]

        if index == 'subtitle' and self.option2 and 'title' in self.option2:
            return self.option2['title']

        return ''

def add_ex(ex,text):
    rst = text
    if not (ex in text or ex == 'Si.Ex' and 'So.Ex' in text):
        if ex == 'So.Ex' and 'Si.Ex' in text:
            rst = text.replace('Si.Ex','So.Ex')
        else:
            if text:
                rst += ', '

            rst += ex

    return rst

def final_json(year):
    print(f'Adding comments from Data/comments.json. Saving result in Results/{year}/ordo_without_ep.json')
    dbOrdo = TinyDB(f'Results/{year}/scrap_feasts_others_votives.json', indent=4)
    dbComments = TinyDB(f'Resources/Data/comments.json', indent=4)
    db = TinyDB(f'Results/{year}/ordo_without_ep.json', indent=4)
    Day = Query()

    ## Check all the days of the year
    dt = date(year,1,1)
    oct_Corpus = 0
    sj_dt = date(year,3,19)
    bt_dt = dbOrdo.search(Day.title=='The Most Holy Trinity')[0]['id']
    bt_dt = date(year,int(bt_dt[:2]),int(bt_dt[2:]))
    while dt < date(year+1,1,1):
        # Getting data
        ordo = ordo_day(sorted(dbOrdo.search((Day.id == dt.strftime('%m%d')) & (Day.option > 0)), key=lambda x: x['option']))
        
        # Preparing result
        rst = {}
        rst['date'] = dt.strftime('%Y/%m/%d')
        rst['title'] = ordo['title']

        if ordo['subtitle']:
            rst['subtitle'] = ordo['subtitle']
        rst['feast'] = ordo['feast']
        rst['color'] = ordo['color'].upper()
        
        ## Choosing the Mass
        if ordo['lg']:
            rst['lit_grade'] = ordo['lg']
        else:
            rst['lit_grade'] = ''

        if ordo['mass']:
            mass = ordo['mass']
        elif ordo['lg']:
            mass = f"Mass of the {ordo['lg']}"
        else:
            mass = f"Mass of the day"        
        rst['mass'] = mass

        rst['ep'] = ordo['ep']

        ## Final comments
        other_comments = ""
        day_comments = dbComments.search(Day.id == dt.strftime('%m%d'))
        for dc in day_comments:
            if 'comments' in dc and dc['comments']:
                other_comments += f", {dc['comments']}" if other_comments else dc['comments']
        
        if ordo['comments'] and other_comments:
            rst['comments'] = ordo['comments'] + ', ' + other_comments
        elif other_comments:
            rst['comments'] = other_comments
        else:
            rst['comments'] = ''
        
        # With the exception of Holy Week put SoEx and SiEx in A and B feasts
        if not any(item in rst['title'] for item in ['Palm','Holy Week','Holy Thursday','Good Friday','Holy Saturday']):
            if rst['feast'] == 'A':
                rst['comments'] = add_ex('So.Ex',rst['comments'])
            elif (rst['feast'] == 'B' or dt.strftime('%a') == 'Sat'):
                rst['comments'] = add_ex('Si.Ex',rst['comments'])
        
        ## Vigil before first Friday
        if dt.weekday() == 4:
            friday = dt + timedelta(days=1)

            if 1 <= friday.day < 8:
                if rst['comments']:
                    rst['comments'] += ', '
                rst['comments'] += 'Vigil'

        ## Here for Octave of Corpus
        if 0 < oct_Corpus < 8:
            rst['comments'] = add_ex('So.Ex',rst['comments'])
            oct_Corpus += 1

        if rst['title'] == 'The Most Holy Body and Blood of Christ':
            oct_Corpus = 1

        ## Trisagio Angelicum
        if 0 <= (bt_dt - dt).days < 3:
            if rst['comments']:
                rst['comments'] += ', '
            rst['comments'] += 'Trisagium Angelicum'

        # On Sundays
        if dt.weekday() == 6:
            #Quicumque
            if 15 <= dt.day <= 21: # Third Sunday
                if rst['comments']:
                    rst['comments'] += ', '

                rst['comments'] += f"Quicumque"

            # Sundays of St. Jospeh
            if dt < sj_dt:
                bt_days = (sj_dt - dt).days
                if bt_days <= 6*7 + sj_dt.weekday() + 1:
                    sofsj = int(7 - (bt_days - sj_dt.weekday() - 1)/7)
                    if rst['comments']:
                        rst['comments'] += ', '

                    rst['comments'] += f"{sofsj} Sunday of St. Joseph"

        # Insert result
        db.insert(rst)

        # Incress day to continue the loop
        dt += timedelta(days=1)
    db.close()
