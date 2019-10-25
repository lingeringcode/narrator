# Narrator
by Chris Lindgren <chris.a.lindgren@gmail.com>
Distributed under the BSD 3-clause license. See LICENSE.txt or http://opensource.org/licenses/BSD-3-Clause for details.

## Overview

A set of functions that process and create descriptive summary visualizations to help develop a broader narrative through-line of one's tweet data.

It functions only with Python 3.x and is not backwards-compatible (although one could probably branch off a 2.x port with minimal effort).

**Warning**: ```narrator``` performs very little custom error-handling, so make sure your inputs are formatted properly! If you have questions, please let me know via email.

## System requirements

* ast
* matplot
* pandas
* numpy
* emoji
* re

## Installation
```pip install narrator```

## Objects

```narrator``` will initialize and use the following objects in future versions. It is currently not implemented yet. More to come here.

* ```topperObject```: Object class with attributes that store desired top X samples from the corpus Object properties as follows:
    - ```.top_x_hashtags```:
    - ```.top_x_tweeters```:
    - ```.top_x_tweets```:
    - ```.top_x_topics```:
    - ```.top_x_urls```:
    - ```.top_x_rts```:
    - ```.period_dates```:

## General Functions

```narrator``` contains the following general functions:

* ```initializeTO```: Initializes a topperObject().
* ```date_range_writer```: Takes beginning date and end date to write a range of those dates per Day as a List
    - Args:
        - bd= String. Beginning date in YYYY-MM-DD format
        - ed= String. Ending date in YYYY-MM-DD format
    - Returns List of arrow date objects for whatever needs.
* ```period_writer```:  Accepts list of lists of period date information and returns a Dict of per Period dates for temporal analyses.
    - Args:
        - periodObj: Optional first argument periodObject, Default is None
        - 'ranges': Hierarchical list in following structure:<pre>
                ranges = [
                    ['p1', ['2018-01-01', '2018-03-30']],
                    ['p2', ['2018-04-01', '2018-06-12']],
                    ...
                ]</pre>
    - Returns Dict of period dates per Day as Lists: <code>{ 'p1': ['2018-01-01', '2018-01-02', ...] }</code> 

## Summarizer Functions

* ```hashtag_summarizer```: Counts hashtag use and optionally as temporally
    distributed.
    - Args:
        - search_option: String. Either 'hashtags' or' tweets_and_hashtags'. The second 
            option searches for hashtags in the hashtag column and keywords in 
            the tweet column. For example, you search for someone's name in the 
            corpus that isn't always represented as a hashtag.
        - keyword_list= List. A list of keywords of which you search within the tweet column.
        - df_corpus= DataFrame of tweet corpus
        - hash_col= String value of the DataFrame column name for hashtags.
        - tweet_col= String value of the DataFrame column name for tweets.
        - sum_option= String. Current options for sampling include the following:
            - 'sum_all_hash': Sum of all hashtags across entire corpus
            - 'sum_group_hash': Sum of a group of hashtags (List) across entire corpus
            - 'sum_single_hash': Sum of a single hashtag (String) across entire corpus
            - 'single_hash_per_day': Sum of single hashtag per Day in provided range
            - 'group_hash_per_day': Sum of group of hashtags per Day in provided range
        - single_hash= String of single hashtag to isolate.
        - hash_list= List of hashtags to isolate.
        - time_agg_type= If sum by group temporally, define its temporal aggregation:
            - 'day': Aggregate time per Day
            - 'period': Aggregate time per period
        - date_col= String value of the DataFrame column name for the dates in xx-xx-xxxx format.
        - sort_check= Boolean. If True, sort sums per day.
        - sort_date_check= Boolean. If True, sort by dates.
        - sort_type= Boolean. If True, descending order. If False, ascending order.
        - output_type= String. OPtions for particular Dataframe output
            - d3js= DF in a format conduive for small multiples chart in D3.js
            - python= DF in a format conduive for small multiples chart in python's matplot
    - Return: Depending on option, a sample as a List of Tuples or Dict of grouped samples
* ```get_sample_size```: Helper function for summarizer functions. If sample=True,
    then sample sent here and returned to the summarizer for output.
    - Args:
        - sort_check= Boolean. If True, sort the corpus.
        - sort_date_check= Boolean. If True, sort corpus based on dates.
        - df= DataFrame of corpus.
        - ss= Integer of sample size to output.
        - sample_check= Boolean. If True, use ss value. If False, use full corpus.
    - Returns DataFrame to summarizer function.
* ```grouper```: Takes default values in 'skeleton' Dict and hydrates them with sample List of Tuples
    - Args:
        - group_type= String. Current options include 'day' or 'period'
        - listed_tuples= List of Tuples from get_sample_size(). 
            - Example structure is the following: ```[(('keyword', '01-27-2019'), 100), (...), ...]```
        - skeleton= Dict. Fully hydrated skeleton dict, wherein grouper() updates its default 0 Int values.
    - Returns Dict of updated values per keyword
* ```skeletor```: Takes desired date range and list of keys to create a skeleton Dict before hydrating it with the sample values. Overall, this provides default 0 Int values for every keyword in the sample.
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
* ```whichPeriod```: Helper function for grouper(). Isolates what period a date is in for use.
    - Args: 
        - period_dates= Dict of Lists per period
        - date= String. Date to lookup.
    - Returns String of period to grouper().
* ```find_term```: Helper function for accumulator(). Searches for hashtag in tweet. If there, return True. If not, return False.
        - Args:
            - search= String. Term to search for.
            - text= String. Text to search.
        - Returns Boolean
