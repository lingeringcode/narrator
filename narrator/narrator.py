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
import math

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
    date_range_writer: Takes beginning date and end date to write a range of those dates per Day as a List
    - Args:
        - bd= String. Beginning date in YYYY-MM-DD format
        - ed= String. Ending date in YYYY-MM-DD format
    - Returns List of arrow date objects for whatever needs.
'''
def date_range_writer(bd, ed):
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
        p_dates = date_range_writer(r[1][0], r[1][1]) # send period date range
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
    skeletor: Takes desired date range and list of keys to create a skeleton Dict before hydrating it with the sample values. Overall, this provides default 0 Int values for every keyword in the sample.
    - Args:
        - aggregate_level= String. Current options include:
            - 'day': per Day
            - 'period_day': Days per Period
            - 'period': per Period
        - date_range= 
            - If 'day' aggregate level, a List of per Day dates ```['2018-01-01', '2018-01-02', ...]```
            - If 'period' aggregate level, a Dict of periods with respective date Lists: ```{{'1': ['2018-01-01', '2018-01-02', ...]}}```
        - keys= List of keys for hydrating the Dict
    - Returns full Dict 'skeleton' with default 0 Integer values for the grouper() function
'''
def skeletor(**kwargs):
    dict_groups = {}
    # Write per Day Dict skeleton
    if kwargs['aggregate_level'] == 'day':
        for r in kwargs['date_range']:
            dict_groups.update({ r: {} })
            for h in kwargs['keys']:
                dict_groups[r].update({ h: 0})
    # Write Days per Period Dict skeleton
    elif kwargs['aggregate_level'] == 'period_day':
        for p in kwargs['date_range']:
            dict_groups.update({ p: {} })
            for day in kwargs['date_range'][p]:
                dict_groups[p].update({ day: {} })
                for h in kwargs['keys']:
                    dict_groups[p][day].update({h: 0 })
    # Write per Period Dict skeleton
    elif kwargs['aggregate_level'] == 'period':
        for p in kwargs['date_range']:
            dict_groups.update({ p: {} })
            for h in kwargs['keys']:
                dict_groups[p].update({h: 0 })
    return dict_groups

'''
    get_sample_size: Helper function for summarizer functions. If sample=True,
    then sample sent here and returned to the summarizer for output.
    - Args:
        - sort_check= Boolean. If True, sort the corpus.
        - sort_date_check= Boolean. If True, sort corpus based on dates.
        - counted_list= List. Tallies from corpus.
        - ss= Integer of sample size to output.
        - sample_check= Boolean. If True, use ss value. If False, use full corpus.
    - Returns DataFrame to summarizer function.
'''
def get_sample_size(sort_check, sort_date_check, sort_type, counted_list, ss, sample_check):
    # Check if to be sorted or not
    if sort_check == True:
        sorted_df = sorted(counted_list, key=lambda x: x[1], reverse=True)

        # Check if delimited sample size
        if sample_check == True:
            top_dates = sorted_df[:ss]
            return top_dates
        elif sample_check == False:
            return sorted_df
    elif sort_date_check == True:
        if sort_type == True:
            sorted_df = sorted(counted_list, key=lambda x: x[0], reverse=True) #descending
        elif sort_type == False:
            sorted_df = sorted(counted_list, key=lambda x: x[0], reverse=False) #ascending
        
        # Check if delimited sample size
        if sample_check == True:
            top_dates = sorted_df[:ss]
            return top_dates
        elif sample_check == False:
            return sorted_df
    elif sort_check == False and sort_date_check == False:
        # Check if delimited sample size
        if sample_check == True:
            first_dates = counted_list[:ss]
            return first_dates
        elif sample_check == False:
            return counted_list

        
'''
    whichPeriod: Helper function for grouper(). Isolates what period a date is in for use.
    - Args: 
        - period_dates= Dict of Lists per period
        - date= String. Date to lookup.
    - Returns String of period to grouper().
'''
def whichPeriod(period_dates, date):
    for p in period_dates:
        if date in period_dates[p]:
            return p
    return False

