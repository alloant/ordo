#!/bin/python

import os
from bs4 import BeautifulSoup
import requests
from tinydb import TinyDB
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

season = ""
did = 0
week = "I"
lg = ""
color = ""
title = ""

def scrapRow(row):
    global season,did,week,lg,color,title
    #print('###')

    if 'class' in row.attrs:
        if 'tbhd' in row['class']:
            return ""
    
    if row.find(class_="season"):
        season = row.text
        return ""

    if 'id' in row.attrs: # Starting the day
        did = row['id']
    lg = ""
    is_row = False
    for cell in row:
        #print(cell)
        for ele in cell:
            if isinstance(ele,str):
                week = ele
            else:
                try:
                    lg = ele['title']
                    continue
                except:
                    pass
                
                if 'class' in ele.attrs:
                    if ele.attrs['class'] == ["indent"]:
                        is_row = True
                        title = ""
                        for sp in ele:
                            if sp.text == "":
                                color = sp['class'][0]
                                color = color[5:]
                            else:
                                title += sp.text
                                try:
                                    lg2 = int(sp['class'][0][5:])
                                except:
                                    pass
    
    if is_row:
        return {'season':season.strip(),'id':did,'week':week.strip(),'lg':lg.strip(),'lg2':lg2,'color':color.strip(),'title':title.strip()}
    else:
        return ""
    

def scrapOrdo(year):
    url = f"http://www.gcatholic.org/calendar/{year}/IN-en.htm" 
    print("web:",url)

    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    tables = soup.select('table')
    ordo = tables[2]
    try:
        os.mkdir(f'rst/{year}')
    except:
        print(f'rst/{year} already there')
    db = TinyDB(f'rst/{year}/scrap.json', storage=CachingMiddleware(JSONStorage))
    cont = 0
    for row in ordo:
        dt = scrapRow(row)
        if dt:
            db.insert(dt)
            #print(dt)
            cont += 1

    db.close()
        

