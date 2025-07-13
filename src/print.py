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

def final_json(year):
    print(f'Adding comments (like flowers, benedicions, octaves, etc... Saving result in rst/{year}/ordo_without_ep.json')
    dbOrdo = TinyDB(f'rst/{year}/scrap_feasts_others_votives.json', indent=4, sort_keys=True)
    dbComments = TinyDB(f'rst/data/comments.json', indent=4, sort_keys=True)
    db = TinyDB(f'rst/{year}/ordo_without_ep.json', indent=4, sort_keys=True)
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

        ## Replace st for super st
        title = f"<|{dt.day} [small]#{dt.strftime('%a')}#"
        tt = re.sub(r'ˢᵗ', '^st^', ordo['title'])
        tt = re.sub(r'ⁿᵈ', '^nd^', tt)
        tt = re.sub(r'ʳᵈ', '^rd^', tt)
        tt = re.sub(r'ᵗʰ', '^th^', tt)
        rst['title'] = tt

        if ordo['subtitle']:
            rst['subtitle'] = ordo['subtitle']
        rst['feast'] = ordo['feast']
        rst['color'] = ordo['color'].upper()
        
        ## Choosing the Mass
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

        # Sundays of St. Jospeh
        if dt.weekday() == 6 and dt < sj_dt:
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


def json_to_adoc(year):
    db = TinyDB(f'rst/{year}/ordo.json', indent=4, sort_keys=True)

    with open(f'rst/{year}/ordo.adoc','w') as file:
        file.write(f"= Ordo Delhi {year}\n\n")

        current_month = 0
        for day in db.all():
            dt = datetime.strptime(day['date'],"%Y/%m/%d")
            if current_month < dt.month:
                file.write(f"== {dt.strftime('%B')}\n\n")
                current_month = dt.month
            #else:
            #    file.write("---\n\n")

            file.write('[%unbreakable]\n')
            file.write('[grid=none,frame=none,cols="2,20",stripes=even]\n')
            file.write('|===\n')

            file.write("| |\n")

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
           
            if 'Saturday' in day['title'] or 'feast' in day and day['feast'] < 'C' and day['feast'] or dt.month == 5:
                file.write(f">.^|[pink]#󰴈# [{day['color']}]*{day['color']}*")
            else:
                file.write(f">.^|[{day['color']}]*{day['color']}*")
            
            file.write(f" ^.^|[small]#{day['mass']}#, [ep]#EP{day['ep']}#")

            if 'comments' in day:
                file.write(f" +\n[gray]#{day['comments']}#")
            
            file.write("\n") # End second row
            file.write("|===\n\n")



        file.close()

def json_to_csv(year):
    db = TinyDB(f'rst/{year}/ordo.json', indent=4, sort_keys=True)
    Day = Query()

    with open(f'rst/{year}/ordo.csv','w') as file:
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

