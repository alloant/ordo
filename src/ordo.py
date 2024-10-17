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

days = ["Monday", "Tuesday", "Wednesday", 
        "Thursday", "Friday", "Saturday", "Sunday"]

VI = Theme(
        default_color="35",
        vertical_color="35",
        horizontal_color="35",
        junction_color="35",
    )

WH = Theme(
        default_color="37",
        vertical_color="37",
        horizontal_color="37",
        junction_color="37",
    )

GR = Theme(
        default_color="32",
        vertical_color="32",
        horizontal_color="32",
        junction_color="32",
    )

def setVotives(year):
    path = f'rst/{year}votives.json'
    if not exists(path):
        shutil.copy('data/votives.json',path)
    
    path = f'rst/{year}mixed_vot.json'
    if not exists(path):
        shutil.copy(f'rst/{year}mixed.json',path)

    db = TinyDB(f'rst/{year}mixed_vot.json')
    dbVot = TinyDB(f'rst/{year}votives.json')
    Day = Query()
    Vot = Query()

    rst = db.search( (Day.title.search("Ordinary Time")) & (Day.option==1) & (Day.lg2>3) & (~Day.mass.exists()) )

    names = ["","color","mass","freq"]
    current_month = 0
    for row_day in rst:
        td = date(year,int(row_day['id'][:2]),int(row_day['id'][2:]))
        if current_month == 0 or current_month < int(row_day['id'][:2]):
            current_month = int(row_day['id'][:2])
            month = PT()
            sm = td.replace(day=1)
            em = td.replace(day=1) + relativedelta(months=1)

            num_days = []
            week_days = []
            free_days = []

            while sm < em:
                num_days.append(sm.day)
                free = db.search( (Day.title.search("Ordinary Time")) & (Day.option==1) & (Day.lg2>3) & (~Day.mass.exists()) & (Day.id == sm.strftime('%m%d')) )
                week_days.append(sm.strftime('%a'))
                if free:
                    free_days.append('x')
                else:
                    free_days.append('')
        
                sm += timedelta(days=1)
            
            month.field_names = num_days
            month.add_row(week_days)
            month.add_row(free_days)

        tb = PT()
        tb.field_names = names
        weekday = days[date(year,int(row_day['id'][:2]),int(row_day['id'][2:])).weekday()]
        vot_day = dbVot.search(Vot.days == weekday)
        vot_free = dbVot.search(Vot.days=="")

        weekdays_year = db.count( (Day.title.search("Ordinary Time")) & (Day.option==1) & (Day.lg2>3) & (~Day.mass.exists()) & (Day.title.search(weekday)) )

        for i,row in enumerate(vot_day+vot_free):
            r = [f"{i+1}"]
            if 'count' in row:
                ct = row['count']
            else:
                ct = 0
                
            if 'last' in row:
                lt = datetime.strptime(row_day['id'],'%m%d') - datetime.strptime(row['last'],'%m%d')
                lt = lt.days
            else:
                lt = 0

            for v in names[1:-1]:
                if v in row:
                    if i < len(vot_day):
                        value = f"\033[1m{row[v]}\033[0m"
                    else:
                        value = row[v]
                    r.append(value)
                else:
                    r.append("")
                
            if ct > 0:
                r.append(f'Used \033[1m{ct}\033[0m times. Last time was \033[1m{lt}\033[0m days ago')
            else:
                r.append('')

            tb.add_row(r)
        

        os.system('clear')
        print(month)

        print(f"\033[1m {td.strftime('%d %B')} - {row_day['title']}\033[0m")
        print(f"There are {weekdays_year} free {weekday}s this year")
        print(tb)
        option = input("Choose value: ")

        vt = (vot_day+vot_free)[int(option)-1]
        
        if 'count' in vt:
            dbVot.update({'count': vt['count'] + 1,'last':row_day['id']},doc_ids=[vt.doc_id])
        else:
            dbVot.update({'count': 1,'last':row_day['id']},doc_ids=[vt.doc_id])

        db.update({'mass': vt['mass']},doc_ids=[row_day.doc_id])
        db.update({'color': vt['color']},doc_ids=[row_day.doc_id])

    db.all()
    db.close()
    dbVot.all()
    dbVot.close()

