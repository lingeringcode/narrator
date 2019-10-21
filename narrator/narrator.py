# -*- coding: utf-8 -*-
#!/usr/bin/python3

# Narrator: Visualizer for tweet data
# by Chris Lindgren <chris.a.lindgren@gmail.com>
# Distributed under the BSD 3-clause license.
# See LICENSE.txt or http://opensource.org/licenses/BSD-3-Clause for details.

# WHAT IS IT?
# A set of functions that process and create regular sum and temporal charts to help refine broader narrative of the data set(s).
# It functions only with Python 3.x and is not backwards-compatible.

# Warning: narrator performs very little custom error-handling, so make sure your inputs are formatted properly! If you have questions, please let me know via email.
from os import listdir
from os.path import isfile, join
import arrow
import ast
import csv
import pandas as pd
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt
import functools
import operator
import re
import emoji
import string

'''
    See README.md for an overview and comments for extended explanation.
'''
class topperObject:
    '''an object class with attributes that store desired top X samples from the corpus'''
    def __init__(self, top_x_tweets=None, top_x_hashtags=None, top_x_tweeters=None,
                top_x_targets=None, top_x_topics=None, top_x_urls=None, top_x_rts=None,
                period_dates=None):
        self.top_x_hashtags = top_x_hashtags
        self.top_x_tweeters = top_x_tweeters
        self.top_x_tweets = top_x_tweets
        self.top_x_topics = top_x_topics
        self.top_x_urls = top_x_urls
        self.top_x_rts = top_x_rts
        self.period_dates = period_dates

##################################################################

## General Functions

##################################################################

'''
    Initialize topperObject
'''
def initializeTO():
    return topperObject()

'''
    period_maker: Helper function for period_dates_writer.
'''
def period_maker(bd, ed):
    # Make period date-range
    begin_date = arrow.get(bd, 'YYYY-MM-DD')
    end_date = arrow.get(ed, 'YYYY-MM-DD')
    date_range = arrow.Arrow.range('day', begin_date, end_date)
    return date_range

'''
    period_writer():  Accepts list of lists of period date information
    and returns a Dict of per Period dates for temporal analyses.
        - Args:
            - periodObj: Optional first argument periodObject, Default is None
            - 'ranges': Hierarchical list in following structure:
                ranges = [
                    ['p1', ['2018-01-01', '2018-03-30']],
                    ['p2', ['2018-04-01', '2018-06-12']],
                    ...
                ]
'''
def period_dates_writer(topperObject=None, **kwargs):
    period_dict = {}
    for r in kwargs['ranges']:
        period_list = []
        p_dates = period_maker(r[1][0], r[1][1]) # send period date range
        for d in p_dates:
            # Append returned date range to period list
            period_list.append( str(d.format('YYYY-MM-DD')) )
        period_dict.update({r[0]: period_list})

    if topperObject == None:
        return period_dict
    else:
        topperObject.period_dates = period_dict
        return topperObject

##################################################################

## SUMMARIZER FUNCTIONS

##################################################################
'''
    get_sample_size: Helper function for summarizer functions. If sample=True,
    then sample sent here and returned to the summarizer for output.
    - Args:
        - sort_check= Boolean. If True, sort the corpus. If False, leave in temporal order.
        - df= DataFrame of corpus.
        - ss= Integer of sample size to output.
        - sample_check= Boolean. If True, use ss value. If False, use full corpus.
    - Returns DataFrame to summarizer function.
'''
def get_sample_size(sort_check, df, ss, sample_check):
    # Check if to be sorted or not
    if sort_check == True:
        sorted_df = sorted(df, key=lambda x: x[1], reverse=True)
        print('Top 10:\n\n', sorted_df[:10])
        # Check if delimited sample size
        if sample_check == True:
            top_dates = sorted_df[:ss]
            return top_dates
        elif sample_check == False:
            return sorted_df
    elif sort_check == False:
        print('First 10:\n\n', df[:10])
        # Check if delimited sample size
        if sample_check == True:
            first_dates = df[:ss]
            return first_dates
        elif sample_check == False:
            return df