'''
    grouper: Takes default values in 'skeleton' Dict and hydrates them with sample List of Tuples
    - Args:
        - group_type= String. Current options include:
            - 'day': per Day
            - 'period_day': Days per Period
            - 'period': per Period
        - listed_tuples= List of Tuples from get_sample_size(). 
            - Example structure is the following: [(('keyword', '01-27-2019'), 100), (...), ...]
        - skeleton= Dict. Fully hydrated skeleton dict, wherein grouper() updates its default 0 Int values.
    - Returns Dict of updated values per keyword
'''
def grouper(**kwargs):
    print('\n\nHydrating skeleton with sample now ...')
    if kwargs['group_type'] == 'day':
        for g in kwargs['listed_tuples']:
            if g[0][1] in kwargs['skeleton']:
                kwargs['skeleton'][g[0][1]][g[0][0]] = g[1]
    elif kwargs['group_type'] == 'period_day':
        for g in kwargs['listed_tuples']:
            # Parse periods
            for p in kwargs['skeleton']:
                # If date in period, assign new keyword value
                if g[0][1] in kwargs['skeleton'][p]:
                    kwargs['skeleton'][p][g[0][1]][g[0][0]] = g[1]
    elif kwargs['group_type'] == 'period':
        for g in kwargs['listed_tuples']:
            # Parse periods and accrue totals for each hashtag
            for p in kwargs['skeleton']:
                # Accrue totals per period
                p_check = whichPeriod(kwargs['period_dates'], g[0][1]) #returns period of date
                if p_check is not False:
                    kwargs['skeleton'][p_check][g[0][0]] = g[1] + kwargs['skeleton'][p_check][g[0][0]]
                    
    return kwargs['skeleton']

'''
    grouped_dict_to_df: Takes grouped Dict and outputs a DataFrame.
    - Args:
        - main_sum_option= String. Options for grouping into a Dataframe.
            - group_hash_temporal= Multiple groups of hashtags
        - grouped_output_type= Sring. oPtions for DF outputs
            - spread= Good for small multiples in D3.js 
            - consolidated= Good for small multiples in matplot
        - time_agg_type= String. Options for type of temporal grouping.
            - period= Grouped by periods
        - group_dict= Hydrated Dict to convert to a DataFrame for visualization or output
    - Returns DataFrame for use with a plotter function or output as CSV
'''
def grouped_dict_to_df(**kwargs):
    if kwargs['main_sum_option'] == 'grouped_terms_perday' and kwargs['time_agg_type'] == 'period':
        
        if kwargs['grouped_output_type'] == 'consolidated':
            ph = []
            for p in kwargs['group_dict']:
                for ht in kwargs['group_dict'][p]:
                    ph.append([int(p), ht, kwargs['group_dict'][p][ht]])

            columns = ['period','term','count']
            df_return = pd.DataFrame(ph, columns=columns)
            
            return df_return
        elif kwargs['grouped_output_type'] == 'spread':
            period_col_values = []
            data = {'columns': {}}
            for p in kwargs['group_dict']:
                for ht in kwargs['group_dict'][p]:
                    # Append hashtag values
                    if ht not in data['columns']:
                        data['columns'].update({ht: [ kwargs['group_dict'][p][ht] ]})
                    elif ht in data['columns']:
                        data['columns'][ht].append(kwargs['group_dict'][p][ht])
                    # Append period
                    if int(p) not in period_col_values:
                        period_col_values.append(int(p))

            df_periods = pd.DataFrame({'period': period_col_values})
            df_hts = pd.DataFrame(data['columns'])
            df_return = df_periods.join(df_hts)
            
            return df_return