def listOrdo(year):
    db = TinyDB(f'{year}final.json')
    Day = Query()

    rst = db.search(Day.option == True)

    tb = PT()
    tb.field_names = [""] + list(rst[0].keys())
    tb.add_rows([[f"({i})"] + list(row.values()) for i,row in enumerate(rst)])

    print(tb)

    db.close()


def joinScrapFix(year):
    db = TinyDB(f'rst/{year}mixed.json')
    dbs = TinyDB(f'rst/{year}scrap.json')
    dbf = TinyDB(f'data/fix.json')
    
    Day = Query()

    for row in dbs.all() + dbf.all():
        if row['id'] != "" and 'title' in row:
            mov = dbf.search(Day.title == row['title'])
            if mov:
                for field in ['feast','mass','comments','subtitle']:
                    if field in mov[0]:
                        row[field] = mov[0][field]

            db.insert(dict(row))

    db.all()
    db.close()

def prepareOrdo(year, one_day = None):
    path = f'rst/{year}mixed.json'
    if not exists(path):
        joinScrapFix(year)
    
    db = TinyDB(path)
    Day = Query()

    day = one_day if one_day else date(year,1,1)

    while day.year == year:
        dayID = day.strftime("%m%d")
        if db.contains((Day.id == dayID) & (Day.option == 1)) and not one_day:
            day += timedelta(days=1)
            continue
        
        rst = db.search(Day.id == dayID)

        if len(rst) > 1:
            if len(rst) == 2 and 'title' in rst[0] and 'title' in rst[1]: # Here there are only two with the same title, I take the one with the feasts
                if rst[0]['title'] == rst[1]['title']:
                    doc_id = rst[0].doc_id if 'feast' in rst[0] else rst[1].doc_id
                    db.update({'option': 1},doc_ids=[doc_id])
                    day += timedelta(days=1)
                    continue
            
            if rst.count(Day.lg2 < 4) == 1: # There is only one Sol, Feast, Memorial, Sunday...
                if rst.count( (Day.lg2>3) & (Day.feast.exists()) ) <= 1:
                    db.update({'option': 1},(Day.id==dayID) & (Day.lg2<4))
                    db.update({'option': 2},(Day.id==dayID) & (Day.lg2>3) & (Day.feast.exists()))
                    day += timedelta(days=1)
                    continue
            
            
            season = rst[0]['season'] if 'season' in rst[0] else ''
            if any(ss in season.lower() for ss in ['lent','advent']):
                tb = CT(theme=VI)
            elif any(ss in season.lower() for ss in ['christmas','easter']):
                tb = CT(theme=WH)
            else:
                tb = CT(theme=GR)
                #tb = PT()

            names = ["","season","id","lg","feast","title","subtitle","comments"]
            tb.field_names = names
            
            for i,row in enumerate(rst):
                db.update({'option': 0},Day.id == row['id'])
                r = [f"{i+1}"]
                for v in names[1:]:
                    if v in row:
                        if any(pos in row[v].lower() for pos in ['sunday','lent','solemnity','feast','ash','octave']):
                            r.append(f'\033[1m{row[v]}\033[0m')
                        else:
                            r.append(row[v])
                    else:
                        if v == 'season':
                            r.append(season)
                        else:
                            r.append("")
                
                if not r[1:] in [tbrow[1:] for tbrow in tb.rows]:
                    tb.add_row(r)
                
            
            print(tb)

            option = input("Choose value: ")
            options = [int(v)-1 for v in option.split("-")]

            for i,opt in enumerate(options):
                db.update({'option': i + 1},doc_ids=[rst[opt].doc_id])
        elif rst:
            db.update({'option': 1}, Day.id == rst[0]['id'])

        if one_day:
            break

        day += timedelta(days=1)

    db.all()
    db.close()