* ```grouped_dict_to_df```: Takes grouped Dict and outputs a DataFrame.
    - Args:
        - sum_option= String. Options for grouping into a Dataframe.
            - group_hash_temporal= Multiple groups of hashtags
        - output_type= Sring. oPtions for DF outputs
            - d3js= Good for small multiples in D3.js 
            - python= Good for small multiples in matplot
        - time_agg_type= String. Options for type of temporal grouping.
            - period= Grouped by periods
        - group_dict= Hydrated Dict to convert to a DataFrame for visualization or output
    - Returns DataFrame for use with a plotter function or output as CSV
* ```accumulator```: Helper function for summarizer functions. Accumulates by hashtag lists and keyword lists.
    - Args:
        - checker= String. Options for accumulation:
            - hashtags: Hashtag search.
            - keywords: Keyword search.
        - df_list= List. DataFrame passed as a list for traversing
        - check_list= List. List of terms to accrue and append
            - If hashtags, converted to List of hashtags
            - If keywords, List of dicts, where each key is its accompanying hashtag.
    - Returns a hydrated list of Tuples with hashtags and accompanying date.

## Plotter Functions

* ```bar_plotter```: Plot the desired sum of your column sums as a bar chart
    - Args:
        - ax=None # Resets the chart
        - counter = List of tuples returned from match_maker(),
        - path = String of desired path to directory,
        - output = String value of desired file name (.png)
    - Returns: Nothing, but outputs a matplot figure in your Jupyter Notebook and .png file.
* ```multiline_plotter```: Plots and saves a small-multiples line chart from a returned DataFrame from a summarizer function that used the 
    - Args:
        - style= String. See matplot docs for options available, e.g. 'seaborn-darkgrid' 
        - pallette= String. See matplot docs for options available, e.g. 'Set1'
        - graph_option= String. Current options for sampling include the following:
            - 'single_hash_per_day': Sum of single hashtag per Day in provided range
            - 'group_hash_per_day': Sum of group of hashtags per Day in provided range
            - 'single_hash_per_period': Sum of single hashtag per Period
            - 'group_hash_per_period': Sum of group of hashtags per Period
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

## Example Uses

### Create a Dictionary of period dates

```python
ranges = [
    ('1', ['2018-01-01', '2018-03-30']),
    ('2', ['2018-04-01', '2018-06-12']),
    ('3', ['2018-06-13', '2018-07-28']),
    ('4', ['2018-07-29', '2018-10-17']),
    ('5', ['2018-10-18', '2018-11-24']),
    ('6', ['2018-11-25', '2018-12-10']),
    ('7', ['2018-12-11', '2018-12-19']),
    ('8', ['2018-12-20', '2018-12-25']),
    ('9', ['2018-12-26', '2019-02-13']),
    ('10', ['2019-02-14', '2019-02-28'])
]

period_dates = narrator.period_dates_writer(ranges=ranges)
period_dates['1'][:5]

## Output ##
['2018-01-01', '2018-01-02', '2018-01-03', '2018-01-04', '2018-01-05']
```

### Use the ```hashtag_summarizer``` to generate multiple types of summary outputs

The below examples takes a group of hashtags, searches for them based on the period dates, then outputsthese groupings in descending order. In this case, it can also use a keyword list and hashtag list as 2 forms of input to inform the search across the corpus.

```python
liberal_keyword_list = [ 
    {
        '#felipegomez': ['felipe alonzo-gomez', 'felipe gomez']
    },
    {
        '#maquin': ['jakelin caal', 'maquín', 'maquin' ]
    }
]
liberal_hashtag_list = [
    '#familyseparation', '#familiesbelongtogether',
    '#felipegomez', '#keepfamiliestogether',
    '#maquin', '#noborderwall', '#shutdownstories',
    '#trumpshutdown', '#wherearethechildren'
]

arrow_date_range = narrator.date_range_writer('2018-01-01', '2019-02-28')
range_list = []
for d in arrow_date_range:
    # Append returned date range to period list
    range_list.append( str(d.format('YYYY-MM-DD')) )

dict_group_skel = narrator.skeletor(
    aggregate_level='period',
    date_range=period_dates,
    keys=liberal_hashtag_list
)

ht_df_sum = narrator.hashtag_summarizer(
    search_option='tweets_and_hashtags',
    keyword_list=liberal_keyword_list,
    tweet_col='tweet',
    id_col='id',
    df_corpus=df_all,
    hash_col='hashtags',
    date_col='date',
    sum_option='group_hash_temporal',
    hash_list=liberal_hashtag_list,
    skeleton=dict_group_skel,
    time_agg_type='period',
    period_dates=period_dates,
    sort_check=False,
    sort_date_check=True,
    sort_type=False, #Ascending (F) or descending (T)?
    sample_check=False,
    sample_size=None,
    output_type='python' #d3js or python
)
ht_df_sum
```

Output from above code:
<img src="https://raw.githubusercontent.com/lingeringcode/narrator/master/assets/images/output_summarizer_mult_grouping.png" />

### Plot a "Small Multiples" Line Chart

```python
narrator.multiline_plotter(
    style='dark_background',
    palette='Paired',
    graph_option='group_hash_per_period',
    df=ht_df_sum,
    x_col='period',
    multi_x=3,
    multi_y=3,
    linewidth=1.9,
    alpha=0.9,
    chart_title='Liberal hashtag sums per period',
    x_title='Periods',
    y_title='# of Hashtags',
    path='figures',
    output='test_multi.png'
)
```
Output:
<img src="https://raw.githubusercontent.com/lingeringcode/narrator/master/assets/images/matplot_small_multiples.png" />

I've also created a D3.js version:

<img src="https://raw.githubusercontent.com/lingeringcode/narrator/master/assets/images/d3_small_multiples.png" />


## Distribution update terminal commands

<pre>
# Create new distribution of code for archiving
sudo python3 setup.py sdist bdist_wheel

# Distribute to Python Package Index
python3 -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
</pre>