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
import json

# Import ordinary least squares from statsmodels
import pandas as pd
import numpy as np

DATA_PATH = os.path.dirname(os.path.abspath(__file__))

#########################
#  SET TAX YEAR
TAX_YEAR = 2016
#########################


def load_trip_summary(file_list):
    """
    Takes the output csv from the Vancouver Translink
    Compass card account and returns the data in a dataframe.
    """
    # initialize a list for the card interactions
    card_action = []
    trip_dataframe = pd.DataFrame()

    # create a date list to avoid duplicate entries
    all_datetimes = []

    for file_path in file_list:
        with open(file_path, 'rU') as csvfile:
            # Note that the example csv was TAB DELIMITED
            compass_file = csv.reader(csvfile)
            for row in compass_file:
                # A proper implementation of checking the header format
                # will be needed.  This is a bad hack.
                if row[0] == 'DateTime':
                    headers = row
                else:
                    datetime = pd.to_datetime(row[0])
                    # avoid adding duplicate entries because Compass export
                    # date range doesn't work.  Also make sure only trips
                    # in the desired tax year are included.
                    extraneous_entries = ['Missing', 'Transfer']
                    if row[0] not in all_datetimes and datetime.year == TAX_YEAR:
                        all_datetimes += [row[0]]
                        # filter out missing taps and transfers as they
                        # are interested in just the tap in - tap out combo
                        # that makes up the one-way trip we're targeting.
                        excluded_entry = False
                        for e in extraneous_entries:
                            if e in row[2].split():
                                excluded_entry = True
                        if excluded_entry == False:
                            location = row[1]
                            transaction = row[2]
                            product = row[3]
                            amount = float(row[4])
                            card_action += [[datetime, location, transaction, product, amount]]

    return pd.DataFrame(card_action, columns=headers)


file_list = glob.glob(DATA_PATH + '/data/*.csv')
# load the discharge summary into a pandas dataframe
trips_df = load_trip_summary(file_list)

headers = trips_df.columns.values
# headers[0] should be datetime
trips_df = trips_df.sort_values(by='DateTime')

# according to CRA, to claim your Compass transit amount,
# your card must be used to make a minimum
# 32 one-way trips over a maximum 31 consecutive days
# http://www.cra-arc.gc.ca/tx/ndvdls/tpcs/ncm-tx/rtrn/cmpltng/ddctns/lns360-390/364/lgblty-eng.html

min_trips = 32
min_days = pd.Timedelta('31 days')

first_day = min(trips_df['DateTime'])
last_day = max(trips_df['DateTime'])

# create an array to track eligible one-way trips
eligible_trips = []

most_trips = 0

all_eligible_trips = pd.DataFrame()

for i in range(len(trips_df['DateTime'])):
    curr_date = trips_df.ix[i][0]
    end_date = pd.to_datetime(curr_date + min_days)

    # filter for all datetimes in the given 31-day period
    mask = (trips_df['DateTime'] > curr_date) & (trips_df['DateTime'] < end_date)
    date_slice = trips_df.loc[mask]

    # get an array of all the 'tap in' transactions, as these
    # represent a unique one-way trip
    tap_ins = [e for e in date_slice['Transaction'] if e.find('Tap in') != -1]
    #print('tap_ins = ', tap_ins)

    # track the highest number of trips in a 31-day period
    if len(tap_ins) > most_trips:
        most_trips = len(tap_ins)

    # if there are more than the minimum required trips
    # in the 31-day period, add the trips to the all_eligible_trips
    # dataframe
    if len(tap_ins) >= min_trips:
        start_day = min(date_slice['DateTime'])
        end_day = max(date_slice['DateTime'])

        # if one eligible period has been found
        # and we find another, check if the start date
        # of the latest eligible period falls within the
        # range already registered.  If so, add only the
        # additional dates (union, no duplicate entries).
        # If not, add the whole period,
        if not all_eligible_trips.empty:
            if start_day in all_eligible_trips['DateTime']:
                # merge the two dataframes
                all_eligible_trips = pd.merge(all_eligible_trips, date_slice, \
                    how='outer', on='DateTime')
        else:
            all_eligible_trips = date_slice

# Add up the transaction values in the resultant overall eligible
# trip period
total_transaction_value = abs(sum([v for v in all_eligible_trips['Amount']]))

print('eligible Compass Usage Period = ', min(all_eligible_trips['DateTime']), \
    ' to ', max(all_eligible_trips['DateTime']))
print('total transaction value = $', total_transaction_value )

