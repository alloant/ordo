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
    print(f'Adding comments from data/comments.json. Saving result in rst/{year}/ordo_without_ep.json')
    dbOrdo = TinyDB(f'rst/{year}/scrap_feasts_others_votives.json', indent=4)
    dbComments = TinyDB(f'rst/data/comments.json', indent=4)
    db = TinyDB(f'rst/{year}/ordo_without_ep.json', indent=4)
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


def json_to_csv(year):
    db = TinyDB(f'rst/{year}/ordo.json', indent=4)
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

def get_color(day):
    if 'Holy Saturday' in day['title']:
        return ''

    match day['color']:
        case 'R':
            return '<span class="color-mass text-danger small me-1">R</span>'
        case 'G':
            return '<span class="color-mass text-success small me-1">G</span>'
        case 'V':
            return '<span class="color-mass small me-1" style="color: #9400D3;">V</span>'
        case 'W':
            return '<span class="color-mass small me-1" style="color: #CCCCCC;">W</span>'

def get_just_color(day):
    match day['color']:
        case 'R':
            return "#C82333"
        case 'G':
            return "#155724"
        case 'V':
            return "#6F42C1"
        case 'W':
            if day['lit_grade'] in ['Solemnity','Feast'] or 'Easter Sunday' in day['title'] or 'Supper' in day['title']:
                return "#FFC300"

            return "#FFF9C4"

def get_style(day,dt,place):
    match day['color']:
        case 'R':
            dark = "#C82333"
            medium = "#FF4C4C"
            light = "#FFB3B3"
            font = "#FFFFFF"
        case 'G':
            dark = "#155724"
            medium = "#28A745"
            light = "#C3E6CB"
            font = "#FFFFFF"
        case 'V':
            dark = "#6F42C1"
            medium = "#8A63D2"
            light = "#EAB8F1"
            font = "#FFFFFF"
        case 'W':
            if day['lit_grade'] in ['Solemnity','Feast'] or 'Easter' in day['title'] or 'Supper' in day['title']:
                dark = "#FFD700"
                medium = "#FFC300"
                light = "#FFF9C4"
                font = "#FFFFFF"
            else:
                dark = "#343A40"
                medium = "#6C757D"
                light = "#D3D3D3"
                font = "#FFFFFF"



    if day['lit_grade'] == 'Solemnity' or dt.weekday() == 6 or 'Easter Sunday' in day['title'] or 'Supper' in day['title'] or 'Good Friday' in day['title']:
        if place == 'date':
            return f'style="background-color: {dark}; color: {font};"'
        elif place == 'title':
            return f'style="background-color: {medium}; color: {font};"'
        elif place == 'comments':
            return f'style="background-color: {light};"'
    elif day['lit_grade'] == 'Feast':
        if place == 'date':
            return f'style="background-color: {medium}; color: {font};"'
        elif place == 'title':
            return f'style="background-color: {light};"'


    return ''

def flowers(day,dt):
    if (dt.weekday() == 5 and not 'Holy Saturday' in day['title']) or 'feast' in day and day['feast'] < 'C' and day['feast'] or dt.month == 5:
        return '<span class="small" style="color: #E75480;">󰴈</span>'
    return ""


