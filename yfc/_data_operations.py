import csv
import os
import numpy as np
import pandas as pd
import requests

from ._decorators import timeit
from ._exceptions import Yahoo404Error


def read_api_dict():
    """Creates a dictionary of Yahoo Finance API parameters from a csv file.


    Arguments:
        takes no arguments
    File specs:
        csv with columns 'parameter, description'
    Returns:
        a dictionary consisting of parameters and their descriptions
    """
    api_dict_csv_path = os.path.join(os.path.dirname(__file__), 'yahoo_api_dict.csv')
    with open(api_dict_csv_path) as api:
        reader = csv.DictReader(api)
        api_dict = {row['parameter']: row['description'] for row in reader}

    return api_dict


def get_ticker_list_from_file(tickers_csv_path):
    """Creates a list of tickers from a csv file listing tickers one per line.

    Arguments:
        tickers_csv_path --> string containing path to tickers csv file
    File specs:
        csv with column 'ticker'
    Returns:
        a list of ticker strings
    """
    with open(tickers_csv_path) as tickers_file:
        reader = csv.DictReader(tickers_file)
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
def get_current_answer_string(ticker_string, param_string):
    """Queries Yahoo Finance API, returns a CSV string with the response.

    Arguments:
        ticker_string --> comma-separated string of tickers
        param_string --> comm-separated string of Yahoo API parameters
    Returns:
        response string, CSV formatted
    """
    base_url = 'http://finance.yahoo.com/d/quotes.csv'
    params = {'s': ticker_string, 'f': param_string}

    while True:
        try:
            response = requests.get(base_url, params)
        except requests.exceptions.ConnectionError:
            print 'Connection error, trying again...'
        else:
            answer_string = response.text
            return answer_string


def get_date_components(date_object):
    """Extracts components dates for a historical data request.

    Arguments:
        date_object --> string date, Python datetime, NumPy datetime64 or pandas Timestamp
    Returns:
        (m, d, y) --> month, day, year (integers)
    """
    # TODO implement datetime, datetime64 and Timestamp handling
    if type(date_object) == str:
        date_string = date_object
        y, m, d = [int(i) for i in date_string.split('-')]
        m -= 1  # Need to decrement, Yahoo has 0-indexing for months

        return m, d, y


@timeit
def get_historical_answer_string(ticker, from_date=None, to_date=None):

    base_url = 'http://real-chart.finance.yahoo.com/table.csv'

    params = {'s': ticker}
    if from_date is not None:
        params['a'], params['b'], params['c'] = get_date_components(from_date)
    if to_date is not None:
        params['d'], params['e'], params['f'] = get_date_components(to_date)

    while True:
        try:
            response = requests.get(base_url, params)
            if response.status_code == 404:
                raise Yahoo404Error('No historical data for ticker ' + params['s'])
        except requests.exceptions.ConnectionError:
            print 'Connection error, trying again...'
        except Yahoo404Error:
            return None
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

    if answer_string is None:
        return None
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


def current_pd_dataframe(api_dict, answer_list, param_list, ticker_list):
    """Constructs a pandas DataFrame from a data dictionary and cleans it.

    Arguments:
        api_dict --> dictionary containing Yahoo Finance API parameters and their definitions
        answer_list --> list of lists containing rows for future DataFrame
        param_list --> list of Yahoo Finance API parameters that were used to request data
        ticker_list --> list of tickers for which data was requested

    Returns:
        pandas_dataframe --> configuration: rows are companies, columns are parameter definitions
                             wrangling:
                                        - 'N/A's are replaced with NumPy NaNs
                                        - all-NaN columns are dropped
                                        - where possible, columns are converted to numeric
    """
    
    dict_for_pandas = {api_dict[param_list[index]]: item for index, item in enumerate(zip(*answer_list))}

    pandas_dataframe = pd.DataFrame(dict_for_pandas)
    pandas_dataframe.index = ticker_list
    pandas_dataframe = pandas_dataframe.replace(to_replace='N/A', value=np.nan)

    for item in pandas_dataframe:
        if pandas_dataframe[item].count() == 0:
            del pandas_dataframe[item]

    for colname in pandas_dataframe:
        try:
            pandas_dataframe[colname] = pd.to_numeric(pandas_dataframe[colname])
        except ValueError:
            print colname, 'could not be converted.'

    # TODO Convert columns to datetimes if possible
    # TODO Parse values with M, B for million/billion

    return pandas_dataframe


def historical_pd_dataframe(answer_list):

    if answer_list is None:
        return None

    columns, data = answer_list[0], answer_list[1:]

    dict_for_pandas = {columns[index]: item for index, item in enumerate(zip(*data))}

    pandas_dataframe = pd.DataFrame(dict_for_pandas)
    pandas_dataframe.index = pd.to_datetime(pandas_dataframe['Date'])
    pandas_dataframe = pandas_dataframe[columns]
    del pandas_dataframe['Date']

    for colname in pandas_dataframe:
        try:
            pandas_dataframe[colname] = pd.to_numeric(pandas_dataframe[colname])
        except ValueError:
            print colname, 'could not be converted.'

    return pandas_dataframe


def save_formatted_csv(result_csv_path, header_list, ticker_list, answer_list):
    """DEPRECATED: use write_to_csv option instead.
    Writes the data from the response list to a CSV file using csv.DictWriter.

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
