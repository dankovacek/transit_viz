import os
import sys
import glob
import csv
import time
import re
import math
import datetime
import scipy
import string
import re

# Import ordinary least squares from statsmodels
import statsmodels.api as sm
from statsmodels.formula.api import ols
import scipy.stats as stats
import matplotlib.pyplot as plt
from matplotlib import rcParams
import pandas as pd
import numpy as np

import bokeh
from bokeh.io import hplot, gridplot
from bokeh.layouts import gridplot
from bokeh.plotting import figure, output_file, show, ColumnDataSource
from bokeh.models import HoverTool, BoxSelectTool, ResetTool, SaveTool
from bokeh.models import BoxZoomTool, LassoSelectTool, BoxSelectTool, PanTool
from bokeh.models import ResizeTool, UndoTool, RedoTool, BoxAnnotation
from bokeh.models import DatetimeTickFormatter, Legend
from bokeh.charts import TimeSeries
from bokeh.palettes import Spectral6

DATA_PATH = os.path.dirname(os.path.abspath(__file__))

def load_trip_summary(f):
    """
    Takes the output csv from the Vancouver Translink
    Compass card account and returns the data in a dataframe.
    """
    file_path = DATA_PATH + '/' + f
    # initialize a list for the regional data rows
    q_msmts = []
    with open(file_path, 'rU') as csvfile:
        # Note that the example csv was TAB DELIMITED
        q_file = csv.reader(csvfile)
        for row in q_file:
            # A proper implementation of checking the header format
            # will be needed.  This is a temporary solution and a bad idea.
            if row[0] == 'DateTime':
                headers = [row[0], 'date_str', row[1], row[2], row[3], row[4]]
                #pressure_index = row.index('Stn Press (kPa)')
            else:
                datetime = pd.to_datetime(row[0])
                date_str = row[0]
                location = row[1].upper()
                location = location.replace('STREET', 'ST')
                location = location.replace(' ', '')[:-3]
                transaction = row[2]
                product = row[3]
                amount = float(row[4])

                q_msmts += [[datetime, date_str, location, transaction, product, amount]]

    return pd.DataFrame(q_msmts, columns=headers)


import xml.etree.ElementTree as etree

def parse_kml(f):
    """ Takes in as input the Translink stations kml file
    downloaded from the Vancouver Open Data Catalogue:
    http://data.vancouver.ca/datacatalogue/
    and returns the station name and coordinates in
    a pandas dataframe.  Note that only stations
    in the city limits are included."""

    tree = etree.parse(DATA_PATH + '/' + f)

    # retrieve header information from file
    # If the device setup changes, make adjustments to tags here.
    stations = []
    coords = []

    i = 0
    for elem in tree.iter():
        # remove the url prefix on the element tag
        tag = elem.tag.split('}')[-1]

        # we're only interested in the name and coordinates
        if tag == 'name':
            # a bunch of useless crap to try matching kml location format
            formatted_name = elem.text
            formatted_name = formatted_name.replace('.', '')
            formatted_name = formatted_name.replace('\\n', '')
            formatted_name = formatted_name.replace(' ', '').upper()
            stations += [formatted_name]#.split('-')
        elif tag == 'coordinates':
            lat_lon = elem.text.split(',')[:2]
            lat = lat_lon[0]
            lon = lat_lon[1]

    # create a new dataframe
    station_df = pd.DataFrame()

    # create column titles for the dataframe
    header = ['station_name', 'lat', 'lon']

    # add the station array to the dataframe
    # the first two entries are not stations, so eliminate them
    station_df[header[0]] = stations[2:]

    # add the coordinates array to the dataframe
    station_df[header[1]] = lat
    station_df[header[2]] = lon

    return pd.DataFrame(station_df, columns=header)



transit_history_file = 'compass_card_history.csv'
# load the discharge summary into a pandas dataframe
trips_df = load_trip_summary(transit_history_file)

# parse the kml file of translink stations within CoV limits
station_kml = 'rapid_transit_stations.kml'
stations_df = parse_kml(station_kml)

# output the station list with coordinates to csv
# and unfortunately manually correct the names to match
# the compass output names
filename = 'CoV_Translink_Stns_formatted'
filename += datetime.date.today().strftime("%Y%B%d") + '.csv'
stations_df.to_csv(filename)

# iterate through the trips and count numbers of trips
locations = {}
for e in trips_df['Location'].iteritems():
    if e[1] not in locations.keys():
        locations[e[1]] = 1
    else:
        locations[e[1]] += 1

# determine the total number of trips
total_trips = sum([locations[e] for e in locations.keys()])

normalized_trips = [(e, float(locations[e] / total_trips)) for e in locations.keys()]
print(total_trips, ' <<<---- total trips')
#print('normalized trips: ', normalized_trips)

#now put the renamed station csv back in order
station_list_file = 'CoV_Translink_Stations2017February21.csv'
stations = {}
with open(station_list_file, 'rU') as csvfile:
    for e in csvfile:
        temp_list = e.split(',')
        if temp_list[0] is not '':
            if temp_list[1] not in stations.keys():
                lat = temp_list[2][3:-1]
                lon = temp_list[3][2:-5]
                stations[temp_list[1]] = [float(lat), float(lon)]