'''
    find_term: Helper function for accumulator(). Searches for hashtag in tweet.
        If there, return True. If not, return False.
        - Args:
            - search= String. Term to search for.
            - text= String. Text to search.
        - Returns Boolean
'''
def find_term(search, text):
    result = re.findall('\\b'+search+'\\b', text, flags=re.IGNORECASE)
    if len(result) > 0:
        print('Term:', search, '\n\nResult;', result)
        return True
    else:
        return False

'''
    accumulator: Helper function for summarizer function. Accumulates by simple lists and keyed lists.
    - Args:
        - checker= String. Options for accumulation:
            - simple: Takes values from simple_list and conducts a search on primary_col.
            - keyed: Takes values from keyed_list and conducts a search on secondary_col.
        - df_list= List. DataFrame passed as a list for traversing
        - check_list= List. List of terms to accrue and append
            - If simple, converted to List of each listed term.
            - If keyed, List of dicts, where each key is its accompanying primary_col term.
    - Returns a hydrated list of Tuples with each primary term and its accompanying date.
'''
def accumulator(checker, df_list, check_list):
    if checker == 'simple':
        print('Started accumulating content with simple listed terms.')
        terms_and_dates = []
        for h in df_list:
            ht = ast.literal_eval(h[1])
            if type(ht) is not float:
                ht = [n.strip() for n in ht]
                if len(ht) > 1:
                    for i in ht:
                        # Check if in check_list
                        if i in check_list:
                            # Append primary term and date
                            terms_and_dates.append( (i, h[0], int(float(h[2]))) )
                elif len(ht) == 1:
                    if ht[0] in check_list:
                        # Append primary term and date
                        terms_and_dates.append( (ht[0], h[0], int(float(h[2]))) )
        print('Accumulating content with simple listed terms complete.')
        return terms_and_dates
    elif checker == 'keyed':
        print('Started accumulating content with keyed terms.')
        keywords_and_dates = []
        # Traverse list of tweets, check for keywords
        for t in df_list:
            for ht in check_list:
                for kw in ht:
                    for k in ht[kw]:
                        # k = keyword in each check_list
                        # Search for it in a tweet
                        check_keyword = k in str(t[2])
                        # Filter out if simple_list term is used
                        if check_keyword == True:
                            check_ht = find_term( kw, str(t[2]) )
                            # If not found as simple_list term, append it
                            if check_ht == False:
                                keywords_and_dates.append( (kw, t[0], int(float(t[3])), k) )
        print('Accumulating content with keyed terms complete.')
        return keywords_and_dates

