#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import os

from prettytable import PrettyTable as PT
from datetime import date

from src.scrap_ordo import scrapOrdo
from src.scrap_readings import scrapReadingsYear

from src.ordo import addFeasts, prepareOrdo, setVotives, choose_ep
from src.print import json_to_html, json_to_csv, json_to_adoc, final_json


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
            scrapOrdo(year)
            addFeasts(year)
            input('Press any key to continue')
        case '2':
            prepareOrdo(year)
        case '3':
            day = input('Enter day (ddmm): ')
            if len(day) == 4 and day.isdigit():
                print(year,day[:2],day[2:])
                prepareOrdo(year,date(year,int(day[:2]),int(day[2:])))
        case '4':
            setVotives(year)
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
            """
            print("Choose size a5 or a6")
            theme = input("Size (a6): ")
            theme ='a6' if not theme else theme

            command = ['asciidoctor-pdf','-a','optimize','-a','media=prepress','-a','pdf-themesdir=resources/themes','-a','pdf-fontsdir=resources/fonts','-a',f'pdf-theme=ordo{theme}',f'rst/{year}/ordo.adoc','-o',f'rst/{year}/ordo.pdf']
            """
            command = ['weasyprint',f'rst/{year}/ordo.html',f'rst/{year}/ordo.pdf']
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

