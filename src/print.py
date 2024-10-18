#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
from tinydb import TinyDB, Query
from prettytable import PrettyTable as PT
from datetime import date, timedelta, datetime
import csv

#󰴈󰜡


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
                return f"{self.option1['comments']}, {self.option2['comments']}"

        if index in self.option1:
            if index == 'feast':
                if not self.option1['feast'] and 'Sunday' in self.option1['title']:
                    return 'C'
            return self.option1[index]

        if index == 'subtitle' and self.option2 and 'title' in self.option2:
            return self.option2['title']

        return ''

def final_json(year):
    dbOrdo = TinyDB(f'rst/{year}/scrap_feasts_others_votives.json')
    dbComments = TinyDB(f'rst/data/comments.json')
    db = TinyDB(f'rst/{year}/ordo_without_ep.json')
    Day = Query()

    dt = date(year,1,1)
    while dt < date(year+1,1,1):
        rst = {}
        ordo = ordo_day(sorted(dbOrdo.search((Day.id == dt.strftime('%m%d')) & (Day.option > 0)), key=lambda x: x['option']))

        title = f"<|{dt.day} [small]#{dt.strftime('%a')}#"
        tt = re.sub(r'ˢᵗ', '^st^', ordo['title'])
        tt = re.sub(r'ⁿᵈ', '^nd^', tt)
        tt = re.sub(r'ʳᵈ', '^rd^', tt)
        tt = re.sub(r'ᵗʰ', '^th^', tt)

        rst['date'] = dt.strftime('%Y/%m/%d')
        rst['title'] = tt
        if ordo['subtitle']:
            rst['subtitle'] = ordo['subtitle']
        rst['feast'] = ordo['feast']
        rst['color'] = ordo['color'].upper()
        
        if ordo['mass']:
            mass = ordo['mass']
        elif ordo['lg']:
            mass = f"Mass of the {ordo['lg']}"
        else:
            mass = f"Mass of the day"
        
        rst['mass'] = mass
        rst['ep'] = ordo['ep']
        other_comments = ""
        day_comments = dbComments.search(Day.id == dt.strftime('%m%d'))
        for dc in day_comments:
            if 'comments' in dc and dc['comments']:
                other_comments += f", {dc['comments']}" if other_comments else dc['comments']

        if ordo['comments']:
            rst['comments'] = ordo['comments'] + ' ,' + other_comments
        elif other_comments:
            rst['comments'] = other_comments

        if not any(item in rst['title'] for item in ['Palm','Holy Week','Holy Thursday','Good Friday','Holy Saturday']):
            if rst['feast'] == 'A':
                rst['comments'] = f"{rst['comments']}, So.Ex" if 'comments' in rst else 'So.Ex'
            elif rst['feast'] == 'B' or dt.strftime('%a') == 'Sat':
                rst['comments'] = f"{rst['comments']}, Si.Ex" if 'comments' in rst else 'Si.Ex'

        db.insert(rst)
        dt += timedelta(days=1)
    db.close()


def json_to_adoc(year):
    db = TinyDB(f'rst/{year}/ordo.json')

    with open(f'rst/{year}/ordo.adoc','w') as file:
        file.write(f"= Ordo Delhi {year}\n\n")

        current_month = 0
        for day in db.all():
            dt = datetime.strptime(day['date'],"%Y/%m/%d")
            if current_month < dt.month:
                file.write(f"== {dt.strftime('%B')}\n\n")
                current_month = dt.month
            else:
                file.write("---\n\n")

            file.write('[%unbreakable]\n')
            file.write('[grid=none,frame=none,cols="2,20"]\n')
            file.write('|===\n')

            file.write(f"^|{dt.day} [small]#{dt.strftime('%a')}#")
            if 'feast' in day and day['feast']:
                if day['feast'] == 'C':
                    file.write(f" ^.^|[small]#\({day['feast']})#")
                else:
                    file.write(f" ^.^|[small]#({day['feast']})#")
            else:
                file.write(f" ^.^|")
            
            file.write(f" {day['title']}")
            if 'subtitle' in day:
                file.write(f" +\n[gray]#{day['subtitle']}#")

            file.write("\n") # End first row
           
            if 'Saturday' in day['title']:
                file.write(f">.^|[gray]#󰴈#55 [{day['color']}]*{day['color']}*")
            else:
                file.write(f" ^.^|[small]#{day['mass']}#")

            if 'comments' in day:
                file.write(f" +\n[gray]#{day['comments']}#")
            
            file.write("\n") # End second row

            file.write("|===\n\n")



        file.close()

def json_to_csv(year):
    db = TinyDB(f'rst/{year}/ordo.json')
    Day = Query()

    with open(f'rst/{year}/ordo.csv','w') as file:
        csvf = csv.writer(file)
        
        headers = ['date','feast','color','title','mass','comments']
        csvf.writerow(headers)
        for day in db.all():
            dt = datetime.strptime(day['date'],"%Y/%m/%d")
            row = [dt.strftime('%d %b')] + [day[key] if key in day else '' for key in headers]
            if 'subtitle' in day:
                row[3] += f" ({day['subtitle']})"

            csvf.writerow(row)

    db.close()