'''
    summarizer: Counts a column variable of interest and returns a sample data set
        based on set parameters. There are 5 search options from which to choose.
        See the the 'main_sum_option' list below.
    - Args:
        - Required Options:
            - main_sum_option= String. Current options for sampling include the following:
                - 'sum_all_col': Sum of all the passed variable across entire corpus
                - 'sum_group_col': Sum of a group of the passed variables (List) across entire corpus
                - 'sum_single_col': Sum of a single isolated variables value (String) across entire corpus
                - 'single_term_per_day': Sum of single variable per Day in provided range
                - 'grouped_terms_perday': Sum of group of a type of variable per Day in provided range
            - column_type= String. Provides the type of summary to conduct.
                - 'hashtags': Searches for hashtags
                - 'urls': Searches for URLs
                - 'other': Searches for another type of content
            - df_corpus= DataFrame of tweet corpus
            - primary_col= String. Name of the primary targeted DataFrame column of interest, 
                e.g., hashtags, urls, etc.
            - sort_check= Boolean. If True, sort sums per day.
            - sort_date_check= Boolean. If True, sort by dates.
            - sort_type= Boolean. If True, descending order. If False, ascending order.
        - Conditional options:
            - group_search_option= String. Use to choose what search options to use for 'group_col_per_day'. 
                - 'single_col': Searches for search terms in the single pertinent column
                - 'keywords_and_col': Searches for a column variable and accompanying
                    keywords in another content column, such as 'tweets'. For example,  you search for someone's 
                    name in the corpus that isn't always represented as a hashtag.
            - simple_list= List of terms to isolate.
            - keyed_list= List of Dicts. A keyed list of keywords of which you search within the secondary_col.
            - secondary_col= String. Name of the secondary targeted DataFrame column of interest, 
                if needed, e.g., tweets, usernames, etc.
            - single_term= String of single term to isolate.
            - time_agg_type= If sum by group temporally, define its temporal aggregation:
                - 'day': Aggregate time per Day
                - 'period': Aggregate time per period
            - date_col= String value of the DataFrame column name for the dates in xx-xx-xxxx format.
            - id_col= String value of the DataFrame column name for the unique ID.
            - grouped_output_type= String. Options for particular Dataframe output
                - consolidated= Each listed value in group is a column with its period values
                - spread= One column for each listed group value
    - Return: Depending on option, a sample as a List of Tuples or Dict of grouped samples
'''
def summarizer(**kwargs):
    cleaned_df_data = pd.DataFrame([])
    clean_data_filtered = pd.DataFrame([])
    
    # 1. Remove null values
    clean_data = kwargs['df_corpus'][(kwargs['df_corpus'][kwargs['primary_col']].isnull() == False)]
    
    # 2. Is it URLs or Hashtags
    print('Cleaning the data.')
    if kwargs['column_type'] == 'hashtags':
        clean_data_filtered = clean_data[clean_data[kwargs['primary_col']].str.contains('#')]
    
    elif kwargs['column_type'] == 'urls':
        clean_data_filtered = clean_data[clean_data[kwargs['primary_col']].str.contains('http')]
    
    elif kwargs['column_type'] == 'other':
        clean_data_filtered = clean_data.copy()
        
    cleaned_df_data = clean_data_filtered.reset_index()
    print('Data cleaned, now writing samples.')
    
    # 2. Count and sort; append to this list
    cleaned_listed_data = []
    
    # Option 2.1 - Count per Hashtag, across entire corpus
    if kwargs['main_sum_option'] == 'sum_all_col':
        print('Hydrating by desired', kwargs['sum_option'])
        for h in list(cleaned_df_data[kwargs['primary_col']]):
            h = ast.literal_eval(h)
            if type(h) is not float:
                h = [n.strip() for n in h]
                if len(h) > 1 and type(h) is not float:
                    for i in h:
                        cleaned_listed_data.append(i)
                elif len(h) == 1 and type(h) is not float:
                    cleaned_listed_data.append(h[0]) 
        
        # Count'em up
        col_totals = list(Counter(cleaned_listed_data).items())
        
        print('Writing up the sample')
        top_x = get_sample_size(
            sort_check=kwargs['sort_check'],
            sort_date_check=kwargs['sort_date_check'],
            sort_type=kwargs['sort_type'],
            counted_list=col_totals,
            ss=kwargs['sample_size'],
            sample_check=kwargs['sample_check']
        )
        return top_x
    # Option 2.2 - Count group of hashtags across entire corpus
    elif kwargs['main_sum_option'] == 'sum_group_col':
        print('Hydrating by desired', kwargs['sum_option'])
        for h in list(cleaned_df_data[kwargs['primary_col']]):
            h = ast.literal_eval(h)
            if type(h) is not float:
                h = [n.strip() for n in h]
                if len(h) > 1 and type(h) is not float:
                    for i in h:
                        if i in kwargs['simple_list']:
                            cleaned_listed_data.append(i)
                elif len(h) == 1 and type(h) is not float and h[0] in kwargs['simple_list']:
                    cleaned_listed_data.append(h[0]) 
        
        # Count'em up
        col_totals = list(Counter(cleaned_listed_data).items())
        
        print('Writing up the sample')
        top_x = get_sample_size(
            sort_check=kwargs['sort_check'],
            sort_date_check=kwargs['sort_date_check'],
            sort_type=kwargs['sort_type'],
            counted_list=col_totals,
            ss=kwargs['sample_size'],
            sample_check=kwargs['sample_check']
        )
        return top_x
    # Option 2.3 - Count single hashtag across entire corpus
    elif kwargs['main_sum_option'] == 'sum_single_col':
        print('Hydrating by desired', kwargs['sum_option'])
        for h in list(cleaned_df_data[kwargs['primary_col']]):
            h = ast.literal_eval(h)
            if type(h) is not float:
                h = [n.strip() for n in h]
                if len(h) > 1 and type(h) is not float:
                    for i in h:
                        if i == kwargs['single_term']:
                            cleaned_listed_data.append(i)
                elif len(h) == 1 and type(h) is not float and h[0] == kwargs['single_term']:
                    cleaned_listed_data.append(h[0]) 
        
        col_totals = list(Counter(cleaned_listed_data).items())
        
        print('Writing up the sample')
        top_x = get_sample_size(
            sort_check=kwargs['sort_check'],
            sort_date_check=kwargs['sort_date_check'],
            sort_type=kwargs['sort_type'],
            counted_list=col_totals,
            ss=kwargs['sample_size'],
            sample_check=kwargs['sample_check']
        )
        return top_x
    # Option 2.4 - Count a single isolated value temporally across entire corpus
    elif kwargs['main_sum_option'] == 'single_term_perday':
        # Isolate columns of interest: Dates (xx-xx-xxxx) and 
        df_primary_data = cleaned_df_data[[kwargs['date_col'], kwargs['primary_col'], [kwargs['id']]]]
        col_and_dates = []
        for h in df_primary_data.values.tolist():
            ht = ast.literal_eval(h[1])
            if type(ht) is not float:
                ht = [n.strip() for n in ht]
                if len(ht) > 1:
                    for i in ht:
                        # Check if equal to search parameter
                        if i == kwargs['single_term']:
                            # Append hashtag and date
                            col_and_dates.append( (i, h[0]) )
                elif len(ht) == 1 and ht[0] == kwargs['single_term']:
                    # Append hashtag and date
                    col_and_dates.append( (ht[0], h[0]) )
        
        col_totals = list(Counter(col_and_dates).items())

        print('Writing up the sample')
        top_date_x = get_sample_size(
            sort_check=kwargs['sort_check'],
            sort_date_check=kwargs['sort_date_check'],
            sort_type=kwargs['sort_type'],
            counted_list=col_totals,
            ss=kwargs['sample_size'],
            sample_check=kwargs['sample_check']
        )

        # Group sample per Day or per Period
        temporal_top_date_x = grouper(
            listed_tuples=top_date_x,
            group_type=kwargs['time_agg_type'],
            skeleton=kwargs['skeleton']
        )
        return temporal_top_date_x
    
    # Option 2.5 - Count grouping of variable values per Day across entire corpus
    elif kwargs['main_sum_option'] == 'grouped_terms_perday':
        print('Hydrating by desired', kwargs['main_sum_option'])
        col_and_dates = []
        terms_date_totals = []
        merged_terms_and_dates = []
        # Write Lists with desired search parameters info
        if kwargs['group_search_option'] == 'single_col':
            # If column has embedded listed values ONLY
            df_primary_data = cleaned_df_data[[kwargs['date_col'], kwargs['primary_col']]]
            for h in df_primary_data.values.tolist():
                # Code as a list
                ht = ast.literal_eval(h[1])
                if type(ht) is not float:
                    ht = [n.strip() for n in ht]
                    if len(ht) > 1:
                        for i in ht:
                            # Check if in simple_list
                            if i in kwargs['simple_list']:
                                # Append term and date
                                col_and_dates.append( (i, h[0]) )
                    elif len(ht) == 1:
                        if ht[0] in kwargs['simple_list']:
                            # Append term and date
                            col_and_dates.append( (ht[0], h[0]) )
                            
            terms_date_totals = list(Counter(col_and_dates).items())
            
        elif kwargs['group_search_option'] == 'keywords_and_col':
            # 1. Search and list primary column xref'd with the simple_list
            df_data = cleaned_df_data[[kwargs['date_col'], kwargs['primary_col'], kwargs['id_col']]]
            primary_dates_id = accumulator('simple', df_data.values.tolist(), kwargs['simple_list'])
            
            # 2. Search secondary_col with keyed_list; Also filters out content already accounted by the simple_list
            df_kw_data = kwargs['df_corpus'][ [kwargs['date_col'], kwargs['primary_col'], kwargs['secondary_col'], kwargs['id_col'] ]]
            secondary_dates_id = accumulator('keyed', df_kw_data.values.tolist(), kwargs['keyed_list'])
            
            # 3. Merge Lists and filter out unecessary items
            merged_list = primary_dates_id + secondary_dates_id
            for m in merged_list:
                merged_terms_and_dates.append((m[0], m[1]))
        
            terms_date_totals = list(Counter(merged_terms_and_dates).items())
        
        print('Writing up the sample')
        top_date_x = get_sample_size(
            counted_list=terms_date_totals,
            sort_check=kwargs['sort_check'],
            sort_date_check=kwargs['sort_date_check'],
            sort_type=kwargs['sort_type'],
            ss=kwargs['sample_size'],
            sample_check=kwargs['sample_check']
        )

        print('Grouping the sample based on the', kwargs['time_agg_type'], 'option.')
        
        grouped_top_date_x = {}
        if kwargs['time_agg_type'] == 'period':
            grouped_top_date_x = grouper(
                listed_tuples=top_date_x,
                group_type=kwargs['time_agg_type'],
                skeleton=kwargs['skeleton'],
                period_dates=kwargs['period_dates']
            )
        elif kwargs['time_agg_type'] == 'period_day':
            grouped_top_date_x = grouper(
                listed_tuples=top_date_x,
                group_type=kwargs['time_agg_type'],
                skeleton=kwargs['skeleton']
            )
                    
        print('\n\nConverting data to a DataFrame.')
        
        df_grouped_top_date_x = grouped_dict_to_df(
            main_sum_option=kwargs['main_sum_option'],
            time_agg_type=kwargs['time_agg_type'],
            group_dict=grouped_top_date_x,
            grouped_output_type=kwargs['grouped_output_type']
        )

        print('\n\nSample hydration complete!')
        return df_grouped_top_date_x

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
    # [(('#buildthewall', '2019-03-14'), 1),
        # (('#buildthewall', '2019-02-28'), 30),
        # (('#buildthewall', '2019-02-27'), 80), ... ]
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

