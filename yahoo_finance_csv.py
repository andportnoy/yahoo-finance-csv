import sys
import csv
import requests
from datetime import datetime
import pandas as pd
import numpy as np


def timeit(func):
    """Timing decorator, prints out function name and execution time."""
    def timed(*args, **kwargs):
        start = datetime.now()
        result = func(*args, **kwargs)
        finish = datetime.now()
        diff = finish - start
        print '\n', func.__name__, 'call took', diff.total_seconds(), 'seconds.\n'
        return result
    return timed


def get_api_dict_from_file(api_dict_csv_path):
    """Creates a dictionary of Yahoo Finance API parameters from a csv file.


    Arguments:
        api_dict_csv_path --> string containing path to API dictionary file
    File specs:
        csv with columns 'parameter, description'
    Returns:
        a dictionary consisting of parameters and their descriptions
    """
    with open(api_dict_csv_path) as api:
        reader = csv.DictReader(api)
        return {row['parameter']: row['description'] for row in reader}


def get_ticker_list_from_file(tickers_csv_path):
    """Creates a list of tickers from a csv file listing tickers one per line.
    
    Arguments:
        tickers_csv_path --> string containing path to tickers csv file
    File specs:
        csv with column 'ticker'
    Returns:
        a list of ticker strings
    """
    with open(tickers_csv_path) as tickers:
        reader = csv.DictReader(tickers)
        return [row['ticker'] for row in reader]


def get_ticker_string_from_list(ticker_list):
    """Returns a string of tickers separated by commas joined from a list."""

    ticker_string = ','.join(ticker_list)
    return ticker_string


def get_param_list_from_api_dict(api_dict):
    """Returns the keys of the API dictionary."""
    return api_dict.keys()


def get_param_string_from_list(param_list):
    """Returns a string of parameters with no separators joined from a list."""
    return ''.join(param_list)


@timeit
def get_answer_string(ticker_string, param_string):
    """Queries Yahoo Finance API, returns a CSV string with the response.
    
    Arguments:
        ticker_string --> comma-separated string of tickers
        param_string --> comm-separated string of Yahoo API parameters
    Returns:
        response string, CSV formatted
    """
    url = 'http://finance.yahoo.com/d/quotes.csv?s=' + ticker_string + '&f=' + param_string
    while True:
        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError:
            print 'Connection error, trying again...'
        else:
            answer_string = response.text
            return answer_string


def get_header_list(param_list, api_dict):
    """Creates a header for a CSV data file.
    
    Arguments:
        param_list --> list of Yahoo Finance API parameters formed by comma-splitting param_string
        api_dict --> dictionary with Yahoo Finance API parameter descriptions mapped to parameters
    Returns:
        list of parameter descriptions retrieved from the API dictionary.
    """
    return [api_dict[param] for param in param_list]


def get_answer_list_from_string(answer_string):
    """Creates a list from the response string.
    
    Arguments:
        answer_string --> text content of Yahoo Finance API request response
    Returns:
        list generated from the string by comma-splitting
    """
    csv_rows_list = answer_string.splitlines()
    reader = csv.reader(csv_rows_list)
    answer_list = list(reader)
    return answer_list


def save_raw_answer_to_file(answer_path, answer_string):
    """Saves the response string to a specified path.
    
    Arguments:
        answer_path --> path to target
        answer_string --> text content of Yahoo Finance API request response
    Returns:
        nothing
    """
    with open(answer_path, 'wb') as raw_data:
        raw_data.write(answer_string)
    print 'Raw response csv file saved to ' + answer_path


def construct_row(k, header_list, answer_list):
    """Creates a row of data for a CSV file (to be used with csv.DictWriter).
    
    Arguments:
        k --> position of observation sublist on the response list
        header_list --> list of parameter names except 'ticker'
        answer_list --> list formed by comma-splitting answer_string
    Returns:
        row of data in form of a dictionary
    """
    return {header_list[i]: answer_list[k][i] for i in xrange(len(header_list))}


def save_formatted_csv(result_csv_path, header_list, ticker_list, answer_list):
    """Writes the data from the response list to a CSV file using csv.DictWriter.
    
    Arguments:
        result_csv_path -- > path to target csv file (existing file will be overwritten)
        header_list --> list of parameter descriptions
        ticker_list --> list of tickers for which data is to be retrieved
        answer_list --> list formed by comma-splitting answer_string
    Returns:
        nothing
    """
    with open(result_csv_path, 'wb') as data:
        fieldnames = ['ticker'] + header_list
        writer = csv.DictWriter(data, fieldnames, quoting=csv.QUOTE_NONE, escapechar='\b')
        writer.writeheader()
        for k in range(len(ticker_list)):
            row = construct_row(k, header_list, answer_list)
            row['ticker'] = ticker_list[k]
            writer.writerow(row)


@timeit
def current(tickers, write_to_csv=False, result_csv_path=None, api_dict_csv_path='yahoo_api_dict.csv'):
    """Wrapper function, performs data retrieval/storage using other functions.
    
    Arguments:
        ticker_csv_path --> path to ticker csv file
        write_to_csv --> boolean, retrieve writes data to a csv file if set to True, returns a pandas dataframe
                         if set to False (default)
        result_csv_path --> string, specifies path to csv file to write the data (overwrites the file)
        api_dict_csv_path --> string, specifies path to csv file giving descriptions to Yahoo Finance parameters

    Returns:
        a pandas dataframe or None (if write_to_csv is set to False)
    """

    # create parameter string for the request
    api_dict = get_api_dict_from_file(api_dict_csv_path)
    param_list = get_param_list_from_api_dict(api_dict)
    param_string = get_param_string_from_list(param_list)

    # create ticker string for the request
    if type(tickers) == str:
        try:
            ticker_list = sorted(get_ticker_list_from_file(tickers))
        except Exception:
            sys.exit('File not found. Provide either a proper csv file or a list of tickers.')
        else:
            ticker_string = get_ticker_string_from_list(ticker_list)

    elif type(tickers) == list:
        ticker_list = tickers
        try:
            ticker_string = get_ticker_string_from_list(ticker_list)
        except Exception:
            print Exception
    else:
        raise Exception('Please provide either a csv file or a list of tickers.')

    # make request and transform it into a list
    answer_string = get_answer_string(ticker_string, param_string)
    answer_list = get_answer_list_from_string(answer_string)

    # lookup the parameter definitions and create a dictionary to be transformed into a pandas DataFrame
    dict_for_pandas = {api_dict[param_list[index]]: item for index, item in enumerate(zip(*answer_list))}
    pandas_dataframe = pd.DataFrame(dict_for_pandas)
    pandas_dataframe.index = ticker_list
    pandas_dataframe = pandas_dataframe.replace(to_replace='N/A', value=np.nan)

    # Drop columns that consist of NaN's only
    for item in pandas_dataframe:
        if pandas_dataframe[item].count() == 0:
            del pandas_dataframe[item]

    # Convert columns to numeric if possible, handle exception and print column name otherwise
    for colname in pandas_dataframe:
        try:
            pandas_dataframe[colname] = pd.to_numeric(pandas_dataframe[colname])
        except ValueError:
            print colname, 'could not be converted.'

    # TODO Convert columns to datetimes if possible
    # TODO Parse values with M, B for million/billion
    
    if write_to_csv:
        pandas_dataframe.to_csv(result_csv_path)

    return pandas_dataframe
