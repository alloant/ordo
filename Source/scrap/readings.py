#!/bin/python

from bs4 import BeautifulSoup
import requests
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
from datetime import date, timedelta
import re

def scrapReadings(day,url,keep_going = True):
    all_readings = []

    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    other = soup.find(class_="nested")

    if other and keep_going:
        all_readings = scrapReadings(day,other.a['href'],False)
    

    temp = soup.find(class_='b-lectionary')
    title = ""
    if temp:
        temp = temp.find('h2')
        if temp:
            title = str(temp.get_text(separator=" ")).strip()
            title = re.sub(' +', ' ', title)
            title = re.sub('\n','',title).split("  ")
            
    readings = soup.find_all(attrs={'class':'b-verse'})
    
    # Do something to get the title to see if it is the memory or the season
    for rd in readings:
        key = rd.find(class_='name').get_text(separator=" ")
        if not key:
            continue
        
        tp = rd.find(class_='address')
        tp1 = tp.get_text(separator=" ")
        if hasattr(tp,'a'):
            if tp.a:
                tp2 = tp.a['href']
            else:
                tp2 = ""
        else:
            tp2 = ""
        text = rd.find(class_='content-body').get_text(separator=" ")
        all_readings.append({'day':day,'title':title,'type':key.strip(),'num':tp1.strip(),'link':tp2.strip(),'text':text.strip(),'season':keep_going})
    
    return all_readings


def scrapReadingsYear(year):
    day = date(year,1,1)
    Day = Query()
    db = TinyDB(f'Results/{year}readings.json', storage=CachingMiddleware(JSONStorage), indent=4, sort_keys=True)

    while day.year == year:
        if db.count(Day.day==day.strftime("%m%d")) > 0:
            print(f"{day.strftime('%m%d')} is already done")
            day += timedelta(days=1) 
            continue
        url = f"https://bible.usccb.org/bible/readings/{day.strftime("%m%d")}24.cfm"
        try:
            db.insert_multiple(scrapReadings(day.strftime("%m%d"),url))
        except Exception as err:
            print(f'Could not insert {url}. {err}')
            break
        day += timedelta(days=1) 
    
    db.close()

def scrapGospel(target):
    if target.isdigit():
        day = date.today() + timedelta(days = int(target))
    else:
        tg = target.split("/")
        day = date(date.today().year,tg[1],tg[0])
        
    url = f"https://bible.usccb.org/bible/readings/{day.strftime("%m%d")}24.cfm"
    rst = scrapReadings(day.strftime("%m%d"),url)[-1]

    return f"{rst['title'][0]} - {rst['num']}: {rst['text']}"



