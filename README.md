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

```narrator``` initializes and uses the following objects:

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
* ```period_maker```: Helper function for period_dates_writer.
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

* ```hashtag_summarizer```: Counts hashtag use: optionally as temporally distributed or as totals per hashtag. You can also specify sorting preferences.
    - Args:
        - df_corpus= DataFrame of tweet corpus
        - hash_col= String value of the DataFrame column name for hashtags.
        - date_col= String value of the DataFrame column name for the dates in xx-xx-xxxx format.
        - single_date_counter= Boolean. If True, build sums per day for single hashtag. If False, overall sum.
        - group_date_counter= Boolean. If True, build sums per day for grouping of hashtags.
        - sorted= Boolean. If True, sort sums per day. If False, maintain temporal order.
        - sort_type= Boolean. If True, descending order. If False, ascending order.
* ```get_sample_size```: Helper function for summarizer functions. If sample=True, then sample sent here and returned to the summarizer for output.
    - Args:
        - sort_check= Boolean. If True, sort the corpus. If False, leave in temporal order.
        - df= DataFrame of corpus.
        - ss= Integer of sample size to output.
        - sample_check= Boolean. If True, use ss value. If False, use full corpus.
    - Returns DataFrame to summarizer function.
* More to come

## Plotter Functions

* ```bar_plotter```: Plot the desired sum of your column sums as a bar chart
    - Args:
        - ax=None # Resets the chart
        - counter = List of tuples returned from match_maker(),
        - path = String of desired path to directory,
        - output = String value of desired file name (.png)
    - Returns: Nothing, but outputs a matplot figure in your Jupyter Notebook and .png file.
* More to come

## Distribution update terminal commands

<pre>
# Create new distribution of code for archiving
sudo python3 setup.py sdist bdist_wheel

# Distribute to Python Package Index
python3 -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
</pre>