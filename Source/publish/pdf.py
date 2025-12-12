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

def get_color(day):
    if 'Holy Saturday' in day['title']:
        return ''

    match day['color']:
        case 'R':
            return '<span class="color-mass text-danger big me-1">R</span>'
        case 'G':
            return '<span class="color-mass text-success big me-1">G</span>'
        case 'V':
            return '<span class="color-mass big me-1" style="color: #9400D3;">V</span>'
        case 'W':
            return '<span class="color-mass big me-1" style="color: #777777;">W</span>'

def get_just_color(day):
    match day['color']:
        case 'R':
            return "#C82333"
        case 'G':
            return "#155724"
        case 'V':
            return "#6F42C1"
        case 'W':
            return "#FFC300"
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
            font = "#000000"
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
                font = "#000000"
            else:
                dark = "#343A40"
                medium = "#6C757D"
                light = "#D3D3D3"
                font = "#000000"

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
    db = TinyDB(f'Results/{year}/ordo.json', indent=4)
    with open(f'Results/{year}/ordo.html','w') as file:
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
                body.append(BS(f'<h2 class="m-4">{dt.strftime("%B")}</h2>','html.parser'))
            
            
            if day['lit_grade'] == 'Solemnity':
                grade = '-sol'
            elif dt.weekday() == 6:
                grade = '-sun'
            elif day['lit_grade'] == 'Feast':
                grade = '-fea'
            else:
                grade = ''

                        
            card = f"""
            <div class="mycard rounded m-2" style="border: 1px solid {get_just_color(day)};">
                <div class="row p-0 m-0 border-bottom">
                    <div class="col-2 border-end d-flex align-items-center justify-content-center" {get_style(day,dt,'date')}>
                            <span class="text-center small p-0 m-0">{dt.strftime("%a")} {dt.strftime("%d")}</span>
                    </div>
                    
                    <div class="col-10 d-flex flex-column align-items-center justify-content-center" {get_style(day,dt,'title')}>
                        <span class="text-center">{get(day,"title")}</span>
                        {get(day,"subtitle")}
                    </div>
                </div>

                <div class="row p-0 m-0">
                    <div class="col-2">
                        <div class="row p-0 m-0">
                            <span class="text-center small">{get(day,"feast")} {flowers(day,dt)}</span>
                        </div>
                    </div>

                    <div class="col-10 d-flex flex-column align-items-center justify-content-center">
                        <div class="row small m-0 p-0 text-center">
                            <span>{get_color(day)} <span>{get(day,"mass")}</span><span class="ep small" style="white-space: nowrap;">{get(day,"ep")}</span></span>
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
        elif key == 'subtitle':
            if day["subtitle"]:
                return f'<span class="text-center small" style="color: #333333;">({day["subtitle"]})</span>'
            else:
                return ''

        return day[key]
    else:
        return ""

def add_comma(text):
    if text:
        return ','

    return ''

def html_template(year):
    return f"""

<html>

<head>
  <meta charset="utf-8">
  <title>Ordo Delhi {year}</title>
  <link href="../../Resources/bootstrap.min.css" rel="stylesheet">
  <link href="../../Resources/style.css" rel="stylesheet">
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
