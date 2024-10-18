#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import os

from prettytable import PrettyTable as PT
from datetime import date

from src.scrap_ordo import scrapOrdo
from src.scrap_readings import scrapReadingsYear

from src.ordo import addFeasts, prepareOrdo, setVotives, choose_ep
from src.print import json_to_csv, json_to_adoc, final_json


while True:
    #os.system('clear')
    tb = PT()

    tb.add_row([1,"Scrap ordo"])
    tb.add_row([2,"Add feasts and comments in scrap ordo"])
    tb.add_row([3,"Prepare ordo"])
    tb.add_row([4,"Modify day"])
    tb.add_row([5,"Set votives"])
    tb.add_row([6,"Final json"])
    tb.add_row([7,"Select ep"])
    tb.add_row([8,"Export to adoc and csv"])
    tb.add_row([9,"Convert adoc to pdf"])
    tb.add_row([10,"Scrap readings"])
    tb.add_row([11,"Exit"])

    print(tb)

    option = input("Option: ")
    
    if option != '10':
        year = int(input(f'Enter year ({date.today().year + 1}): ').strip() or date.today().year + 1)

    match option:
        case '1':
            scrapOrdo(year)
        case '2':
            addFeasts(year)
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
            final_json(year)
        case '7':
            choose_ep(year)
        case '8':
            json_to_csv(year)
            json_to_adoc(year)
        case '9':
            print("Choose size a5 or a6")
            theme = input("Size (a5): ")
            theme = 'a5' if not theme else theme

            command = ['asciidoctor-pdf','-a','optimize','-a','media=prepress','-a','pdf-themesdir=resources/themes','-a','pdf-fontsdir=resources/fonts','-a',f'pdf-theme=ordo{theme}',f'rst/{year}/ordo.adoc','-o',f'rst/{year}/ordo.pdf']

            # Execute the command
            result = subprocess.run(command, capture_output=True, text=True)

            # Print the output and error (if any)
            print("Output:")
            print(result.stdout)
            print("Error:")
            print(result.stderr)
        case '10':
            scrapReadingsYear(year)
        case '11':
            break

