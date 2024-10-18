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
import re
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


def addFeasts(year):
    dbFeasts = TinyDB(f'rst/data/calendar.json')
    path = f'rst/{year}/scrap_feasts.json'
    if not exists(path):
        shutil.copy(f'rst/{year}/scrap.json',path)
    db = TinyDB(f'rst/{year}/scrap_feasts.json')

    # Specify the keys you want to keep
    keys_to_filter = ['season', 'week']
    keys_to_add = ['feast','subtitle', 'comments','color','mass','ep']

    for feast in dbFeasts.table('season').all():
        # Create a new dictionary with only the specified keys
        filter_dict = {key: feast[key] for key in keys_to_filter if key in feast}
        add_dict = {key: feast[key] for key in keys_to_add if key in feast}
        rst = db.update(add_dict,Query().fragment(filter_dict))

        if not rst:
            print(f'Did not find {feast}')

    # Specify the keys you want to keep
    keys_to_filter = ['id', 'title']

    for feast in dbFeasts.table('fixed').all():
        # Create a new dictionary with only the specified keys
        filter_dict = {key: feast[key] for key in keys_to_filter if key in feast}
        add_dict = {key: feast[key] for key in keys_to_add if key in feast}
        rst = db.update(add_dict,Query().fragment(filter_dict))

        if not rst:
            db.insert(dict(feast))

    for feast in dbFeasts.table('move').all():
        add_dict = {key: feast[key] for key in keys_to_add if key in feast}
        rst = db.update(add_dict,Query().title == feast['title'])

        if not rst:
            print(f'Did not find {feast}')

    for sunday in db.search(Query().title.search('Sunday', flags=re.IGNORECASE)):
        if not 'feast' in sunday or 'C' < sunday['feast']:
            db.update({'feast': 'C'},doc_ids=[sunday.doc_id])

    # St. Cyril to 13 Feb
    title = "Saint Cyril, monk, and Saint Methodius, bishop"
    if not db.update({'id': '0213'},Query().title == title):
        print(f'Cannot find {title}')

    # St. Athanaious to 4 or 5 May
    title = "Saint Athanasius, bishop and doctor of the Church"
    nid = '0504' if not db.search((Query().id=='0504') & (Query().title.search('Sunday'))) else '0505'
    if not db.update({'id': nid},Query().title == title):
        print('Cannot find {title}')


    title = "Saint Severino, martyr"
    if db.search((Query().id=='1108') & (Query().title.search('Sunday'))):
        if not db.update({'id': '1107'},Query().title == title):
            print('Cannot find {title}')


    title = "The Most Holy Trinity"
    rst = db.search(Query().title == title)
    if rst:
        htid = int(rst[0]['id'])
        doc_ids = [f'0000{htid-2}'[-4:],f'0000{htid-1}'[-4:],f'0000{htid}'[-4:]]
        db.update({'comments': lambda x: x + (',' if x else '') + f' Trisagium Angelicum'},doc_ids=doc_ids)
    
    db.close()

def setVotives(year):
    path = f'rst/{year}/votives.json'
    if not exists(path):
        shutil.copy('rst/data/votives.json',path)
    dbVot = TinyDB(path)
    Vot = Query()
    
    path = f'rst/{year}/scrap_feasts_others_votives.json'
    if not exists(path):
        shutil.copy(f'rst/{year}/scrap_feasts_others.json',path)
    db = TinyDB(path)
    Day = Query()

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
            cont = vt['count']
        else:
            dbVot.update({'count': 1,'last':row_day['id']},doc_ids=[vt.doc_id])
            count = 1
        
        if 'options' in vt:
            option = vt['options'].split(',')[count % len(options)].upper()
            db.update({'mass': f"vt['mass']} (option {option})",doc_ids=[row_day.doc_id])
        else:
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


def addOthers(year):
    dbScrap = TinyDB(f'rst/{year}/scrap_feasts.json')
    dbOther = TinyDB(f'rst/data/other.json')
    db = TinyDB(f'rst/{year}/scrap_feasts_others.json')
    
    Day = Query()

    for row in dbScrap.all() + dbOther.table('fixed').all() + dbOther.table('move').all():
        db.insert(dict(row))

    db.close()

def prepareOrdo(year, one_day = None):
    path = f'rst/{year}/scrap_feasts_others.json'
    if not exists(path):
        addOthers(year)
    
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
                
            
            os.system('clear')
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


def get_mondays(year):
    # Start from the first day of the year
    start_date = datetime(year, 1, 1)
    
    # Find the first Monday of the year
    if start_date.weekday() != 0:  # 0 is Monday
        start_date += timedelta(days=(7 - start_date.weekday()))
    
    # Generate a list of all Mondays in the year
    mondays = [datetime(year,1,1)]
    while start_date.year == year:
        mondays.append(start_date.date())
        start_date += timedelta(weeks=1)
    mondays += [datetime(year,12,31)]
    
    return mondays

def choose_ep(year):
    path = f'rst/{year}/ordo.json'
    if not exists(path):
        shutil.copy(f'rst/{year}/ordo_without_ep.json',path)

    db = TinyDB(path)
    Day = Query()

    mondays = get_mondays(year)
    headers = ["date","feast","title","lg","mass","ep"]
    for i,start in enumerate(mondays):
        if i == len(mondays):
            break
        st = start.strftime('%Y/%m/%d')
        end = mondays[i+1].strftime('%Y/%m/%d')

        rst = db.search( (Day.date >= st) & (Day.date < end) )
        tb = CT(theme=WH)
        tb.field_names = headers
        ep_filled = True
        for row in rst:
            tb.add_row([row[key] if key in row else '' for key in headers],divider=True)
            if not 'ep' in row or row['ep'] == '':
                ep_filled = False

        if ep_filled:
            continue
        
        print(tb)
        eps = input("Choose ep: ")

        while len(eps) != len(rst):
            eps = input("Put right number of ep: ")

        for i,row in enumerate(rst):
            db.update({'ep': eps[i]},Day.date == row['date'])

    db.close()
