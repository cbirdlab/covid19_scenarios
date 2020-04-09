import os, sys
import csv
import json
import numpy as np
import re
from time import strptime

from collections import defaultdict
from datetime import datetime
from .utils import store_data, stoi

# ------------------------------------------------------------------------
# Globals
counties = {
    "007" : "aransas",
    "025" : "bee",
    "047" : "brooks",
    "131" : "duval",
    "249" : "jim wells",
    "261" : "kenedy",
    "273" : "kleberg",
    "297" : "live oak",
    "355" : "nueces",
    "311" : "nueces",
    "355" : "mcmullen",
    "391" : "refugio",
    "409" : "san patricio",
}

DIR = "/home/ekrell/Downloads/COVID19/Case Data"
# Cases, deaths, recoveries
FILE_CASES = "texas_confirmed_cases_cumulative_new_Audrey.csv"
# Population data by age group
FILE_POP = ""
LOC = "Texas A&M University - Corpus Christi"
year = "2020"
offset = 2
cols = ['time', 'cases', 'deaths', 'hospitalized', 'icu', 'recovered']

# ------------------------------------------------------------------------
# Functions

# ------------------------------------------------------------------------
# Main point of entry
def parse():
    # Access files
    dfCasesFile = DIR + "/" + FILE_CASES + ".4"     # ! Cases starts at earlier date
    dfDeathsFile = DIR + "/" + FILE_CASES + ".1"
    dfRecoveredFile = DIR + "/" + FILE_CASES + ".3"

    # Init output data
    regions = defaultdict(list)
    nrows = 0
    dates = []

    # Use csv columns to get a list of all dates (equals number of rows)
    with open(dfCasesFile, newline='') as csvfile:
        rdr = csv.reader(csvfile, delimiter=',', quotechar='"')
        hdr = next(rdr)
        nrows = len(hdr[6:])
        for col in hdr[6:]:
            md = list(re.findall(r'(\w+?)(\d+)', col.split('_')[1])[0])
            md[0] = md[0].lower()[0:3]
            md[0] = strptime(md[0],'%b').tm_mon
            dates.append("{}-{:02}-{:02}".format(year, md[0], int(md[1])))

    cases = np.zeros(nrows)
    deaths = np.zeros(nrows)
    hospitals = np.zeros(nrows)
    icus = np.zeros(nrows)
    recovered = np.zeros(nrows)

    # Aggregate cases for all counties of interest
    with open(dfCasesFile, newline='') as csvfile:
        rdr = csv.reader(csvfile, delimiter=',', quotechar='"')
        hdr = next(rdr)
        for row in rdr:
            for c in counties.values():
                if row[1].lower() == c:
                    irow = [(int(x) if x else 0) for x in row[6:]]
                    cases = cases + irow

    # Aggregate deaths for all counties of interest
    dayOffset = 0
    with open(dfDeathsFile, newline='') as csvfile:
        rdr = csv.reader(csvfile, delimiter=',', quotechar='"')
        hdr = next(rdr)
        for row in rdr:
            for c in counties.values():
                if row[1].lower() == c:
                    irow = [(int(x) if x else 0) for x in row[6:]]
                    deaths[offset:] = deaths[offset:] + irow

    # Aggregate recoveries for all counties of interest
    dayOffset = 0
    with open(dfRecoveredFile, newline='') as csvfile:
        rdr = csv.reader(csvfile, delimiter=',', quotechar='"')
        hdr = next(rdr)
        for row in rdr:
            for c in counties.values():
                if row[1].lower() == c:
                    irow = [(int(x) if x else 0) for x in row[6:]]
                    recovered[offset:] = recovered[offset:] + irow


    # Combine into table
    for r in range(len(dates)):
        regions["USA-CoastalBend"].append([dates[r], int(cases[r]), int(deaths[r]), None, None, int(recovered[r])])

    #print (regions)

    store_data(regions, 'unitedstates_texas_coastalbend', cols)


if __name__ == '__main__':
    parse()