def json_to_html(year):
    db = TinyDB(f'rst/{year}/ordo.json', indent=4)
    with open(f'rst/{year}/ordo.html','w') as file:
        soup = BS(html_template(year),'html.parser')
        body = soup.find('body')
        body.clear()
        cover = f"""
        <div class="rounded" id="cover-page">
            <h1>Ordo Delhi {year}</h1>
            <h2>Cycle A - Year II</h2>
            <p class="date">January 1, {year}</p>
        </div>
        <div class="empty-page-placeholder"></div>
        """
        body.append(BS(cover,'html.parser'))
        
        ## Now we add the elements in the body
        current_month = 0
        for day in sorted(db.all(),key = lambda doc: doc.get('date')):
            dt = datetime.strptime(day['date'],"%Y/%m/%d")
            if current_month == 0 or current_month != dt.month:
                #if dt.month == 3:
                #    break
                if current_month > 0:
                    body.append(body_month)
                current_month = dt.month
                body_month = BS(f'<div class="container-flush"></div>','html.parser')
                cards_month = body_month.find('div')
                body.append(BS(f'<h2>{dt.strftime("%B")}</h2>','html.parser'))
            
            
            if day['lit_grade'] == 'Solemnity':
                grade = '-sol'
            elif dt.weekday() == 6:
                grade = '-sun'
            elif day['lit_grade'] == 'Feast':
                grade = '-fea'
            else:
                grade = ''

                        
            card = f"""
            <div class="mycard rounded m-2" style="border: 2px solid {get_just_color(day)};">
                
                <div class="row p-0 m-0 border-bottom">
                    <div class="col-1 border-end" {get_style(day,dt,'date')}>
                        <div class="row fw-bold p-0 m-0">
                            <span class="text-center p-0 m-0">{dt.strftime("%a")}</span>
                        </div>
                        <div class="row fw-bold p-0 m-0">
                            <span class="text-center p-0 m-0">{dt.strftime("%d")}</span>
                        </div>
                    </div>
                    
                    <div class="col-11 d-flex flex-column justify-content-center align-items-center gap-0" {get_style(day,dt,'title')}>
                        <p class="fw-bold text-center py-0 my-0">{get(day,"title")}</p>
                        <p class="small text-center py-0 my-0">{get(day,"subtitle")}</p>
                    </div>
                </div>

                <div class="row p-0 m-0">
                    <div class="col-1 d-flex flex-column justify-content-center align-items-center">
                        <span>{get(day,"feast")}</span>
                        {flowers(day,dt)}
                    </div>

                    <div class="col-11">
                        <div class="row m-0 p-0 text-center">
                            <div class="">
                                {get_color(day)}
                                <span>{get(day,"mass")}</span>
                                <span class="ep small" style="white-space: nowrap;">{get(day,"ep")}</span>
                            </div>
                        </div>
                    </div>
                </div>
            """

            if get(day,"comments") != "":
                card += f"""
                <div class="row p-0 m-0 border-top" {get_style(day,dt,'comments')}>
                    <div class="row m-0 p-0 text-center">
                        <span class="small">{get(day,"comments")}</span>
                    </div>
                </div>
                """
            
            card += """
            </div>
            """



            #body.append(BS(card,'html.parser'))
            cards_month.append(BS(card,'html.parser'))
        
        body.append(body_month)
        file.write(str(soup))

def get(day,key):
    if key in day:
        if key in ['mass','ep','color'] and 'Holy Saturday' in day['title']:
            return ""
        elif key == 'comments':
            exps = ['Si.Ex','So.Ex']
            rst = day[key]
            for exp in exps:
                if f", {exp}" in rst:
                    rst = f'<span class="rounded bg-warning" style="padding: 1px;">{exp}</span>, ' + rst.replace(f', {exp}','')
                elif f"{exp}, " in rst:
                    rst = f'<span class="rounded bg-warning" style="padding: 1px;">{exp}</span>, ' + rst.replace(f'{exp}, ','')    
                elif exp == rst:
                    rst = f'<span class="rounded bg-warning" style="padding: 1px;">{exp}</span>'
                elif exp in rst:
                    rst = f'<span class="rounded bg-warning" style="padding: 1px;">{exp}</span>, ' + rst.replace(exp,'')
            
            return rst
        elif key == 'ep':
            match day[key]:
                case '1':
                    return ', EP I'
                case '2':
                    return ', EP II'
                case '3':
                    return ', EP III'
                case '4':
                    return ', EP IV'

        return day[key]
    else:
        return ""

def add_comma(text):
    if text:
        return ','

    return ''
  
    #<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    #<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/bootstrap-icons.min.css">
    #<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

def html_template(year):
    return f"""

<html>

<head>
  <meta charset="utf-8">
  <title>Ordo Delhi {year}</title>
  <link href="../../resources/bootstrap.min.css" rel="stylesheet">
  <link href="../../resources/style.css" rel="stylesheet">
  <meta name="description" content="Ordo {year}">
</head>

<body>
  <header>
  </header>

    MARKER 

  <footer>
  </footer>

</body>

</html>
    """