'''
    hashtag_summarizer: Counts hashtag use and optionally as temporally
    distributed.
    - Args:
        - df_corpus= DataFrame of tweet corpus
        - hash_col= String value of the DataFrame column name for hashtags.
        - date_col= String value of the DataFrame column name for the dates in xx-xx-xxxx format.
        - date_counter= Boolean. If True, build sums per day. If False, overall sum.
        - sorted= Boolean. If True, sort sums per day. If False, maintain temporal order.
        - sort_type= Boolean. If True, descending order. If False, ascending order.
'''
def hashtag_summarizer(**kwargs):
    # 1. Clean data
    clean_hash_data = kwargs['df_corpus'][(kwargs['df_corpus'][kwargs['hash_col']].isnull() == False)]
    clean_hash_data_filtered = clean_hash_data[clean_hash_data[kwargs['hash_col']].str.contains('#')]
    clean_hash_data_filtered = clean_hash_data.reset_index()

    # 2. Count and sort in descending order
    cleaned_hashtags = []
    # Option 2.1 - Count per Hashtag, across entire corpus
    if kwargs['date_counter'] == False:
        for h in list(clean_hash_data_filtered[kwargs['hash_col']]):
            h = ast.literal_eval(h)
            if type(h) is not float:
                h = [n.strip() for n in h]
                if len(h) > 1 and type(h) is not float:
                    for i in h:
                        cleaned_hashtags.append(i)
                elif len(h) == 1 and type(h) is not float:
                    cleaned_hashtags.append(h[0]) 
        hashtag_totals = list(Counter(cleaned_hashtags).items())
        
        # Get sample
        top_x = get_sample_size(
            sort_check=kwargs['sort_check'],
            df=hashtag_totals,
            ss=kwargs['sample_size'],
            sample_check=kwargs['sample_check'])
        return top_x
    # Option 2.2 - Count hashtags per Day, across entire corpus
    elif kwargs['date_counter'] == True:
        # Isolate columns of interest: Dates (xx-xx-xxxx) and 
        df_hash_data = clean_hash_data_filtered[[kwargs['date_col'], kwargs['hash_col']]]
        hashtags_and_dates = []
        for h in df_hash_data.values.tolist():
            ht = ast.literal_eval(h[1])
            if type(ht) is not float:
                ht = [n.strip() for n in ht]
                if len(ht) > 1:
                    for i in ht:
                        hashtags_and_dates.append( (i, h[0]) ) #append hashtag and date
                elif len(ht) == 1:
                    hashtags_and_dates.append( (ht[0], h[0]) ) #append hashtag and date
        
        hashtag_date_totals = list(Counter(hashtags_and_dates).items())

        # Get sample
        top_date_x = get_sample_size(
            sort_check=kwargs['sort_check'],
            df=hashtag_date_totals,
            ss=kwargs['sample_size'],
            sample_check=kwargs['sample_check'])
        return top_date_x

##################################################################

## PLOTTER FUNCTIONS

##################################################################
'''
    bar_plotter: Plot the desired column sums as a bar chart
    -- Args:
        ax=None # Resets the chart
        counter = List of tuples returned from match_maker(),
        path = String of desired path to directory,
        output = String value of desired file name (.png)
    - Returns: Nothing

'''
def bar_plotter(**kwargs):
    if kwargs['ax'] is None:
        fig = plt.figure()
        kwargs['ax'] = fig.add_subplot(111)

    frequencies = []
    names = []

    for c in kwargs['counter']:
        frequencies.append(c[1])
        names.append(c[0])

    N = len(names)
    x_coordinates = np.arange(len(kwargs['counter']))
    kwargs['ax'].bar(x_coordinates, frequencies, align='center')

    kwargs['ax'].xaxis.set_major_locator(plt.FixedLocator(x_coordinates))
    kwargs['ax'].xaxis.set_major_formatter(plt.FixedFormatter(names))

    plt.xticks(range(N)) # add loads of ticks
    plt.xticks(rotation='vertical')

    plt.gca().margins(x=0)
    plt.gcf().canvas.draw()
    tl = plt.gca().get_xticklabels()
    maxsize = max([t.get_window_extent().width for t in tl])
    m = kwargs['margin'] # inch margin
    s = maxsize/plt.gcf().dpi*N+2*m
    margin = m/plt.gcf().get_size_inches()[0]

    plt.gcf().subplots_adjust(left=margin, right=1.-margin)
    plt.gcf().set_size_inches(s, plt.gcf().get_size_inches()[1])

    # Tweak spacing to prevent clipping of tick-labels
    plt.subplots_adjust(bottom=-0.15)
    plt.savefig(join(kwargs['path'], kwargs['output']))
    print('File ', kwargs['output'], ' saved to ', kwargs['path'])
    plt.show()

'''
    temporal_bar_plotter: Plot the desired column sums as a temporal bar chart
    -- Args:
        ax=None # Resets the chart
        counter = List of tuples returned from match_maker()
        title= String. Title of the chart.
        margin= Float in inches for adjusting margin
        subplot_adj_bottom= Float in inches for adjusting bottom margin issues
        path = String of desired path to directory
        output = String value of desired file name (.png)
    - Returns: Nothing.
'''
def temporal_bar_plotter(**kwargs):
    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111)
    
    frequencies = []
    names = []
    dates = kwargs['date_range']

    for c in kwargs['counter']:
        for d in dates:
            if  d == c[0]:
                frequencies.append(c[1])
                names.append( c[0]+':  '+str(c[1]) )
                
    N = len(names)
    x_coordinates = np.arange(N) #changed from counter
    ax.bar(x_coordinates, frequencies, align='center')

    ax.xaxis.set_major_locator(plt.FixedLocator(x_coordinates))
    ax.xaxis.set_major_formatter(plt.FixedFormatter(names))
    
    plt.xticks(range(N)) # add loads of ticks
    plt.xticks(rotation='vertical')

    plt.gca().margins(x=0)
    plt.gcf().canvas.draw()
    tl = plt.gca().get_xticklabels()
    maxsize = max([t.get_window_extent().width for t in tl])
    m = kwargs['margin'] # inch margin
    s = maxsize/plt.gcf().dpi*N+2*m
    margin = m/plt.gcf().get_size_inches()[0]

    plt.gcf().subplots_adjust(left=margin, right=1.-margin)
    plt.gcf().set_size_inches(s, plt.gcf().get_size_inches()[1])
    
    # Tweak spacing to prevent clipping of tick-labels
    plt.title(kwargs['title'], fontdict=None, loc='center', pad=None)
    plt.subplots_adjust(bottom=kwargs['subplot_adj_bottom'])
    plt.savefig(join(kwargs['path'], kwargs['output']))
    print('File ', kwargs['output'], ' saved to ', kwargs['path'])
    plt.show()