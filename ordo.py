#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import os

from prettytable import PrettyTable as PT
from datetime import date

from Source.scrap import fetch_ordo, scrapReadingsYear
from Source.prepare import annotate_ordo, prepare_ordo, choose_votives, choose_ep, final_json
from Source.publish import json_to_html, json_to_csv


while True:
    os.system('clear')
    tb = PT()

    tb.add_row([1,"Scrap ordo"])
    tb.add_row([2,"Prepare ordo"])
    tb.add_row([3,"Modify day"])
    tb.add_row([4,"Set votives"])
    tb.add_row([5,"Add comments"])
    tb.add_row([6,"Select ep"])
    tb.add_row([7,"Export hmtl and csv"])
    tb.add_row([8,"Convert to pdf"])
    tb.add_row([9,"Scrap readings"])
    tb.add_row([0,"Exit"])

    print(tb)

    option = input("Option: ")
    
    if option != '11':
        year = int(input(f'Enter year ({date.today().year + 1}): ').strip() or date.today().year + 1)

    match option:
        case '1':
            fetch_ordo(year)
            annotate_ordo(year)
            input('Press any key to continue')
        case '2':
            prepare_ordo(year)
        case '3':
            day = input('Enter day (ddmm): ')
            if len(day) == 4 and day.isdigit():
                print(year,day[:2],day[2:])
                prepare_ordo(year,date(year,int(day[:2]),int(day[2:])))
        case '4':
            choose_votives(year)
        case '5':
            final_json(year)
            input('Press any key to continue')
        case '6':
            choose_ep(year)
        case '7':
            json_to_csv(year)
            json_to_html(year)
            #json_to_adoc(year)
            input('Press any key to continue')
        case '8':
            command = ['weasyprint',f'Results/{year}/ordo.html',f'Results/{year}/ordo.pdf']
            # Execute the command
            result = subprocess.run(command, capture_output=True, text=True)

            # Print the output and error (if any)
            print("Output:")
            print(result.stdout)
            print("Error:")
            print(result.stderr)
            input('Press any key to continue')
        case '9':
            scrapReadingsYear(year)
            input('Press any key to continue')
        case '0':
            break
        case _:
            break

