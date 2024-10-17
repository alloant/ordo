#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
from tinydb import TinyDB, Query
from prettytable import PrettyTable as PT
from datetime import date, timedelta, datetime
import csv

#󰴈󰜡
def to_csv(year):
    db = TinyDB(f'rst/{year}mixed_vot.json')
    Day = Query()

    with open(f'print/{year}ordo.csv','w') as file:
        csvf = csv.writer(file)
        
        dt = date(year,1,1)
        csvf.writerow(['Date','Feast','Color','Title','Mass','Comments'])
        while dt.year <= year:
            day = db.search((Day.id == dt.strftime('%m%d')) & (Day.option == 1))
            day2 = db.search((Day.id == dt.strftime('%m%d')) & (Day.option == 2))
            if day:
                print(dt,day[0].values())
                day = day[0]
                row = []
                row.append(dt.strftime('%d %b'))
                row.append(day['feast'] if 'feast' in day else '')
                row.append(day['color'] if 'color' in day else '')
                row.append(day['title'] if 'title' in day else '')
                if day2:
                    row[-1] += f" ({day2[0]['title'] if 'title' in day2[0] else ''})"
                    if 'feast' in day2[0]:
                        if day2[0]['feast'] < row[1]:
                            row[1] = day2[0]['feast']

                row.append(day['mass'] if 'mass' in day else f"Mass of the {day['lg']}" if 'lg' in day and day['lg'] else '')
                row.append(day['comments'] if 'comments' in day else '')
                if day2:
                    cm = day2[0]['comments'] if 'comments' in day2[0] else ''
                    if row[-1] and cm:
                        row[-1] += ', '
                    row[-1] += cm


                csvf.writerow(row)
            
            dt += timedelta(days=1)


    db.close()

def print_ordo(year):
    to_csv(year)

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
                return self.option2[index]

            if index == 'feast':
                return self.option1['feast'] if self.option1['feast'] < self.option2['feast'] else self.option2['feast']
            elif index == 'comments':
                return f"{self.option1['comments']}, {self.option2['comments']}"

        if index in self.option1:
            if index == 'feast':
                if not self.option1['feast'] and 'Sunday' in self.option1['title']:
                    return 'C'
            return self.option1[index]

        if index == 'subtitle' and self.option2 and 'title' in self.option2:
            return self.option2['title']

        return ''

def to_adoc(year):
    db = TinyDB(f'rst/{year}mixed_vot.json')
    Day = Query()

    with open(f'print/{year}ordo.adoc','w') as file:
        file.write(f"= Ordo Delhi {year}\n\n")

        dt = date(year,1,1)
        current_month = 0
        while dt < date(year+1,1,1):
            if current_month < dt.month:
                file.write(f"== {dt.strftime('%B')}\n\n")
                current_month = dt.month
            ordo = ordo_day(sorted(db.search((Day.id == dt.strftime('%m%d')) & (Day.option > 0)), key=lambda x: x['option']))

            file.write('[%unbreakable]\n')
            file.write('[grid=none,cols="2,20"]\n')
            file.write('|==========================\n')
            
            title = f"<|{dt.day} [small]#{dt.strftime('%a')}#"
            tt = re.sub(r'ˢᵗ', '^st^', ordo['title'])
            tt = re.sub(r'ⁿᵈ', '^nd^', tt)
            tt = re.sub(r'ʳᵈ', '^rd^', tt)
            tt = re.sub(r'ᵗʰ', '^th^', tt)

            if ordo['feast']:
                if ordo['feast'] in ['c','C']:
                    title += f" |[small]#\({ordo['feast']})# *{tt}*"
                else:
                    title += f" |[small]#({ordo['feast']})# *{tt}*"
            else:
                if dt.strftime('%a') == 'Sun':
                    title += f" |*{tt}*"
                else:
                    title += f" |{tt}"
            title += f" [gray]#({ordo['subtitle']})#\n" if ordo['subtitle'] else '\n'
            file.write(title)
            
            #mass = f"^.>|[V]*{ordo['color']}*"
            mass = f"^|[{ordo['color'].upper()}]*{ordo['color'].upper()}*"
            if ordo['mass']:
                mass += f" |[small]#{ordo['mass']}#\n"
            elif ordo['lg']:
                mass += f" |[small]#Mass of the {ordo['lg']}#\n"
            else:
                mass += f" |[small]#Mass of the day#\n"
            file.write(mass)

            if ordo['comments']:
                file.write(f"||[gray]#{ordo['comments']}#\n")
            file.write("|==========================\n\n\n")
            
            dt += timedelta(days=1)

        file.close()