'''
    multiline_plotter: Plots and saves a small-multiples line chart from a returned DataFrame from the summarizer function that used the 'spread' output option
    - Modified src: https://python-graph-gallery.com/125-small-multiples-for-line-chart/
    - Args:
        - style= String. See matplot docs for options available, e.g. 'seaborn-darkgrid' 
        - pallette= String. See matplot docs for options available, e.g. 'Set1'
        - graph_option= String. Options for sampling will include all of the the following, but for now only 'group_var_per_period':
            - 'single_var_per_day': Sum of single variable per Day in provided range
            - 'group_var_per_day': Sum of group of variable per Day in provided range
            - 'single_var_per_period': Sum of single variable per Period
            - 'group_var_per_period': Sum of group of variable per Period
        - df= DataFrame of data set to be visualized
        - x_col= DataFrame column for x-axis
        - multi_x= Integer for number of graphs along x/rows
        - multi_y= Integer for number of graphs along y/columns
            - NOTE: Only supports 3x3 right now.
        - linewidth= Float. Line width level.
        - alpha= Float (0-1). Opacity level of lines
        - chart_title= String. Title for the overall chart
        - x_title= String. Label for x axis
        - y_title= String. Label for y axis
        - path= String. Path to save figure
        - output= String. Filename for figure.
    - Returns nothing, but plots a 'small multiples' series of charts
'''
def multiline_plotter(**kwargs):
    if kwargs['graph_option'] == 'group_var_per_period':
        # Initialize the use of a stylesheet
        # See docs for options, e.g., 'dark_background'
        plt.style.use(kwargs['style'])

        # Create a color palette
        # See docs for options, e.g., 'Set1' or 'Paired'
        palette = plt.get_cmap(kwargs['palette'])

        # Create a figure and a grid of subplots
        fig, axs = plt.subplots(nrows=kwargs['multi_x'], ncols=kwargs['multi_y'])

        # counter will store the feature index 
        # to use when highlighting a particular 
        # variable in each subplot
        counter = 0

        # Traverse each individual subplot within the 3x3 grid
        # Note: This code subsets each subplot via axs[row, col]
        for row in range(axs.shape[0]):
            for col in range(axs.shape[1]):
                # Plot every feature in each subplot as a white line
                for feature in kwargs['df'].drop(kwargs['x_col'], axis=1).columns:
                    axs[row, col].plot(kwargs['df'][kwargs['x_col']],
                                   kwargs['df'][feature],
                                   marker="",
                                   color="white", 
                                   linewidth=0.6,
                                   alpha=0.3)
                # For each subplot, plot only one non-"period" feature 
                # via counter and in color
                # Note: counter is input directly inside of palette()
                axs[row, col].plot(kwargs['df'][kwargs['x_col']],
                                   kwargs['df'].drop(kwargs['x_col'], axis=1).iloc[:, counter],
                                   marker="",
                                   color=palette(counter), 
                                   linewidth=2.4,
                                   alpha=0.9)
                
                # Set xlim and ylim for each subplot
                # Define ranges based on data set values
                x_max = math.ceil(max(kwargs['df'].iloc[:, :1].copy().max().values.tolist()))
                x_min = math.floor(min(kwargs['df'].iloc[:, :1].copy().min().values.tolist()))
                y_max = math.ceil(max(kwargs['df'].iloc[:, 1:-1].copy().max().values.tolist()))
                y_min = math.floor(min(kwargs['df'].iloc[:, 1:-1].copy().min().values.tolist()))
                axs[row, col].set_xlim(x_min,x_max)
                axs[row, col].set_ylim(y_min,y_max)

                # Remove x-axis tick marks from the first two rows of subplots
                # TODO: Revise to be modular, based on grid definition besides 3x3
                if row in [0, 1]:
                    axs[row, col].tick_params(labelbottom=False)
                # Remove the y-axis tick marks from the second and third 
                # columns of subplots
                if col in [1, 2]:
                    axs[row, col].tick_params(labelleft=False)          

                # Assign each subplot a title based on the one non-"period" 
                # feature that was highlighted in color
                axs[row, col].set_title(kwargs['df'].drop(kwargs['x_col'], axis=1).iloc[:, counter].name, 
                                        loc="left", 
                                        fontsize=12, 
                                        fontweight=0, 
                                        color=palette(counter))

                # Subplot complete, so increment counter
                # so the next column variable is highlighted
                counter += 1

        # Assign overall title
        fig.suptitle(kwargs['chart_title'], 
                     fontsize=13, 
                     fontweight=0,
                     color="white", 
                     style="italic", 
                     y=1.02)

        # Label axes
        fig.text(0.5, 0.01, kwargs['x_title'], ha="center", va="center")
        fig.text(0.01, 0.5, kwargs['y_title'], ha="center", va="center", rotation='vertical')

        # Unsquish layout
        fig.tight_layout()

        # Export figure as PNG file
        fig.savefig(
            join(kwargs['path'], kwargs['output']),
            dpi=200,
            bbox_inches="tight")
        print('File ', kwargs['output'], ' saved to ', kwargs['path'])
        plt.show()
