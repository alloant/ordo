#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess

from prettytable import PrettyTable as PT
from datetime import date

from src.scrap_ordo import scrapOrdo
from src.scrap_readings import scrapReadingsYear

from src.ordo import addFeasts, prepareOrdo, setVotives
from src.print import print_ordo, json_to_adoc, final_json

tb = PT()

tb.add_row([1,"Scrap ordo"])
tb.add_row([2,"Add feasts and comments in scrap ordo"])
tb.add_row([3,"Prepare ordo"])
tb.add_row([4,"Modify day"])
tb.add_row([5,"Set votives"])
tb.add_row([6,"Final json"])
tb.add_row([7,"Export to adoc and csv"])
tb.add_row([8,"Convert adoc to pdf"])
tb.add_row([9,"Scrap readings"])

print(tb)

option = input("Option: ")

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
        print_ordo(year)
        json_to_adoc(year)
    case '8':
        command = ['asciidoctor-pdf','-a','optimize','-a','media=prepress','-a','pdf-themesdir=resources/themes','-a','pdf-fontsdir=resources/fonts','-a','pdf-theme=ordoa6',f'rst/{year}/ordo.adoc','-o',f'rst/{year}/ordo.pdf']

        # Execute the command
        result = subprocess.run(command, capture_output=True, text=True)

        # Print the output and error (if any)
        print("Output:")
        print(result.stdout)
        print("Error:")
        print(result.stderr)
    case '9':
        scrapReadingsYear(year)

