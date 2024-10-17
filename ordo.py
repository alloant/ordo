#!/usr/bin/env python
# -*- coding: utf-8 -*-

from prettytable import PrettyTable as PT
from datetime import date

from src.scrap_ordo import scrapOrdo
from src.scrap_readings import scrapReadingsYear

from src.ordo import prepareOrdo, setVotives
from src.print import print_ordo, to_adoc

tb = PT()

tb.add_row([1,"Scrap ordo"])
tb.add_row([2,"Scrap readings"])
tb.add_row([3,"Prepare ordo"])
tb.add_row([4,"Modify day"])
tb.add_row([5,"Set votives"])
tb.add_row([6,"Print ordo"])

print(tb)

option = input("Option: ")

year = int(input(f'Enter year ({date.today().year + 1}): ').strip() or date.today().year + 1)

match option:
    case '1':
        scrapOrdo(year)
    case '2':
        scrapReadingsYear(year)
    case '3':
        prepareOrdo(year)
    case '4':
        day = input('Enter day (ddmm): ')
        if len(day) == 4 and day.isdigit():
            print(year,day[:2],day[2:])
            prepareOrdo(year,date(year,int(day[:2]),int(day[2:])))
    case '5':
        setVotives(year)
    case '6':
        #print_ordo(year)
        to_adoc(year)
